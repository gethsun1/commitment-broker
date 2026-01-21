from typing import Dict, Any, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.goal_agent import structure_goal_node
from app.agents.planning_agent import plan_commitment_node
from app.agents.drift_agent import detect_drift_node
from app.agents.intervention_agent import intervene_node
from app.agents.evaluation_agent import evaluate_node


class CommitmentState(TypedDict):
    """Shared state for the commitment broker workflow."""
    user_input: Dict[str, Any]
    structured_goal: Dict[str, Any]
    commitment_plan: Dict[str, Any]
    commitment_data: Dict[str, Any]
    spending_data: list
    drift_analysis: Dict[str, Any]
    intervention: Dict[str, Any]
    evaluation: Dict[str, Any]
    interventions: list
    status: str


def should_intervene(state: CommitmentState) -> Literal["intervene", "evaluate"]:
    """Conditional edge: determine if intervention is needed."""
    drift_analysis = state.get("drift_analysis", {})
    if drift_analysis.get("has_drift", False):
        return "intervene"
    return "evaluate"


class CommitmentGraph:
    """LangGraph state machine for commitment broker workflow."""
    
    def __init__(self):
        compiled_graph = self._build_graph()
        # Wrap graph with Opik tracing if available
        self.graph = self._wrap_with_opik(compiled_graph, "commitment_creation")
    
    def _wrap_with_opik(self, compiled_graph, workflow_type: str):
        """Wrap graph with Opik tracing if Opik is properly configured."""
        try:
            from opik.integrations.langchain import OpikTracer, track_langgraph
            import opik
            import os
            
            # Check if Opik API key is set (basic check)
            # If not configured, return graph without tracing
            opik_api_key = os.getenv("OPIK_API_KEY")
            if not opik_api_key:
                # Try to check settings if available
                try:
                    from app.config import settings
                    if not settings.opik_api_key:
                        return compiled_graph
                except Exception:
                    return compiled_graph
            
            # Try to create tracer - if it fails, we'll catch and return graph without tracing
            # This catches httpx version issues, proxy errors, and other Opik initialization problems
            try:
                opik_tracer = OpikTracer(
                    project_name="commitment-broker",
                    tags=["langchain", "langgraph", "workflow"],
                    metadata={"workflow_type": workflow_type}
                )
                return track_langgraph(compiled_graph, opik_tracer)
            except (TypeError, AttributeError, ImportError) as tracer_error:
                # OpikTracer creation failed due to version incompatibility (e.g., httpx proxy issue)
                # Return graph without tracing - app will work but without Opik observability
                error_msg = str(tracer_error)
                if "proxy" in error_msg.lower() or "unexpected keyword" in error_msg.lower():
                    print(f"⚠️  Opik httpx compatibility issue for {workflow_type}. Continuing without tracing.")
                else:
                    print(f"⚠️  Opik tracer creation failed for {workflow_type}: {tracer_error}")
                return compiled_graph
            except Exception as tracer_error:
                # Any other OpikTracer creation error
                print(f"⚠️  Opik tracer creation failed for {workflow_type}: {tracer_error}")
                return compiled_graph
        except ImportError:
            # Opik not installed, return graph without tracing
            return compiled_graph
        except Exception as e:
            # If Opik tracing fails for any reason, return graph without tracing
            # This ensures the app can start even if Opik has issues
            print(f"⚠️  Opik tracing unavailable for {workflow_type}: {e}")
            return compiled_graph
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for commitment creation."""
        workflow = StateGraph(CommitmentState)
        
        # Add nodes for commitment creation workflow
        workflow.add_node("structure_goal", structure_goal_node)
        workflow.add_node("plan_commitment", plan_commitment_node)
        
        # Set entry point
        workflow.set_entry_point("structure_goal")
        
        # Add edges - simple linear flow for commitment creation
        workflow.add_edge("structure_goal", "plan_commitment")
        workflow.add_edge("plan_commitment", END)
        
        return workflow.compile()
    
    async def create_commitment(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the commitment creation workflow."""
        initial_state: CommitmentState = {
            "user_input": user_input,
            "structured_goal": {},
            "commitment_plan": {},
            "commitment_data": {},
            "spending_data": [],
            "drift_analysis": {},
            "intervention": {},
            "evaluation": {},
            "interventions": [],
            "status": "initialized"
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result
    
    async def track_and_detect(self, commitment_data: Dict[str, Any], spending_data: list) -> Dict[str, Any]:
        """Run the tracking and drift detection workflow."""
        # Create a subgraph starting from detect_drift
        tracking_graph = StateGraph(CommitmentState)
        
        tracking_graph.add_node("detect_drift", detect_drift_node)
        tracking_graph.add_node("intervene", intervene_node)
        tracking_graph.add_node("evaluate", evaluate_node)
        
        tracking_graph.set_entry_point("detect_drift")
        tracking_graph.add_conditional_edges(
            "detect_drift",
            should_intervene,
            {
                "intervene": "intervene",
                "evaluate": "evaluate"
            }
        )
        tracking_graph.add_edge("intervene", "evaluate")
        tracking_graph.add_edge("evaluate", END)
        
        compiled_tracking = tracking_graph.compile()
        
        # Wrap tracking graph with Opik tracing if available
        compiled_tracking = self._wrap_with_opik(compiled_tracking, "tracking_and_detection")
        
        initial_state: CommitmentState = {
            "user_input": {},
            "structured_goal": {},
            "commitment_plan": {},
            "commitment_data": commitment_data,
            "spending_data": spending_data,
            "drift_analysis": {},
            "intervention": {},
            "evaluation": {},
            "interventions": [],
            "status": "tracking"
        }
        
        result = await compiled_tracking.ainvoke(initial_state)
        return result
