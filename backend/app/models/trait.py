from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Trait(Base):
    """Personality trait model (e.g., Strategic Thinking, Creativity)."""

    __tablename__ = "traits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    high_behavior = Column(Text)  # Description of high trait behavior
    low_behavior = Column(Text)   # Description of low trait behavior
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    questions = relationship("Question", back_populates="trait")
