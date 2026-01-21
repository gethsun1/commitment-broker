from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        # Use gemini-2.5-flash for all operations (faster and more cost-effective)
        self.pro_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7
        )
        self.flash_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Use flash model for faster responses
            google_api_key=self.api_key,
            temperature=0.7
        )

    def _get_opik_tracer(self, agent_type: str, method: str):
        """Get OpikTracer if Opik is configured, otherwise return None."""
        try:
            from opik.integrations.langchain import OpikTracer
            import os
            
            # Check if Opik API key is set (basic check)
            opik_api_key = os.getenv("OPIK_API_KEY")
            if not opik_api_key:
                # Try to check settings if available
                try:
                    from app.config import settings
                    if not settings.opik_api_key:
                        return None
                except Exception:
                    return None
            
            # Try to create tracer - if it fails, return None
            try:
                return OpikTracer(
                    project_name="commitment-broker",
                    tags=["langchain", "gemini", agent_type],
                    metadata={"agent_type": agent_type, "method": method}
                )
            except Exception as tracer_error:
                # OpikTracer creation failed (e.g., httpx version issue, not configured)
                # Return None so LLM calls proceed without tracing
                print(f"⚠️  Opik tracer creation failed for {agent_type}/{method}: {tracer_error}")
                return None
        except ImportError:
            # Opik not installed, return None
            return None
        except Exception:
            # If Opik is not available or fails, return None
            # The LLM calls will proceed without tracing
            return None

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
        
        # Get Opik tracer if available
        tracer = self._get_opik_tracer("goal_agent", "structure_goal")
        callbacks = [tracer] if tracer else []
        
        response = await self.pro_model.ainvoke(
            messages,
            config={"callbacks": callbacks} if callbacks else {}
        )
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
        
        # Get Opik tracer if available
        tracer = self._get_opik_tracer("planning_agent", "plan_commitment")
        callbacks = [tracer] if tracer else []
        
        response = await self.pro_model.ainvoke(
            messages,
            config={"callbacks": callbacks} if callbacks else {}
        )
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
        
        # Get Opik tracer if available
        tracer = self._get_opik_tracer("drift_agent", "detect_drift")
        callbacks = [tracer] if tracer else []
        
        response = await self.pro_model.ainvoke(
            messages,
            config={"callbacks": callbacks} if callbacks else {}
        )
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
        
        # Get Opik tracer if available
        tracer = self._get_opik_tracer("intervention_agent", "generate_intervention")
        callbacks = [tracer] if tracer else []
        
        response = await self.flash_model.ainvoke(
            messages,
            config={"callbacks": callbacks} if callbacks else {}
        )
        return self._parse_json_response(response.content)

    async def evaluate_performance(
        self, 
        commitment_data: Dict[str, Any], 
        spending_data: list, 
        interventions: list,
        drift_events: list = None
    ) -> Dict[str, Any]:
        """
        Evaluation Agent: AI-powered evaluation using Gemini 2.0 Flash.
        Produces structured JSON evaluation metrics including Behavioral Recovery Score.
        NO math-based calculations - all metrics come from AI analysis.
        """
        # Aggregate spending by week for clearer analysis
        weekly_spending = {}
        for s in spending_data:
            week = s.get('week_number', 0)
            if week not in weekly_spending:
                weekly_spending[week] = []
            weekly_spending[week].append({
                'amount': s.get('amount', 0),
                'category': s.get('category', 'uncategorized'),
                'description': s.get('description', '')
            })
        
        # Format weekly summary
        weekly_summary = []
        for week in sorted(weekly_spending.keys()):
            total_week_spending = sum(item['amount'] for item in weekly_spending[week])
            weekly_summary.append({
                'week': week,
                'total_spending': total_week_spending,
                'ceiling': commitment_data.get('spending_ceiling', 0),
                'transactions': len(weekly_spending[week])
            })
        
        # Format intervention history with recovery analysis
        intervention_history = []
        for i in interventions:
            intervention_history.append({
                'type': i.get('type', 'unknown'),
                'drift_type': i.get('drift_type', 'unknown'),
                'outcome': i.get('outcome', 'pending'),
                'triggered_at': i.get('triggered_at', 'unknown'),
                'message': i.get('message', '')[:100]  # Truncate for prompt
            })
        
        # Format drift events
        drift_summary = []
        if drift_events:
            for d in drift_events:
                drift_summary.append({
                    'type': d.get('drift_type', 'unknown'),
                    'severity': d.get('severity', 'unknown'),
                    'week': d.get('week_number', 'unknown'),
                    'deviation': d.get('deviation_amount', 0)
                })
        
        prompt = f"""You are an AI Evaluation Agent for a financial commitment tracking system. Your task is to evaluate commitment performance, intervention effectiveness, and calculate a Behavioral Recovery Score.

COMMITMENT CONTEXT:
- Goal Amount: ${commitment_data.get('goal_amount', 0):.2f}
- Weekly Target: ${commitment_data.get('weekly_target', 0):.2f}
- Spending Ceiling: ${commitment_data.get('spending_ceiling', 0):.2f}
- Timeframe: {commitment_data.get('goal_timeframe_weeks', 0)} weeks
- Weeks Remaining: {commitment_data.get('weeks_remaining', 0)}

WEEKLY SPENDING HISTORY:
{chr(10).join([f"Week {w['week']}: ${w['total_spending']:.2f} spent (ceiling: ${w['ceiling']:.2f}) - {'COMPLIANT' if w['total_spending'] <= w['ceiling'] else 'EXCEEDED'}" for w in weekly_summary])}

DRIFT DETECTION EVENTS:
{chr(10).join([f"- {d['type']} drift (severity: {d['severity']}, week: {d['week']}, deviation: ${d['deviation']:.2f})" for d in drift_summary]) if drift_summary else "No drift events detected"}

INTERVENTION HISTORY:
{chr(10).join([f"- {i['type']} intervention (drift: {i['drift_type']}, outcome: {i['outcome']})" for i in intervention_history]) if intervention_history else "No interventions triggered"}

YOUR TASK:
1. Calculate adherence rate (percentage of weeks meeting spending ceiling) and identify trend
2. Evaluate intervention success rate and false positive rate
3. Analyze drift detection accuracy (volume, timing, consistency drifts)
4. Assess agent performance (planning accuracy, drift detection precision, intervention timing)
5. Calculate Behavioral Recovery Score (0-100) considering:
   - Time to behavior correction after intervention
   - Stability post-intervention (weeks of compliance after intervention)
   - Need for escalation (did intervention require follow-up?)
   - Overall trajectory improvement

Return ONLY a valid JSON object matching this exact schema:
{{
  "adherence": {{
    "rate": 0.74,
    "trend": "improving",
    "confidence": 0.88
  }},
  "interventions": {{
    "success_rate": 0.92,
    "false_positive_rate": 0.0,
    "justification": "Intervention triggered after deviation exceeded historical tolerance"
  }},
  "drift_analysis": {{
    "volume_drifts": 1,
    "timing_drifts": 0,
    "consistency_drifts": 0,
    "classification_confidence": 0.94
  }},
  "agent_performance": {{
    "planning_accuracy": 0.95,
    "drift_detection_precision": 1.0,
    "intervention_timing": "optimal"
  }},
  "behavioral_recovery_score": {{
    "score": 87,
    "interpretation": "Strong behavioral recovery after intervention",
    "confidence": 0.91
  }}
}}

IMPORTANT: Return ONLY the JSON object, no markdown, no explanations, no code blocks."""
        
        messages = [
            SystemMessage(content="You are an expert evaluation agent for financial commitment systems. You analyze behavioral patterns, intervention effectiveness, and calculate recovery metrics. Always return valid JSON matching the required schema."),
            HumanMessage(content=prompt)
        ]
        
        # Get Opik tracer for evaluation agent
        tracer = self._get_opik_tracer("evaluation_agent", "evaluate_performance")
        callbacks = [tracer] if tracer else []
        
        try:
            response = await self.pro_model.ainvoke(
                messages,
                config={"callbacks": callbacks} if callbacks else {}
            )
            
            # Parse JSON response
            evaluation_json = self._parse_json_response(response.content)
            
            # Validate structure and return
            return evaluation_json
            
        except Exception as e:
            # Log error but return a structured fallback
            print(f"⚠️  Evaluation Agent error: {e}")
            # Return minimal valid structure
            return {
                "adherence": {
                    "rate": 0.0,
                    "trend": "unknown",
                    "confidence": 0.0
                },
                "interventions": {
                    "success_rate": 0.0,
                    "false_positive_rate": 0.0,
                    "justification": f"Evaluation error: {str(e)}"
                },
                "drift_analysis": {
                    "volume_drifts": 0,
                    "timing_drifts": 0,
                    "consistency_drifts": 0,
                    "classification_confidence": 0.0
                },
                "agent_performance": {
                    "planning_accuracy": 0.0,
                    "drift_detection_precision": 0.0,
                    "intervention_timing": "unknown"
                },
                "behavioral_recovery_score": {
                    "score": 0,
                    "interpretation": "Unable to calculate due to evaluation error",
                    "confidence": 0.0
                }
            }
