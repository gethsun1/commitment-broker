from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def plan_commitment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Commitment Planning Agent node."""
    gemini = GeminiService()
    goal_data = state.get("structured_goal", {})
    
    commitment_plan = await gemini.plan_commitment(goal_data)
    
    return {
        "commitment_plan": commitment_plan,
        "status": "commitment_planned"
    }
