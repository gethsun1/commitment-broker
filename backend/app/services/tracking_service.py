from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.models.spending import Spending
from app.models.commitment import Commitment
from app.models.intervention import Intervention, InterventionType
from app.models.evaluation import Evaluation
from app.services.gemini_service import GeminiService
from app.observability.opik_client import OpikClient


class TrackingService:
    def __init__(self):
        self.gemini = GeminiService()
        self.opik = OpikClient()
    
    async def add_spending(
        self,
        db: Session,
        commitment_id: int,
        amount: float,
        category: Optional[str],
        week_number: int,
        description: Optional[str] = None
    ) -> Spending:
        """Add spending entry and trigger drift detection if needed."""
        spending = Spending(
            commitment_id=commitment_id,
            amount=amount,
            category=category,
            week_number=week_number,
            description=description
        )
        
        db.add(spending)
        db.commit()
        db.refresh(spending)
        
        return spending
    
    async def trigger_intervention(
        self,
        db: Session,
        commitment_id: int,
        drift_analysis: Dict[str, Any]
    ) -> Intervention:
        """Trigger an intervention based on drift analysis."""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
        if not commitment:
            raise ValueError(f"Commitment {commitment_id} not found")
        
        # Get spending data for context
        spending_logs = commitment.spending_logs
        spending_data = [
            {"week_number": s.week_number, "amount": s.amount, "category": s.category}
            for s in spending_logs
        ]
        
        commitment_data = {
            "weekly_target": commitment.weekly_target,
            "spending_ceiling": commitment.spending_ceiling,
            "goal_amount": commitment.goal_amount,
            "weeks_remaining": commitment.goal_timeframe_weeks - len(set(s.week_number for s in spending_logs))
        }
        
        # Generate intervention
        intervention_data = await self.gemini.generate_intervention(drift_analysis, commitment_data)
        
        # Map to InterventionType enum
        type_mapping = {
            "gentle_warning": InterventionType.GENTLE_WARNING,
            "recommitment_prompt": InterventionType.RECOMMITMENT_PROMPT,
            "goal_renegotiation": InterventionType.GOAL_RENEGOTIATION
        }
        
        intervention = Intervention(
            commitment_id=commitment_id,
            type=type_mapping.get(intervention_data.get("type"), InterventionType.GENTLE_WARNING),
            message=intervention_data.get("message", ""),
            drift_type=drift_analysis.get("drift_type")
        )
        
        db.add(intervention)
        db.commit()
        db.refresh(intervention)
        
        # Log to Opik
        await self.opik.log_intervention_outcome(
            intervention_id=str(intervention.id),
            intervention_type=intervention.type.value,
            outcome="pending",
            metrics={
                "drift_type": drift_analysis.get("drift_type"),
                "severity": drift_analysis.get("severity")
            }
        )
        
        return intervention
    
    async def evaluate_commitment(
        self,
        db: Session,
        commitment_id: int
    ) -> Evaluation:
        """Evaluate commitment performance."""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
        if not commitment:
            raise ValueError(f"Commitment {commitment_id} not found")
        
        spending_logs = commitment.spending_logs
        interventions = commitment.interventions
        
        total_weeks = len(set(s.week_number for s in spending_logs))
        compliant_weeks = sum(
            1 for s in spending_logs
            if s.amount <= commitment.spending_ceiling
        )
        
        adherence_rate = (compliant_weeks / total_weeks * 100) if total_weeks > 0 else 0
        
        successful_interventions = sum(
            1 for i in interventions
            if i.outcome == "success"
        )
        intervention_success_rate = (
            successful_interventions / len(interventions) * 100
            if interventions else None
        )
        
        false_positives = sum(
            1 for i in interventions
            if i.outcome == "false_positive"
        )
        
        evaluation = Evaluation(
            commitment_id=commitment_id,
            adherence_rate=adherence_rate,
            intervention_success_rate=intervention_success_rate,
            false_positive_interventions=false_positives,
            total_interventions=len(interventions),
            weeks_tracked=total_weeks,
            weeks_compliant=compliant_weeks
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        return evaluation
