from typing import Dict, Any


async def plan_commitment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Commitment Planning Agent node - rule-based planning."""
    goal_data = state.get("structured_goal", {})
    
    target_amount = goal_data.get("target_amount", 0)
    timeframe_weeks = goal_data.get("timeframe_weeks", 4)
    
    # Calculate weekly target
    weekly_target = round(target_amount / timeframe_weeks, 2) if timeframe_weeks > 0 else 0
    
    # Calculate spending ceiling (typically 70-80% of weekly target allows for savings)
    # This is a heuristic: if weekly target is $100, ceiling might be $75
    spending_ceiling = round(weekly_target * 0.75, 2) if weekly_target > 0 else 0
    
    commitment_plan = {
        "weekly_target": weekly_target,
        "spending_ceiling": spending_ceiling,
        "goal_timeframe_weeks": timeframe_weeks
    }
    
    return {
        "commitment_plan": commitment_plan,
        "status": "commitment_planned"
    }
