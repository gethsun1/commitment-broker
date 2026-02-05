from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def intervene_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Intervention Agent node - uses Gemini for contextual intervention."""
    drift_data = state.get("drift_analysis", {})
    commitment_data = state.get("commitment_data", {})
    gemini = GeminiService()
    
    # Use Gemini to generate the intervention
    intervention = await gemini.generate_intervention(drift_data, commitment_data)
    
    # Ensure drift_type is preserved for tracking
    intervention["drift_type"] = drift_data.get("drift_type", "none")
    
    return {
        "intervention": intervention,
        "status": "intervention_generated"
    }
