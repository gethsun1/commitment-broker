from typing import Dict, Any, TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from opik.integrations.langchain import OpikTracer, track_langgraph

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
        # Wrap graph with Opik tracing for automatic workflow tracing
        opik_tracer = OpikTracer(
            project_name="commitment-broker",
            tags=["langchain", "langgraph", "workflow"],
            metadata={"workflow_type": "commitment_creation"}
        )
        self.graph = track_langgraph(compiled_graph, opik_tracer)
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        workflow = StateGraph(CommitmentState)
        
        # Add nodes
        workflow.add_node("structure_goal", structure_goal_node)
        workflow.add_node("plan_commitment", plan_commitment_node)
        workflow.add_node("detect_drift", detect_drift_node)
        workflow.add_node("intervene", intervene_node)
        workflow.add_node("evaluate", evaluate_node)
        
        # Set entry point
        workflow.set_entry_point("structure_goal")
        
        # Add edges
        workflow.add_edge("structure_goal", "plan_commitment")
        workflow.add_edge("plan_commitment", END)  # Initial planning ends here
        
        # For tracking/evaluation flow
        workflow.add_edge("detect_drift", "intervene")  # Will be conditional in practice
        workflow.add_conditional_edges(
            "detect_drift",
            should_intervene,
            {
                "intervene": "intervene",
                "evaluate": "evaluate"
            }
        )
        workflow.add_edge("intervene", "evaluate")
        workflow.add_edge("evaluate", END)
        
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
        
        # Wrap tracking graph with Opik tracing
        tracking_tracer = OpikTracer(
            project_name="commitment-broker",
            tags=["langchain", "langgraph", "workflow"],
            metadata={"workflow_type": "tracking_and_detection"}
        )
        compiled_tracking = track_langgraph(compiled_tracking, tracking_tracer)
        
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
