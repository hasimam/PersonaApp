"""Server-owned scoring and progression for the three-practice private slice."""
import copy
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Dict, Optional, Literal
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.mother import MotherContentRelease, MotherJourney, MotherAssessment, MotherCheckin

router = APIRouter()


def now():
    return datetime.now(timezone.utc)


def owned(db, journey_id, token):
    # Serialize writes and reads that materialize a newly available daily card.
    journey = db.query(MotherJourney).filter_by(id=journey_id).with_for_update().first()
    candidate = hashlib.sha256((token or '').encode()).hexdigest()
    if not journey or not secrets.compare_digest(journey.owner_token_hash, candidate):
        raise HTTPException(404, 'Journey not found')
    return journey


def content_for(db, journey):
    return db.get(MotherContentRelease, journey.content_release_id).content


def display_content(content):
    result = copy.deepcopy(content)
    result.pop('scoring', None)
    for situation in result['situations']:
        for option in situation['options']:
            option.pop('weight', None)
    return result


def score(content, answers):
    areas = []
    for area in content['areas']:
        evidence = []
        for s in content['situations']:
            if s['area'] == area['code']:
                for o in s['options']:
                    if answers.get(s['id']) == o['id']:
                        evidence.append({'situation_id': s['id'], 'option_id': o['id'], 'weight': o['weight']})
        average = sum(e['weight'] for e in evidence) / len(evidence) if len(evidence) >= content['scoring']['minimum_answers'] else None
        band = ('insufficient' if average is None else 'strong' if average >= content['scoring']['strong_min'] else 'mixed' if average >= content['scoring']['mixed_min'] else 'growth')
        evidence.sort(key=lambda e: e['weight'], reverse=band == 'strong')
        areas.append({'code': area['code'], 'band': band, 'average': average, 'evidence': evidence})
    valid = [a for a in areas if a['average'] is not None]
    low = min((a['average'] for a in valid), default=None)
    recommended = [a['code'] for a in valid if a['average'] == low]
    strengths = [a['code'] for a in valid if a['band'] == 'strong']
    # Return examples, never numeric mother scores or internal weights.
    for area in areas:
        area.pop('average')
        for e in area['evidence']:
            e.pop('weight')
    return {'areas': areas, 'recommended': recommended, 'strengths': strengths,
            'all_strong': bool(valid) and all(a['band'] == 'strong' for a in valid)}


def state(db, journey):
    content = content_for(db, journey)
    assessment = db.query(MotherAssessment).filter_by(journey_id=journey.id, kind='baseline').one()
    checkins = db.query(MotherCheckin).filter_by(journey_id=journey.id).order_by(MotherCheckin.day_number).all()
    if journey.status == 'practice' and journey.next_available_at and now() >= journey.next_available_at:
        # Clock opens the next card, but never skips pending participation days.
        journey.next_available_at = None
        journey.updated_at = now()
        db.flush()
    available = journey.status == 'practice' and journey.next_available_at is None
    response = {'id': journey.id, 'status': journey.status, 'current_day': journey.current_day,
                'timezone': journey.timezone, 'focus_code': journey.focus_code,
                'next_available_at': journey.next_available_at,
                'content': display_content(content), 'answers': assessment.answers,
                'result': assessment.result, 'practice': content['practices'][journey.current_day - 1] if available else None,
                'checkins': [{'day': c.day_number, 'outcome': c.outcome, 'repeat_requested': c.repeat_requested} for c in checkins]}
    db.commit()
    return response


class Start(BaseModel):
    age_band: Literal['6-12'] = '6-12'
    timezone: str = Field(default='UTC', max_length=80)


class AssessmentInput(BaseModel):
    answers: Dict[str, Optional[str]] = Field(max_length=12)
    submit: bool = False


class FocusInput(BaseModel):
    focus_code: str


class CheckinInput(BaseModel):
    outcome: Literal['easy', 'difficult', 'not_yet', 'no_opportunity']
    repeat_requested: bool = False


