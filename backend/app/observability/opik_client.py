from typing import Dict, Any, Optional
import httpx
from datetime import datetime

from app.config import settings


class OpikClient:
    """Client for Opik observability and experiment tracking."""
    
    def __init__(self):
        self.api_key = settings.opik_api_key
        self.base_url = "https://api.opik.ai"  # Adjust based on actual Opik API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    async def log_experiment(
        self,
        experiment_name: str,
        prompt_version: str,
        agent_type: str,
        metrics: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log an experiment with metrics."""
        if not self.api_key:
            # No-op if no API key
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "experiment_name": experiment_name,
                    "prompt_version": prompt_version,
                    "agent_type": agent_type,
                    "metrics": metrics,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
                response = await client.post(
                    f"{self.base_url}/experiments",
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            # Log error but don't fail the main workflow
            print(f"Opik logging failed: {e}")
            return False
    
    async def log_prompt_version(
        self,
        agent_type: str,
        prompt_version: str,
        prompt_content: str
    ) -> bool:
        """Log a prompt version for an agent."""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "agent_type": agent_type,
                    "version": prompt_version,
                    "content": prompt_content,
                    "timestamp": datetime.utcnow().isoformat()
                }
                response = await client.post(
                    f"{self.base_url}/prompts",
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Opik prompt logging failed: {e}")
            return False
    
    async def log_intervention_outcome(
        self,
        intervention_id: str,
        intervention_type: str,
        outcome: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Log intervention outcome for tracking success rates."""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "intervention_id": intervention_id,
                    "intervention_type": intervention_type,
                    "outcome": outcome,
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                response = await client.post(
                    f"{self.base_url}/interventions",
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Opik intervention logging failed: {e}")
            return False
    
    async def compare_prompt_versions(
        self,
        agent_type: str,
        versions: list[str]
    ) -> Optional[Dict[str, Any]]:
        """Compare performance across prompt versions."""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/prompts/{agent_type}/compare",
                    params={"versions": ",".join(versions)},
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Opik comparison failed: {e}")
            return None
