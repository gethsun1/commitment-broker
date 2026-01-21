from typing import Dict, Any, List
from app.services.gemini_service import GeminiService


async def evaluate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluation Agent node - collects comprehensive data and calls Gemini for AI evaluation.
    
    Collects:
    - Commitment details (goal, target, timeframe)
    - Weekly spending/contribution history
    - All drift detection events
    - All interventions with outcomes and recovery data
    """
    gemini = GeminiService()
    commitment_data = state.get("commitment_data", {})
    spending_data = state.get("spending_data", [])
    interventions = state.get("interventions", [])
    drift_analysis = state.get("drift_analysis", {})
    
    # Collect drift events - if drift_analysis exists, include it as a drift event
    drift_events = []
    if drift_analysis and drift_analysis.get("has_drift", False):
        drift_events.append({
            "drift_type": drift_analysis.get("drift_type"),
            "severity": drift_analysis.get("severity"),
            "week_number": drift_analysis.get("week_number"),
            "deviation_amount": drift_analysis.get("deviation_amount", 0),
            "description": drift_analysis.get("description", "")
        })
    
    # If drift_events list is provided in state, use it (for comprehensive evaluation)
    if "drift_events" in state:
        drift_events = state.get("drift_events", [])
    
    # Format interventions for evaluation
    # Ensure interventions have all required fields
    formatted_interventions = []
    for intervention in interventions:
        if isinstance(intervention, dict):
            formatted_interventions.append({
                "type": intervention.get("type", "unknown"),
                "drift_type": intervention.get("drift_type", "unknown"),
                "outcome": intervention.get("outcome", "pending"),
                "triggered_at": intervention.get("triggered_at", "unknown"),
                "message": intervention.get("message", "")
            })
        else:
            # If intervention is an object with attributes (e.g., SQLAlchemy model)
            formatted_interventions.append({
                "type": getattr(intervention, "type", {}).value if hasattr(getattr(intervention, "type", None), "value") else str(getattr(intervention, "type", "unknown")),
                "drift_type": getattr(intervention, "drift_type", "unknown"),
                "outcome": getattr(intervention, "outcome", "pending"),
                "triggered_at": str(getattr(intervention, "triggered_at", "unknown")),
                "message": getattr(intervention, "message", "")
            })
    
    # Call Gemini evaluation with comprehensive data
    evaluation = await gemini.evaluate_performance(
        commitment_data=commitment_data,
        spending_data=spending_data,
        interventions=formatted_interventions,
        drift_events=drift_events
    )
    
    return {
        "evaluation": evaluation,
        "status": "evaluated"
    }