@router.post('/journeys')
def start(payload: Start, db: Session = Depends(get_db)):
    try:
        ZoneInfo(payload.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(422, 'Unknown timezone')
    release = db.query(MotherContentRelease).filter_by(status='preview').order_by(MotherContentRelease.published_at.desc(), MotherContentRelease.version.desc()).first()
    if not release:
        raise HTTPException(503, 'Preview content not installed')
    token = secrets.token_urlsafe(32)
    journey = MotherJourney(content_release_id=release.id, owner_token_hash=hashlib.sha256(token.encode()).hexdigest(), timezone=payload.timezone, age_band=payload.age_band)
    db.add(journey)
    db.flush()
    db.add(MotherAssessment(journey_id=journey.id, kind='baseline', answers={}))
    db.flush()
    return {**state(db, journey), 'owner_token': token}


@router.get('/journeys/{journey_id}')
def resume(journey_id: str, db: Session = Depends(get_db), x_mother_owner_token: Optional[str] = Header(None)):
    return state(db, owned(db, journey_id, x_mother_owner_token))


@router.put('/journeys/{journey_id}/assessments/{kind}')
def assessment(journey_id: str, kind: str, payload: AssessmentInput, db: Session = Depends(get_db), x_mother_owner_token: Optional[str] = Header(None)):
    journey = owned(db, journey_id, x_mother_owner_token)
    if kind != 'baseline':
        raise HTTPException(409, 'Review is outside this three-practice preview')
    row = db.query(MotherAssessment).filter_by(journey_id=journey.id, kind=kind).one()
    if journey.status != 'baseline':
        if payload.submit and row.answers == payload.answers:
            return state(db, journey)
        raise HTTPException(409, 'Assessment already submitted')
    content = content_for(db, journey)
    allowed = {s['id']: {o['id'] for o in s['options']} for s in content['situations']}
    if any(k not in allowed or (v is not None and v not in allowed[k]) for k, v in payload.answers.items()):
        raise HTTPException(422, 'Unknown situation or option')
    if payload.submit and set(payload.answers) != set(allowed):
        raise HTTPException(422, 'Answer or explicitly skip every situation')
    row.answers = payload.answers
    journey.updated_at = now()
    if payload.submit:
        row.result = score(content, row.answers)
        row.submitted_at = now()
        journey.status = 'focus'
    db.flush()
    return state(db, journey)


@router.put('/journeys/{journey_id}/focus')
def focus(journey_id: str, payload: FocusInput, db: Session = Depends(get_db), x_mother_owner_token: Optional[str] = Header(None)):
    journey = owned(db, journey_id, x_mother_owner_token)
    if journey.status != 'focus':
        if journey.focus_code == payload.focus_code:
            return state(db, journey)
        raise HTTPException(409, 'Focus is already confirmed')
    if payload.focus_code not in {a['code'] for a in content_for(db, journey)['areas']}:
        raise HTTPException(422, 'Unknown focus')
    journey.focus_code = payload.focus_code
    journey.status = 'practice'
    journey.updated_at = now()
    return state(db, journey)


@router.put('/journeys/{journey_id}/checkins/{day}')
def checkin(journey_id: str, day: int, payload: CheckinInput, db: Session = Depends(get_db), x_mother_owner_token: Optional[str] = Header(None)):
    journey = owned(db, journey_id, x_mother_owner_token)
    existing = db.query(MotherCheckin).filter_by(journey_id=journey.id, day_number=day).first()
    if existing and existing.outcome == payload.outcome and existing.repeat_requested == payload.repeat_requested:
        return state(db, journey)
    if journey.status != 'practice' or day != journey.current_day or (journey.next_available_at and now() < journey.next_available_at):
        raise HTTPException(409, 'This practice is not available')
    if not existing:
        existing = MotherCheckin(journey_id=journey.id, day_number=day)
        db.add(existing)
    existing.outcome = payload.outcome
    existing.repeat_requested = payload.repeat_requested
    journey.updated_at = now()
    if payload.outcome != 'not_yet' and not payload.repeat_requested:
        if day == len(content_for(db, journey)['practices']):
            journey.status = 'preview_complete'
            journey.completed_at = now()
            journey.next_available_at = None
        else:
            journey.current_day += 1
            local = now().astimezone(ZoneInfo(journey.timezone))
            tomorrow = local.date() + timedelta(days=1)
            journey.next_available_at = datetime.combine(tomorrow, datetime.min.time(), tzinfo=ZoneInfo(journey.timezone)).astimezone(timezone.utc)
    db.flush()
    return state(db, journey)


@router.delete('/journeys/{journey_id}', status_code=204)
def delete(journey_id: str, db: Session = Depends(get_db), x_mother_owner_token: Optional[str] = Header(None)):
    journey = owned(db, journey_id, x_mother_owner_token)
    db.delete(journey)
    db.commit()
