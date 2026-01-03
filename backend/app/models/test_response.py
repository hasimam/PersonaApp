from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class TestResponse(Base):
    """Individual question response from a user."""

    __tablename__ = "test_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    response = Column(Integer, nullable=False)  # Likert scale value (1-5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
