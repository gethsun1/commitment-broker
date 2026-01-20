from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def structure_goal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Goal Structuring Agent node."""
    gemini = GeminiService()
    user_input = state.get("user_input", {})
    
    structured_goal = await gemini.structure_goal(user_input)
    
    return {
        "structured_goal": structured_goal,
        "status": "goal_structured"
    }
