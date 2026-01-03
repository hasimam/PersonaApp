from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.session import Base


class Idol(Base):
    """Idol profile model with personality trait scores."""

    __tablename__ = "idols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    image_url = Column(String(255))
    # JSONB format: {"1": 75, "2": 60, ...} where keys are trait_ids
    trait_scores = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
