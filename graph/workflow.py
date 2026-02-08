"""
LangGraph workflow for LinkedIn post generation
"""

from typing import Dict
from datetime import datetime
from langgraph.graph import StateGraph, END
from graph.state import AgentState, create_initial_state
from agents.content_generator import content_agent
from storage.database import db


class PostGenerationWorkflow:
    """
    LangGraph workflow for generating and approving LinkedIn posts
    """
    
    def __init__(self):
        """Initialize the workflow"""
        self.agent = content_agent
        self.db = db
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine
        
        Workflow:
        1. start → route_start → generate_ideas OR generate_post
        2. generate_ideas → generate_post
        3. generate_post → review_post
        4. review_post → save_post
        5. save_post → END
        """
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (each node is a function that processes state)
        workflow.add_node("route_start", self.route_start_node)
        workflow.add_node("generate_ideas", self.generate_ideas_node)
        workflow.add_node("generate_post", self.generate_post_node)
        workflow.add_node("review_post", self.review_post_node)
        workflow.add_node("save_post", self.save_post_node)
        
        # Set entry point
        workflow.set_entry_point("route_start")
        
        # Conditional edge from route_start
        workflow.add_conditional_edges(
            "route_start",
            self.should_generate_ideas,
            {
                "generate_ideas": "generate_ideas",
                "generate_post": "generate_post"
            }
        )
        
        # generate_ideas -> generate_post
        workflow.add_edge("generate_ideas", "generate_post")
        
        # generate_post -> review_post
        workflow.add_edge("generate_post", "review_post")
        
        # review_post -> save_post
        workflow.add_edge("review_post", "save_post")
        
        # save_post -> END
        workflow.add_edge("save_post", END)
        
        return workflow.compile()
    
    # ==================== ROUTING FUNCTIONS ====================
    
    def route_start_node(self, state: AgentState) -> Dict:
        """
        Initial routing node - just passes state through
        """
        return state
    
    def should_generate_ideas(self, state: AgentState) -> str:
        """
        Decide whether to generate ideas first or go straight to post generation
        """
        if state.get("theme") and not state.get("topic"):
            return "generate_ideas"
        else:
            return "generate_post"
    
    # ==================== NODE FUNCTIONS ====================
    
    def generate_ideas_node(self, state: AgentState) -> Dict:
        """
        Generate post topic ideas
        """
        try:
            theme = state["theme"]
            ideas = self.agent.generate_post_ideas(theme, count=5)
            
            # For now, auto-select the first idea
            # In the UI version, we'll let user choose
            selected_idea = ideas[0] if ideas else theme
            
            return {
                **state,
                "post_ideas": ideas,
                "selected_idea": selected_idea,
                "topic": selected_idea,
                "status": "idea_selected"
            }
        
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def generate_post_node(self, state: AgentState) -> Dict:
        """
        Generate the LinkedIn post
        """
        try:
            topic = state["topic"]
            post_type = state.get("post_type", "insight")
            tone = state.get("tone", "professional")
            
            # Check if this is a regeneration attempt
            retry_count = state.get("retry_count", 0)
            
            result = self.agent.generate_post(
                topic=topic,
                post_type=post_type,
                tone=tone,
                save_to_db=False,  # We'll save after approval
                generate_hashtags=True
            )
            
            # Calculate word and char counts
            content = result["content"]
            word_count = len(content.split())
            char_count = len(content)
            
            return {
                **state,
                "content": content,
                "hashtags": result.get("hashtags", ""),
                "word_count": word_count,
                "char_count": char_count,
                "status": "post_generated",
                "retry_count": retry_count
            }
        
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def review_post_node(self, state: AgentState) -> Dict:
        """
        Self-review the generated post
        """
        try:
            content = state["content"]
            
            review = self.agent.review_post(content)
            
            score = review.get("score", 7)
            needs_improvement = score < 6  # Threshold for auto-improvement
            
            return {
                **state,
                "review_score": score,
                "review_feedback": review["review"],
                "needs_improvement": needs_improvement,
                "status": "reviewing"
            }
        
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def save_post_node(self, state: AgentState) -> Dict:
        """
        Save the approved post to database
        """
        try:
            post = self.db.create_post(
                topic=state["topic"],
                content=state["content"],
                post_type=state.get("post_type", "insight"),
                tone=state.get("tone", "professional"),
                hashtags=state.get("hashtags", "")
            )
            
            # Capture post ID while object is still bound
            post_id = post.id if hasattr(post, 'id') else None
            
            return {
                **state,
                "post_id": post_id,
                "status": "approved",
                "approved": True,
                "completed_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    # ==================== WORKFLOW EXECUTION ====================
    
    def run(self, topic: str = None, theme: str = None, post_type: str = "insight", tone: str = "professional") -> AgentState:
        """
        Run the complete workflow
        
        Args:
            topic: Specific topic (if known)
            theme: General theme for idea generation (if topic not known)
            post_type: Type of post
            tone: Tone of post
        
        Returns:
            Final state after workflow completion
        """
        # Create initial state
        initial_state = create_initial_state(
            topic=topic,
            theme=theme,
            post_type=post_type,
            tone=tone
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Convert to regular dict to avoid any TypedDict issues
        return dict(final_state)
    
    def run_with_topic(self, topic: str, post_type: str = "insight", tone: str = "professional") -> AgentState:
        """
        Convenience method: Run workflow with a specific topic
        """
        return self.run(topic=topic, post_type=post_type, tone=tone)
    
    def run_with_theme(self, theme: str, post_type: str = "insight", tone: str = "professional") -> AgentState:
        """
        Convenience method: Run workflow with a theme (will generate ideas first)
        """
        return self.run(theme=theme, post_type=post_type, tone=tone)


# Global workflow instance
workflow = PostGenerationWorkflow()