#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models import TestRun


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete stale non-completed journey runs."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Delete runs older than this many days (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many rows would be deleted without deleting anything.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    db = SessionLocal()

    try:
        stale_runs = db.query(TestRun).filter(
            TestRun.status != "completed",
            TestRun.created_at < cutoff,
        )
        delete_count = stale_runs.count()

        if args.dry_run:
            print(f"[DRY RUN] stale test_runs to delete: {delete_count}")
            return

        stale_runs.delete(synchronize_session=False)
        db.commit()
        print(f"Deleted stale test_runs: {delete_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
