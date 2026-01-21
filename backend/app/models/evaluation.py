from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False, index=True)
    adherence_rate = Column(Float, nullable=False)  # Percentage of weeks meeting target (derived from snapshot)
    intervention_success_rate = Column(Float, nullable=True)  # Percentage of successful interventions (derived from snapshot)
    false_positive_interventions = Column(Integer, default=0)  # Count of false positive interventions (derived from snapshot)
    total_interventions = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Detailed metrics (derived from snapshot for backward compatibility)
    weeks_tracked = Column(Integer, nullable=False)
    weeks_compliant = Column(Integer, nullable=False)
    average_deviation = Column(Float, nullable=True)  # Average deviation from target

    # AI-generated evaluation snapshot (full JSON output from Gemini)
    evaluation_snapshot = Column(JSON, nullable=True)  # Full structured JSON from Evaluation Agent
    
    # Behavioral Recovery Score (new mandatory feature)
    behavioral_recovery_score = Column(Integer, nullable=True)  # 0-100 score
    behavioral_recovery_interpretation = Column(Text, nullable=True)  # AI-generated explanation
    
    # Additional AI-evaluated metrics
    adherence_trend = Column(String, nullable=True)  # "improving", "declining", "stable"
    adherence_confidence = Column(Float, nullable=True)  # 0.0-1.0 confidence score
    intervention_justification = Column(Text, nullable=True)  # AI explanation for interventions
    drift_classification_confidence = Column(Float, nullable=True)  # 0.0-1.0 confidence in drift classification
    planning_accuracy = Column(Float, nullable=True)  # 0.0-1.0 accuracy score
    drift_detection_precision = Column(Float, nullable=True)  # 0.0-1.0 precision score
    intervention_timing = Column(String, nullable=True)  # "optimal", "early", "late"

    # Relationships
    commitment = relationship("Commitment", back_populates="evaluations")
