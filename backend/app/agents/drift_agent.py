from typing import Dict, Any
from collections import defaultdict


async def detect_drift_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Drift Detection Agent node - rule-based detection."""
    commitment_data = state.get("commitment_data", {})
    spending_data = state.get("spending_data", [])
    
    spending_ceiling = commitment_data.get("spending_ceiling", 0)
    weekly_target = commitment_data.get("weekly_target", 0)
    
    # Aggregate spending by week
    weekly_spending = defaultdict(float)
    for entry in spending_data:
        week = entry.get("week_number", 0)
        amount = entry.get("amount", 0)
        weekly_spending[week] += amount
    
    # Detect drift in latest week
    if not weekly_spending:
        return {
            "drift_analysis": {
                "has_drift": False,
                "drift_type": None,
                "severity": "low",
                "description": "No spending data yet",
                "deviation_amount": 0,
                "week_number": None,
                "actual_spending": 0,
                "spending_ceiling": spending_ceiling
            },
            "status": "no_drift"
        }
    
    latest_week = max(weekly_spending.keys())
    latest_spending = weekly_spending[latest_week]
    deviation = latest_spending - spending_ceiling
    
    # Determine drift
    has_drift = deviation > 0
    severity = "high" if deviation > spending_ceiling * 0.5 else "medium" if deviation > 0 else "low"
    drift_type = "volume" if has_drift else None
    
    drift_analysis = {
        "has_drift": has_drift,
        "drift_type": drift_type,
        "severity": severity,
        "description": f"Spending ${latest_spending:.2f} in week {latest_week}, exceeding ceiling by ${deviation:.2f}" if has_drift else f"Spending ${latest_spending:.2f} in week {latest_week}, within limits",
        "deviation_amount": deviation if has_drift else 0,
        "week_number": latest_week,
        "actual_spending": latest_spending,
        "spending_ceiling": spending_ceiling
    }
    
    return {
        "drift_analysis": drift_analysis,
        "status": "drift_detected" if has_drift else "no_drift"
    }
