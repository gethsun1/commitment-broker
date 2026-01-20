from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class InterventionType(str, enum.Enum):
    GENTLE_WARNING = "gentle_warning"
    RECOMMITMENT_PROMPT = "recommitment_prompt"
    GOAL_RENEGOTIATION = "goal_renegotiation"


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False, index=True)
    type = Column(SQLEnum(InterventionType), nullable=False)
    message = Column(Text, nullable=False)  # Intervention message sent to user
    drift_type = Column(String, nullable=True)  # timing, volume, consistency
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    outcome = Column(String, nullable=True)  # success, ignored, failed
    notes = Column(Text, nullable=True)  # Additional notes about the intervention

    # Relationships
    commitment = relationship("Commitment", back_populates="interventions")
