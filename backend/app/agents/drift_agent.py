from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def detect_drift_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Drift Detection Agent node - uses Gemini for detection."""
    commitment_data = state.get("commitment_data", {})
    spending_data = state.get("spending_data", [])
    gemini = GeminiService()
    
    # Use Gemini to detect drift
    drift_analysis = await gemini.detect_drift(commitment_data, spending_data)
    
    # Add contextual metadata for backend persistence if missing from AI output
    if "week_number" not in drift_analysis and spending_data:
        drift_analysis["week_number"] = max([s.get("week_number", 0) for s in spending_data])
    
    if "actual_spending" not in drift_analysis and spending_data and "week_number" in drift_analysis:
        latest_week = drift_analysis["week_number"]
        drift_analysis["actual_spending"] = sum([s.get("amount", 0) for s in spending_data if s.get("week_number") == latest_week])
    
    drift_analysis["spending_ceiling"] = commitment_data.get("spending_ceiling", 0)
    
    has_drift = drift_analysis.get("has_drift", False)
    
    return {
        "drift_analysis": drift_analysis,
        "status": "drift_detected" if has_drift else "no_drift"
    }
