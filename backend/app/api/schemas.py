from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.intervention import InterventionType


class GoalInput(BaseModel):
    goal_description: str
    target_amount: float
    timeframe: str  # e.g., "6 months"
    income_frequency: str  # weekly, biweekly, monthly
    risk_moments: Optional[List[str]] = None
    user_id: str


class CommitmentResponse(BaseModel):
    id: int
    goal_id: str
    user_id: str
    weekly_target: float
    spending_ceiling: float
    goal_amount: float
    goal_timeframe_weeks: int
    income_frequency: str
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class SpendingInput(BaseModel):
    commitment_id: int
    amount: float
    category: Optional[str] = None
    week_number: int
    description: Optional[str] = None


class SpendingResponse(BaseModel):
    id: int
    commitment_id: int
    amount: float
    category: Optional[str]
    week_number: int
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DriftResponse(BaseModel):
    has_drift: bool
    drift_type: Optional[str]
    severity: Optional[str]
    description: Optional[str]
    deviation_amount: Optional[float]


class InterventionResponse(BaseModel):
    id: int
    commitment_id: int
    type: InterventionType
    message: str
    drift_type: Optional[str]
    triggered_at: datetime
    outcome: Optional[str]

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    commitment_id: int
    # Backward compatible fields (derived from snapshot)
    adherence_rate: float
    intervention_success_rate: Optional[float]
    false_positive_interventions: int
    total_interventions: int
    weeks_tracked: int
    weeks_compliant: int
    timestamp: datetime
    # New AI-generated fields
    evaluation_snapshot: Optional[Dict[str, Any]] = None  # Full JSON snapshot from Gemini
    behavioral_recovery_score: Optional[int] = None  # 0-100 score
    behavioral_recovery_interpretation: Optional[str] = None  # AI-generated explanation
    adherence_trend: Optional[str] = None  # "improving", "declining", "stable"
    adherence_confidence: Optional[float] = None  # 0.0-1.0 confidence score
    intervention_justification: Optional[str] = None  # AI explanation for interventions
    drift_classification_confidence: Optional[float] = None  # 0.0-1.0 confidence
    planning_accuracy: Optional[float] = None  # 0.0-1.0 accuracy score
    drift_detection_precision: Optional[float] = None  # 0.0-1.0 precision score
    intervention_timing: Optional[str] = None  # "optimal", "early", "late"
    average_deviation: Optional[float] = None  # Average deviation from target

    class Config:
        from_attributes = True
