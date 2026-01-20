from pydantic import BaseModel, Field
from typing import Optional, List
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
    adherence_rate: float
    intervention_success_rate: Optional[float]
    false_positive_interventions: int
    total_interventions: int
    weeks_tracked: int
    weeks_compliant: int
    timestamp: datetime

    class Config:
        from_attributes = True
