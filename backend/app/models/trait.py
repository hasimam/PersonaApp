from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Trait(Base):
    """Personality trait model (e.g., Strategic Thinking, Creativity)."""

    __tablename__ = "traits"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=False, unique=True, index=True)
    name_ar = Column(String(100), nullable=True)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=True)
    high_behavior_en = Column(Text)  # Description of high trait behavior
    high_behavior_ar = Column(Text, nullable=True)
    low_behavior_en = Column(Text)   # Description of low trait behavior
    low_behavior_ar = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    questions = relationship("Question", back_populates="trait")
