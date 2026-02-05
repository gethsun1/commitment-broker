from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def plan_commitment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Commitment Planning Agent node - uses Gemini for planning."""
    goal_data = state.get("structured_goal", {})
    gemini = GeminiService()
    
    # Use Gemini to plan the commitment
    commitment_plan = await gemini.plan_commitment(goal_data)
    
    # Ensure goal timeframe is preserved
    commitment_plan["goal_timeframe_weeks"] = goal_data.get("timeframe_weeks", 4)
    
    return {
        "commitment_plan": commitment_plan,
        "status": "commitment_planned"
    }
