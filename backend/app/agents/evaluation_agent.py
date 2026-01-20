from typing import Dict, Any
from app.services.gemini_service import GeminiService


async def evaluate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluation Agent node."""
    gemini = GeminiService()
    commitment_data = state.get("commitment_data", {})
    spending_data = state.get("spending_data", [])
    interventions = state.get("interventions", [])
    
    evaluation = await gemini.evaluate_performance(
        commitment_data,
        spending_data,
        interventions
    )
    
    return {
        "evaluation": evaluation,
        "status": "evaluated"
    }
