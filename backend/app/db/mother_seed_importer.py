"""Validate editable bilingual content; activated preview releases remain draft editorially."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel, Field, StrictInt
from typing import Dict, List, Literal
from app.db.session import SessionLocal
from app.models.mother import MotherContentRelease


class Bilingual(BaseModel):
    en: str = Field(min_length=1)
    ar: str = Field(min_length=1)


class Area(BaseModel):
    code: str
    title: Bilingual
    descriptions: Dict[str, Bilingual]


class Option(BaseModel):
    id: str
    text: Bilingual
    weight: StrictInt = Field(ge=0, le=2)


class Situation(BaseModel):
    id: str
    area: str
    text: Bilingual
    options: List[Option]


class Practice(BaseModel):
    day: int
    area: str
    title: Bilingual
    value: Bilingual
    action: Bilingual
    words: Bilingual
    smaller: Bilingual


class Scoring(BaseModel):
    mixed_min: float = Field(ge=0, le=2)
    strong_min: float = Field(ge=0, le=2)
    minimum_answers: Literal[2]


class Content(BaseModel):
    version: str = Field(min_length=1, max_length=80)
    preview: bool
    editorial_status: Literal['draft', 'reviewed']
    age_band: Literal['6-12']
    scoring: Scoring
    areas: List[Area]
    situations: List[Situation]
    review_anchors: List[str]
    practices: List[Practice]


def validate_content(raw):
    content = Content.model_validate(raw).model_dump()
    codes = {a['code'] for a in content['areas']}
    if len(content['areas']) != 4 or codes != {'regulation', 'connection', 'boundaries', 'example'}:
        raise ValueError('Exactly the four supported areas are required')
    for area in content['areas']:
        if set(area['descriptions']) != {'strong', 'mixed', 'growth'}:
            raise ValueError('Every area needs all three result bands')
    situations = content['situations']
    ids = {s['id'] for s in situations}
    if len(situations) != 12 or len(ids) != 12:
        raise ValueError('Twelve unique situations required')
    for code in codes:
        if sum(s['area'] == code for s in situations) != 3:
            raise ValueError('Three situations per area required')
    for s in situations:
        if len(s['options']) != 4 or len({o['id'] for o in s['options']}) != 4:
            raise ValueError('Four unique options required')
    anchors = content['review_anchors']
    if len(anchors) != 8 or len(set(anchors)) != 8 or not set(anchors) <= ids:
        raise ValueError('Eight unique existing anchors required')
    for code in codes:
        if sum(s['area'] == code and s['id'] in anchors for s in situations) != 2:
            raise ValueError('Two anchors per area required')
    count = 3 if content['preview'] else 28
    if [p['day'] for p in content['practices']] != list(range(1, count + 1)):
        raise ValueError(f'Exactly {count} sequential practices required')
    if any(p['area'] not in codes for p in content['practices']):
        raise ValueError('Unknown practice area')
    if content['scoring']['mixed_min'] >= content['scoring']['strong_min']:
        raise ValueError('Scoring bands must be ordered')
    return content


def import_content(db, raw, activate=False):
    content = validate_content(raw)
    if activate and not content['preview']:
        raise ValueError('Full release publication is not enabled in this preview implementation')
    row = db.query(MotherContentRelease).filter_by(version=content['version']).first()
    if row and row.status in ('preview', 'published') and row.content != content:
        raise ValueError('Activated releases are immutable; use a new version')
    if not row:
        row = MotherContentRelease(version=content['version'], status='draft', content=content)
        db.add(row)
    elif row.status == 'draft':
        row.content = content
    if activate and row.status == 'draft':
        row.status = 'preview'
        row.published_at = datetime.now(timezone.utc)
    db.commit()
    return row


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=str(Path(__file__).resolve().parents[2] / 'seed/mothers-6-12-preview-v1.json'))
    parser.add_argument('--activate-preview', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    raw = json.loads(Path(args.file).read_text())
    validate_content(raw)
    if not args.dry_run:
        with SessionLocal() as db:
            row = import_content(db, raw, args.activate_preview)
            print(row.version, row.status)
    else:
        print('Content valid')
