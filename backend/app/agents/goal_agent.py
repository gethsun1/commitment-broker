from typing import Dict, Any
import re


async def structure_goal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Goal Structuring Agent node - rule-based structuring."""
    user_input = state.get("user_input", {})
    
    # Extract timeframe in weeks
    timeframe = user_input.get("timeframe", "1 month")
    timeframe_lower = timeframe.lower()
    
    if "month" in timeframe_lower:
        months = int(re.search(r'\d+', timeframe).group() if re.search(r'\d+', timeframe) else "1")
        timeframe_weeks = months * 4
    elif "week" in timeframe_lower:
        timeframe_weeks = int(re.search(r'\d+', timeframe).group() if re.search(r'\d+', timeframe) else "1")
    elif "year" in timeframe_lower:
        years = int(re.search(r'\d+', timeframe).group() if re.search(r'\d+', timeframe) else "1")
        timeframe_weeks = years * 52
    else:
        timeframe_weeks = 4  # Default to 1 month
    
    structured_goal = {
        "goal_id": user_input.get("goal_id") or f"goal_{user_input.get('user_id', 'default')}",
        "user_id": user_input.get("user_id", "default_user"),
        "goal_description": user_input.get("goal_description", ""),
        "target_amount": float(user_input.get("target_amount", 0)),
        "timeframe": timeframe,
        "timeframe_weeks": timeframe_weeks,
        "income_frequency": user_input.get("income_frequency", "monthly"),
        "risk_moments": user_input.get("risk_moments", [])
    }
    
    return {
        "structured_goal": structured_goal,
        "status": "goal_structured"
    }
