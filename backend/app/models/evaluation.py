from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False, index=True)
    adherence_rate = Column(Float, nullable=False)  # Percentage of weeks meeting target
    intervention_success_rate = Column(Float, nullable=True)  # Percentage of successful interventions
    false_positive_interventions = Column(Integer, default=0)  # Count of false positive interventions
    total_interventions = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Detailed metrics
    weeks_tracked = Column(Integer, nullable=False)
    weeks_compliant = Column(Integer, nullable=False)
    average_deviation = Column(Float, nullable=True)  # Average deviation from target

    # Relationships
    commitment = relationship("Commitment", back_populates="evaluations")
