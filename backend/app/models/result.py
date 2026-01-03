from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Result(Base):
    """Cached test results with trait scores and idol matches."""

    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), index=True, nullable=False)
    # JSONB format: {"1": 75.5, "2": 60.2, ...} where keys are trait_ids
    trait_scores = Column(JSONB, nullable=False)
    # JSONB format: [{"idol_id": 5, "similarity": 0.92}, ...]
    top_matches = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="results")
