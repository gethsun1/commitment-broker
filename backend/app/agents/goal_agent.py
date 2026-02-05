from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def structure_goal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Goal Structuring Agent node - uses Gemini for parsing."""
    user_input = state.get("user_input", {})
    gemini = GeminiService()
    
    # Use Gemini to structure the goal
    ai_structured = await gemini.structure_goal(user_input)
    
    # Merge with system identifiers
    structured_goal = {
        **ai_structured,
        "goal_id": user_input.get("goal_id") or f"goal_{user_input.get('user_id', 'default')}",
        "user_id": user_input.get("user_id", "default_user"),
        "timeframe": user_input.get("timeframe", ai_structured.get("timeframe_weeks", 4)),
    }
    
    return {
        "structured_goal": structured_goal,
        "status": "goal_structured"
    }
