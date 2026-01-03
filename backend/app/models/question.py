from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Question(Base):
    """Personality test question model."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    trait_id = Column(Integer, ForeignKey("traits.id"), nullable=False)
    reverse_scored = Column(Boolean, default=False)  # True if high answer = low trait
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trait = relationship("Trait", back_populates="questions")
    responses = relationship("TestResponse", back_populates="question")
