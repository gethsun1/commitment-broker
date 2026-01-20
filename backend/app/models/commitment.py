from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String, nullable=False, index=True)  # Unique identifier for the goal
    user_id = Column(String, nullable=False, index=True)
    weekly_target = Column(Float, nullable=False)  # Weekly savings target
    spending_ceiling = Column(Float, nullable=False)  # Maximum weekly spending
    goal_amount = Column(Float, nullable=False)  # Total goal amount
    goal_timeframe_weeks = Column(Integer, nullable=False)  # Goal timeframe in weeks
    income_frequency = Column(String, nullable=False)  # weekly, biweekly, monthly
    risk_moments = Column(Text, nullable=True)  # JSON string of risk moments
    version = Column(Integer, default=1)  # Version for tracking changes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    spending_logs = relationship("Spending", back_populates="commitment", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="commitment", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="commitment", cascade="all, delete-orphan")
