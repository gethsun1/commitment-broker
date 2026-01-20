from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        # Use gemini-pro (stable model name that works with v1beta API)
        # gemini-1.5-pro requires v1 API which may not be available
        self.pro_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=self.api_key,
            temperature=0.7
        )
        self.flash_model = ChatGoogleGenerativeAI(
            model="gemini-pro",  # Use same model for now, can switch when API is updated
            google_api_key=self.api_key,
            temperature=0.7
        )

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        import json
        import re
        
        # Remove markdown code blocks if present
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {response}")

    async def structure_goal(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Goal Structuring Agent: Parse user input into structured goal."""
        prompt = f"""Parse the following user financial goal into a structured format.

User Input:
- Goal description: {user_input.get('goal_description', '')}
- Target amount: {user_input.get('target_amount', '')}
- Timeframe: {user_input.get('timeframe', '')}
- Income frequency: {user_input.get('income_frequency', '')}
- Risk moments: {user_input.get('risk_moments', 'None')}

Return a JSON object with:
{{
    "target_amount": float,
    "timeframe_months": int,
    "timeframe_weeks": int,
    "income_frequency": "weekly" | "biweekly" | "monthly",
    "monthly_income": float (if provided),
    "risk_moments": list of strings,
    "goal_description": string
}}
"""
        
        messages = [
            SystemMessage(content="You are a financial goal structuring agent. Parse user goals into structured formats."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.pro_model.ainvoke(messages)
        return self._parse_json_response(response.content)

    async def plan_commitment(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Commitment Planning Agent: Generate weekly commitments from goal."""
        prompt = f"""Create a weekly commitment plan for the following financial goal:

Goal Amount: ${goal_data['target_amount']}
Timeframe: {goal_data['timeframe_weeks']} weeks ({goal_data['timeframe_months']} months)
Income Frequency: {goal_data['income_frequency']}
Risk Moments: {goal_data.get('risk_moments', [])}

Calculate:
1. Weekly savings target (goal_amount / timeframe_weeks)
2. Weekly spending ceiling (based on income and savings target)
3. Behavioral constraints

Return a JSON object with:
{{
    "weekly_target": float,
    "spending_ceiling": float,
    "rationale": string explaining the plan
}}
"""
        
        messages = [
            SystemMessage(content="You are a commitment planning agent. Generate realistic weekly savings targets and spending constraints."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.pro_model.ainvoke(messages)
        return self._parse_json_response(response.content)

    async def detect_drift(self, commitment_data: Dict[str, Any], spending_data: list) -> Dict[str, Any]:
        """Drift Detection Agent: Analyze spending patterns for deviations."""
        spending_summary = "\n".join([
            f"Week {s.get('week_number', '?')}: ${s.get('amount', 0):.2f} - {s.get('category', 'uncategorized')}"
            for s in spending_data
        ])
        
        prompt = f"""Analyze spending behavior for drift detection.

Commitment Details:
- Weekly Target: ${commitment_data['weekly_target']}
- Spending Ceiling: ${commitment_data['spending_ceiling']}

Recent Spending:
{spending_summary}

Classify any drift patterns:
1. Timing: Spending happens at wrong times
2. Volume: Spending exceeds ceiling
3. Consistency: Irregular patterns

Return a JSON object with:
{{
    "has_drift": boolean,
    "drift_type": "timing" | "volume" | "consistency" | null,
    "severity": "low" | "medium" | "high",
    "description": string,
    "deviation_amount": float (if applicable)
}}
"""
        
        messages = [
            SystemMessage(content="You are a drift detection agent. Identify deviations from financial commitments."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.pro_model.ainvoke(messages)
        return self._parse_json_response(response.content)

    async def generate_intervention(self, drift_data: Dict[str, Any], commitment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intervention Agent: Generate contextual intervention based on drift."""
        prompt = f"""Generate an appropriate intervention for the following drift:

Drift Type: {drift_data.get('drift_type', 'none')}
Severity: {drift_data.get('severity', 'low')}
Description: {drift_data.get('description', '')}
Deviation: ${drift_data.get('deviation_amount', 0):.2f}

Commitment Context:
- Goal: ${commitment_data.get('goal_amount', 0)}
- Weekly Target: ${commitment_data.get('weekly_target', 0)}
- Weeks Remaining: {commitment_data.get('weeks_remaining', 0)}

Determine intervention type:
- gentle_warning: For low severity, first-time issues
- recommitment_prompt: For medium severity, recurring issues
- goal_renegotiation: For high severity, significant deviations

Return a JSON object with:
{{
    "type": "gentle_warning" | "recommitment_prompt" | "goal_renegotiation",
    "message": string (personalized intervention message),
    "tone": "supportive" | "firm" | "collaborative"
}}
"""
        
        messages = [
            SystemMessage(content="You are an intervention agent. Generate empathetic but effective interventions to help users stay on track with financial goals."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.flash_model.ainvoke(messages)
        return self._parse_json_response(response.content)

    async def evaluate_performance(self, commitment_data: Dict[str, Any], spending_data: list, interventions: list) -> Dict[str, Any]:
        """Evaluation Agent: Calculate adherence and intervention metrics."""
        total_weeks = len(set(s.get('week_number', 0) for s in spending_data))
        compliant_weeks = sum(
            1 for s in spending_data
            if s.get('amount', 0) <= commitment_data.get('spending_ceiling', 0)
        )
        
        adherence_rate = (compliant_weeks / total_weeks * 100) if total_weeks > 0 else 0
        
        successful_interventions = sum(
            1 for i in interventions
            if i.get('outcome') == 'success'
        )
        intervention_success_rate = (
            successful_interventions / len(interventions) * 100
            if interventions else 0
        )
        
        return {
            "adherence_rate": round(adherence_rate, 2),
            "intervention_success_rate": round(intervention_success_rate, 2),
            "weeks_tracked": total_weeks,
            "weeks_compliant": compliant_weeks,
            "total_interventions": len(interventions),
            "successful_interventions": successful_interventions
        }
