from collections import OrderedDict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import monotonic
from typing import Deque, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.result_sharing import (
    build_shared_result_snapshot,
    hash_capability_token,
    new_share_seed,
    share_token_from_seed,
    verify_owner_token,
)
from app.db.session import get_db
from app.models import ResultShare, TestRun
from app.schemas.share import (
    CreateResultShareRequest,
    CreateResultShareResponse,
    SharedJourneyResultResponse,
)

router = APIRouter()
_rate_buckets: "OrderedDict[str, Deque[float]]" = OrderedDict()
_rate_lock = Lock()
_MAX_RATE_LIMIT_KEYS = 5000


def _rate_limit(request: Request, *, scope: str, limit: int, window_seconds: int) -> None:
    client_ip = request.headers.get("fly-client-ip") or (
        request.client.host if request.client else "unknown"
    )
    bucket_key = f"{scope}:{client_ip}"
    now = monotonic()
    cutoff = now - window_seconds
    with _rate_lock:
        bucket = _rate_buckets.get(bucket_key)
        if bucket is None:
            while len(_rate_buckets) >= _MAX_RATE_LIMIT_KEYS:
                _rate_buckets.popitem(last=False)
            bucket = deque()
            _rate_buckets[bucket_key] = bucket
        else:
            _rate_buckets.move_to_end(bucket_key)
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        bucket.append(now)


def _limit_share_creation(request: Request) -> None:
    _rate_limit(request, scope="create", limit=10, window_seconds=60 * 60)


def _limit_share_reads(request: Request) -> None:
    _rate_limit(request, scope="read", limit=120, window_seconds=60 * 60)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _share_response(row: ResultShare) -> CreateResultShareResponse:
    token = share_token_from_seed(row.token_seed)
    if row.token_hash != hash_capability_token(token):
        raise HTTPException(status_code=500, detail="Share record is invalid")
    return CreateResultShareResponse(token=token, expires_at=_aware(row.expires_at))


def _cleanup_expired_shares(db: Session, now: datetime) -> int:
    deleted = (
        db.query(ResultShare)
        .filter(ResultShare.expires_at <= now)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted


@router.post(
    "/journey/shares",
    response_model=CreateResultShareResponse,
    dependencies=[Depends(_limit_share_creation)],
)
def create_result_share(
    payload: CreateResultShareRequest,
    x_result_owner_token: Optional[str] = Header(default=None, alias="X-Result-Owner-Token"),
    db: Session = Depends(get_db),
):
    test_run = db.query(TestRun).filter(TestRun.id == payload.test_run_id).first()
    if not test_run or not x_result_owner_token or not verify_owner_token(test_run, x_result_owner_token):
        raise HTTPException(status_code=404, detail="Journey not found")
    if test_run.status != "completed" or not test_run.submitted_at:
        raise HTTPException(status_code=400, detail="Journey is not completed")
    if not test_run.selected_activation_id:
        raise HTTPException(status_code=400, detail="Select an activation before sharing")

    now = datetime.now(timezone.utc)
    _cleanup_expired_shares(db, now)
    row = (
        db.query(ResultShare)
        .filter(
            ResultShare.test_run_id == test_run.id,
            ResultShare.language == payload.language,
        )
        .with_for_update()
        .first()
    )
    if row and _aware(row.expires_at) > now:
        return _share_response(row)

    snapshot = build_shared_result_snapshot(db, test_run=test_run, language=payload.language)
    seed = new_share_seed()
    token = share_token_from_seed(seed)
    expires_at = now + timedelta(days=settings.RESULT_SHARE_TTL_DAYS)
    snapshot_data = snapshot.model_dump(mode="json")

    if row:
        row.token_seed = seed
        row.token_hash = hash_capability_token(token)
        row.snapshot_jsonb = snapshot_data
        row.expires_at = expires_at
        row.created_at = now
    else:
        row = ResultShare(
            test_run_id=test_run.id,
            token_seed=seed,
            token_hash=hash_capability_token(token),
            language=payload.language,
            snapshot_jsonb=snapshot_data,
            expires_at=expires_at,
            created_at=now,
        )
        db.add(row)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        row = (
            db.query(ResultShare)
            .filter(
                ResultShare.test_run_id == test_run.id,
                ResultShare.language == payload.language,
                ResultShare.expires_at > now,
            )
            .first()
        )
        if not row:
            raise HTTPException(status_code=409, detail="Could not create share link")
    db.refresh(row)
    return _share_response(row)


@router.get(
    "/shares/report",
    response_model=SharedJourneyResultResponse,
    dependencies=[Depends(_limit_share_reads)],
)
def get_shared_result(
    response: Response,
    x_result_share_token: Optional[str] = Header(default=None, alias="X-Result-Share-Token"),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    if not x_result_share_token or len(x_result_share_token) > 256:
        raise HTTPException(status_code=404, detail="Shared result not found")

    row = (
        db.query(ResultShare)
        .filter(ResultShare.token_hash == hash_capability_token(x_result_share_token))
        .first()
    )
    if not row or _aware(row.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Shared result not found")
    return SharedJourneyResultResponse.model_validate(row.snapshot_jsonb)
