from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def intervene_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Intervention Agent node."""
    gemini = GeminiService()
    drift_data = state.get("drift_analysis", {})
    commitment_data = state.get("commitment_data", {})
    
    intervention = await gemini.generate_intervention(drift_data, commitment_data)
    
    return {
        "intervention": intervention,
        "status": "intervention_generated"
    }
