"""
LangGraph StateGraph for Real Estate Lead Generation workflow
"""

import asyncio
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from utils.models import AgentState
from agents.intent_agent import IntentAgent
from agents.search_agent import SearchAgent
from agents.filter_agent import FilterAgent
from agents.enrichment_agent import EnrichmentAgent
from agents.scoring_agent import ScoringAgent
from agents.formatter_agent import FormatterAgent

class RealEstateLeadGenGraph:
    """LangGraph-based workflow for real estate lead generation"""
    
    def __init__(self):
        self.graph = self._build_graph()
        
        # Initialize agents
        self.intent_agent = IntentAgent()
        self.search_agent = SearchAgent()
        self.filter_agent = FilterAgent()
        self.enrichment_agent = EnrichmentAgent()
        self.scoring_agent = ScoringAgent()
        self.formatter_agent = FormatterAgent()
    
    def _build_graph(self) -> CompiledStateGraph:
        """Build the LangGraph StateGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("intent", self._intent_node)
        workflow.add_node("search", self._search_node)
        workflow.add_node("filter", self._filter_node)
        workflow.add_node("enrichment", self._enrichment_node)
        workflow.add_node("scoring", self._scoring_node)
        workflow.add_node("human_review", self._human_review_node)
        workflow.add_node("formatter", self._formatter_node)
        
        # Define the workflow edges
        workflow.add_edge(START, "intent")
        workflow.add_edge("intent", "search")
        workflow.add_edge("search", "filter")
        workflow.add_edge("filter", "enrichment")
        workflow.add_edge("enrichment", "scoring")
        workflow.add_edge("scoring", "human_review")
        workflow.add_edge("human_review", "formatter")
        workflow.add_edge("formatter", END)
        
        # Compile the graph
        return workflow.compile()
    
    async def run_workflow(self, user_query: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete lead generation workflow"""
        
        print("🏡 Starting Real Estate Lead Generation Workflow...")
        print(f"📝 Query: {user_query}")
        print("=" * 60)
        
        # Initialize state
        initial_state = AgentState(user_query=user_query)
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state, config=config or {})
            
            # Ensure final_leads is set
            if not hasattr(final_state, 'final_leads') or final_state.final_leads is None:
                # Handle both AgentState and dict-like states
                if hasattr(final_state, 'human_reviewed_leads'):
                    final_state.final_leads = final_state.human_reviewed_leads or []
                else:
                    final_state['final_leads'] = final_state.get('human_reviewed_leads', [])
            
            print("=" * 60)
            print("🎉 Workflow Complete!")
            
            # Get final leads handling both state types
            final_leads = final_state.final_leads if hasattr(final_state, 'final_leads') else final_state.get('final_leads', [])
            output_file = final_state.output_file if hasattr(final_state, 'output_file') else final_state.get('output_file')
            errors = final_state.errors if hasattr(final_state, 'errors') else final_state.get('errors', [])
            metadata = final_state.metadata if hasattr(final_state, 'metadata') else final_state.get('metadata', {})
            
            return {
                "success": True,
                "leads": [lead.dict() for lead in (final_leads or [])],
                "total_leads": len(final_leads or []),
                "output_file": output_file,
                "errors": errors,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "leads": [],
                "total_leads": 0
            }
    
    async def _intent_node(self, state: AgentState) -> AgentState:
        """Intent analysis node"""
        print("🎯 Step 1: Analyzing Intent...")
        return await self.intent_agent.process(state)
    
    async def _search_node(self, state: AgentState) -> AgentState:
        """Property search node"""
        print("🔍 Step 2: Searching Properties...")
        return await self.search_agent.process(state)
    
    async def _filter_node(self, state: AgentState) -> AgentState:
        """Filtering node"""
        print("🎯 Step 3: Filtering Results...")
        return await self.filter_agent.process(state)
    
    async def _enrichment_node(self, state: AgentState) -> AgentState:
        """Lead enrichment node"""
        print("📞 Step 4: Enriching Contact Data...")
        return await self.enrichment_agent.process(state)
    
    async def _scoring_node(self, state: AgentState) -> AgentState:
        """Lead scoring node"""
        print("📊 Step 5: Scoring Leads...")
        return await self.scoring_agent.process(state)
    
    async def _human_review_node(self, state: AgentState) -> AgentState:
        """Human review node - will be bypassed in CLI mode"""
        print("👤 Step 6: Human Review...")
        
        # For now, auto-approve all leads with score >= 50
        # In the UI version, this will wait for human input
        approved_leads = []
        
        for lead in state.scored_leads:
            if (lead.score or 0) >= 50:
                lead.human_reviewed = True
                lead.human_approved = True
                lead.status = "approved"
                approved_leads.append(lead)
            else:
                lead.human_reviewed = True
                lead.human_approved = False
                lead.status = "rejected"
        
        state.human_reviewed_leads = approved_leads
        state.current_step = "formatter"
        
        print(f"   ✅ Auto-approved {len(approved_leads)} leads with score >= 50")
        
        return state
    
    async def _formatter_node(self, state: AgentState) -> AgentState:
        """Output formatting node"""
        print("📁 Step 7: Formatting Output...")
        return await self.formatter_agent.process(state)
    
    def get_graph_visualization(self) -> str:
        """Get a text representation of the workflow graph"""
        return """
🏡 Real Estate Lead Generation Workflow:

START
  ↓
🎯 Intent Agent (Analyze user query)
  ↓
🔍 Search Agent (Find properties)
  ↓
🎯 Filter Agent (Apply criteria)
  ↓
📞 Enrichment Agent (Get contact info)
  ↓
📊 Scoring Agent (Score lead quality)
  ↓
👤 Human Review (Quality control)
  ↓
📁 Formatter Agent (Export results)
  ↓
END
"""

# Utility function for standalone testing
async def run_lead_generation(query: str) -> Dict[str, Any]:
    """Standalone function to run lead generation"""
    graph = RealEstateLeadGenGraph()
    return await graph.run_workflow(query)
