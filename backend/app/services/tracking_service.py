from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.models.spending import Spending
from app.models.commitment import Commitment
from app.models.intervention import Intervention, InterventionType
from app.models.evaluation import Evaluation
from app.services.gemini_service import GeminiService
from app.observability.opik_client import OpikClient
from app.agents.evaluation_agent import evaluate_node
from app.agents.graph import CommitmentState


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
        
        # Generate intervention (rule-based for demo - can use LLM in production)
        severity = drift_analysis.get("severity", "low")
        deviation_amount = drift_analysis.get("deviation_amount", 0)
        
        if severity == "high":
            intervention_data = {
                "type": "goal_renegotiation",
                "message": f"You've exceeded your spending limit by ${deviation_amount:.2f} this week. This suggests your goals might need adjustment. Would you like to discuss renegotiating your commitment?",
                "tone": "collaborative"
            }
        elif severity == "medium":
            intervention_data = {
                "type": "recommitment_prompt",
                "message": f"You've overspent by ${deviation_amount:.2f} this week. Let's recommit to your goal and get back on track for the remaining weeks.",
                "tone": "firm"
            }
        else:
            intervention_data = {
                "type": "gentle_warning",
                "message": f"Gentle reminder: You're slightly over your spending limit by ${deviation_amount:.2f}. No worries - let's stay mindful this week!",
                "tone": "supportive"
            }
        
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
        """
        Evaluate commitment performance using AI Evaluation Agent.
        NO math-based calculations - all metrics come from Gemini AI evaluation.
        """
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
        if not commitment:
            raise ValueError(f"Commitment {commitment_id} not found")
        
        # Extract comprehensive data from database
        spending_logs = commitment.spending_logs
        interventions = commitment.interventions
        
        # Prepare spending data
        spending_data = [
            {
                "week_number": s.week_number,
                "amount": s.amount,
                "category": s.category,
                "description": s.description
            }
            for s in spending_logs
        ]
        
        # Prepare commitment data
        total_weeks_tracked = len(set(s.week_number for s in spending_logs))
        commitment_data = {
            "goal_amount": commitment.goal_amount,
            "weekly_target": commitment.weekly_target,
            "spending_ceiling": commitment.spending_ceiling,
            "goal_timeframe_weeks": commitment.goal_timeframe_weeks,
            "weeks_remaining": commitment.goal_timeframe_weeks - total_weeks_tracked
        }
        
        # Prepare intervention data with all fields
        intervention_list = []
        for intervention in interventions:
            intervention_list.append({
                "type": intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                "drift_type": intervention.drift_type,
                "outcome": intervention.outcome or "pending",
                "triggered_at": str(intervention.triggered_at) if intervention.triggered_at else "unknown",
                "message": intervention.message
            })
        
        # Collect drift events from interventions (each intervention was triggered by a drift)
        drift_events = []
        for intervention in interventions:
            if intervention.drift_type:
                drift_events.append({
                    "drift_type": intervention.drift_type,
                    "severity": "medium",  # Default, could be enhanced
                    "week_number": None,  # Could be extracted from intervention timing
                    "deviation_amount": 0  # Could be calculated if stored
                })
        
        # Create evaluation workflow
        evaluation_graph = StateGraph(CommitmentState)
        evaluation_graph.add_node("evaluate", evaluate_node)
        evaluation_graph.set_entry_point("evaluate")
        evaluation_graph.add_edge("evaluate", END)
        compiled_evaluation = evaluation_graph.compile()
        
        # Wrap with Opik tracing if available
        try:
            from opik.integrations.langchain import OpikTracer, track_langgraph
            import os
            opik_api_key = os.getenv("OPIK_API_KEY")
            if opik_api_key:
                try:
                    opik_tracer = OpikTracer(
                        project_name="commitment-broker",
                        tags=["langchain", "langgraph", "evaluation_workflow"],
                        metadata={"workflow_type": "evaluation_only"}
                    )
                    compiled_evaluation = track_langgraph(compiled_evaluation, opik_tracer)
                except Exception:
                    pass  # Continue without Opik if it fails
        except ImportError:
            pass  # Opik not available
        
        # Prepare state for evaluation workflow
        initial_state: CommitmentState = {
            "user_input": {},
            "structured_goal": {},
            "commitment_plan": {},
            "commitment_data": commitment_data,
            "spending_data": spending_data,
            "drift_analysis": {},
            "intervention": {},
            "evaluation": {},
            "interventions": intervention_list,
            "drift_events": drift_events,
            "status": "evaluating"
        }
        
        # Run evaluation agent workflow
        result = await compiled_evaluation.ainvoke(initial_state)
        evaluation_json = result.get("evaluation", {})
        
        # Parse AI-generated evaluation snapshot
        if not evaluation_json:
            raise ValueError("Evaluation agent returned empty result")
        
        # Extract metrics from AI output for backward compatibility
        adherence_data = evaluation_json.get("adherence", {})
        interventions_data = evaluation_json.get("interventions", {})
        drift_analysis_data = evaluation_json.get("drift_analysis", {})
        agent_performance_data = evaluation_json.get("agent_performance", {})
        behavioral_recovery = evaluation_json.get("behavioral_recovery_score", {})
        
        # Calculate derived metrics for backward compatibility
        adherence_rate = adherence_data.get("rate", 0.0) * 100  # Convert from 0-1 to percentage
        total_weeks = total_weeks_tracked
        compliant_weeks = int((adherence_rate / 100) * total_weeks) if total_weeks > 0 else 0
        
        intervention_success_rate = interventions_data.get("success_rate", 0.0) * 100 if interventions_data.get("success_rate") else None
        false_positive_rate = interventions_data.get("false_positive_rate", 0.0)
        false_positives = int(false_positive_rate * len(interventions)) if interventions else 0
        
        # Create Evaluation record with full snapshot
        evaluation = Evaluation(
            commitment_id=commitment_id,
            # Backward compatible fields (derived from snapshot)
            adherence_rate=adherence_rate,
            intervention_success_rate=intervention_success_rate,
            false_positive_interventions=false_positives,
            total_interventions=len(interventions),
            weeks_tracked=total_weeks,
            weeks_compliant=compliant_weeks,
            # New AI-generated fields
            evaluation_snapshot=evaluation_json,  # Full JSON snapshot
            behavioral_recovery_score=behavioral_recovery.get("score"),
            behavioral_recovery_interpretation=behavioral_recovery.get("interpretation"),
            adherence_trend=adherence_data.get("trend"),
            adherence_confidence=adherence_data.get("confidence"),
            intervention_justification=interventions_data.get("justification"),
            drift_classification_confidence=drift_analysis_data.get("classification_confidence"),
            planning_accuracy=agent_performance_data.get("planning_accuracy"),
            drift_detection_precision=agent_performance_data.get("drift_detection_precision"),
            intervention_timing=agent_performance_data.get("intervention_timing")
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # Log evaluation metrics to Opik
        if self.opik:
            try:
                await self.opik.log_experiment(
                    experiment_name="evaluation_run",
                    prompt_version="v1",
                    agent_type="evaluation_agent",
                    metrics={
                        "adherence_rate": adherence_rate,
                        "behavioral_recovery_score": behavioral_recovery.get("score", 0),
                        "intervention_success_rate": intervention_success_rate or 0,
                        "drift_classification_confidence": drift_analysis_data.get("classification_confidence", 0)
                    },
                    metadata={
                        "commitment_id": commitment_id,
                        "weeks_tracked": total_weeks,
                        "total_interventions": len(interventions)
                    }
                )
            except Exception as e:
                print(f"⚠️  Opik evaluation logging failed: {e}")
        
        return evaluation
