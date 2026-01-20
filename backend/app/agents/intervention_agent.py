from typing import Dict, Any


async def intervene_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Intervention Agent node - rule-based intervention."""
    drift_data = state.get("drift_analysis", {})
    commitment_data = state.get("commitment_data", {})
    
    severity = drift_data.get("severity", "low")
    deviation_amount = drift_data.get("deviation_amount", 0)
    drift_type = drift_data.get("drift_type", "none")
    
    # Determine intervention type based on severity
    if severity == "high":
        intervention_type = "goal_renegotiation"
        tone = "collaborative"
        message = f"You've exceeded your spending limit by ${deviation_amount:.2f} this week. This suggests your goals might need adjustment. Would you like to discuss renegotiating your commitment?"
    elif severity == "medium":
        intervention_type = "recommitment_prompt"
        tone = "firm"
        message = f"You've overspent by ${deviation_amount:.2f} this week. Let's recommit to your goal and get back on track for the remaining weeks."
    else:
        intervention_type = "gentle_warning"
        tone = "supportive"
        message = f"Gentle reminder: You're slightly over your spending limit by ${deviation_amount:.2f}. No worries - let's stay mindful this week!"
    
    intervention = {
        "type": intervention_type,
        "message": message,
        "tone": tone
    }
    
    return {
        "intervention": intervention,
        "status": "intervention_generated"
    }
