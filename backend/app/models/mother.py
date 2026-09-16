"""Mother's Miraat: content and anonymous owned participation records."""
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base


class MotherContentRelease(Base):
    __tablename__ = 'mother_content_releases'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String(80), unique=True, nullable=False)
    status = Column(String(20), nullable=False)
    content = Column(JSONB, nullable=False)
    published_at = Column(DateTime(timezone=True))


class MotherJourney(Base):
    __tablename__ = 'mother_journeys'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_release_id = Column(String(36), ForeignKey('mother_content_releases.id'), nullable=False)
    owner_token_hash = Column(String(64), nullable=False)
    age_band = Column(String(10), nullable=False, default='6-12')
    timezone = Column(String(80), nullable=False)
    focus_code = Column(String(30))
    status = Column(String(30), nullable=False, default='baseline')
    current_day = Column(Integer, nullable=False, default=1)
    next_available_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))


class MotherAssessment(Base):
    __tablename__ = 'mother_assessments'
    __table_args__ = (UniqueConstraint('journey_id', 'kind'),)
    id = Column(Integer, primary_key=True)
    journey_id = Column(String(36), ForeignKey('mother_journeys.id', ondelete='CASCADE'), nullable=False, index=True)
    kind = Column(String(20), nullable=False)
    answers = Column(JSONB, nullable=False, default=dict)
    result = Column(JSONB)
    submitted_at = Column(DateTime(timezone=True))


class MotherCheckin(Base):
    __tablename__ = 'mother_checkins'
    __table_args__ = (UniqueConstraint('journey_id', 'day_number'),)
    id = Column(Integer, primary_key=True)
    journey_id = Column(String(36), ForeignKey('mother_journeys.id', ondelete='CASCADE'), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    outcome = Column(String(30), nullable=False)
    repeat_requested = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
