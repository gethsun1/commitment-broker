from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def detect_drift_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Drift Detection Agent node."""
    gemini = GeminiService()
    commitment_data = state.get("commitment_data", {})
    spending_data = state.get("spending_data", [])
    
    drift_analysis = await gemini.detect_drift(commitment_data, spending_data)
    
    return {
        "drift_analysis": drift_analysis,
        "status": "drift_detected" if drift_analysis.get("has_drift") else "no_drift"
    }
