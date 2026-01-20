from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.commitment import Commitment
from app.agents.graph import CommitmentGraph
from app.observability.opik_client import OpikClient


class CommitmentService:
    def __init__(self):
        self.graph = CommitmentGraph()
        self.opik = OpikClient()
    
    async def create_commitment(self, db: Session, user_input: Dict[str, Any]) -> Commitment:
        """Create a new commitment using the agent workflow."""
        # Run the agent workflow
        result = await self.graph.create_commitment(user_input)
        
        structured_goal = result.get("structured_goal", {})
        commitment_plan = result.get("commitment_plan", {})
        
        # Log to Opik
        await self.opik.log_experiment(
            experiment_name="commitment_creation",
            prompt_version="v1",
            agent_type="planning_agent",
            metrics={
                "goal_amount": structured_goal.get("target_amount"),
                "timeframe_weeks": structured_goal.get("timeframe_weeks"),
                "weekly_target": commitment_plan.get("weekly_target")
            }
        )
        
        # Create commitment in database
        goal_id = str(uuid.uuid4())
        commitment = Commitment(
            goal_id=goal_id,
            user_id=user_input.get("user_id", "default_user"),
            weekly_target=commitment_plan.get("weekly_target", 0),
            spending_ceiling=commitment_plan.get("spending_ceiling", 0),
            goal_amount=structured_goal.get("target_amount", 0),
            goal_timeframe_weeks=structured_goal.get("timeframe_weeks", 0),
            income_frequency=structured_goal.get("income_frequency", "monthly"),
            risk_moments=str(structured_goal.get("risk_moments", [])),
            version=1
        )
        
        db.add(commitment)
        db.commit()
        db.refresh(commitment)
        
        return commitment
    
    async def track_spending_and_detect_drift(
        self,
        db: Session,
        commitment_id: int
    ) -> Dict[str, Any]:
        """Track spending and run drift detection workflow."""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
        if not commitment:
            raise ValueError(f"Commitment {commitment_id} not found")
        
        # Get spending data
        spending_logs = commitment.spending_logs
        spending_data = [
            {
                "week_number": s.week_number,
                "amount": s.amount,
                "category": s.category
            }
            for s in spending_logs
        ]
        
        # Prepare commitment data
        commitment_data = {
            "weekly_target": commitment.weekly_target,
            "spending_ceiling": commitment.spending_ceiling,
            "goal_amount": commitment.goal_amount,
            "weeks_remaining": commitment.goal_timeframe_weeks - len(set(s.week_number for s in spending_logs))
        }
        
        # Run drift detection workflow
        result = await self.graph.track_and_detect(commitment_data, spending_data)
        
        drift_analysis = result.get("drift_analysis", {})
        
        return {
            "drift_analysis": drift_analysis,
            "should_intervene": drift_analysis.get("has_drift", False)
        }
