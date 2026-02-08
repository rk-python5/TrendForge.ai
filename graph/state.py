"""
State definitions for LangGraph workflow
"""

from typing import TypedDict, Optional, List, Literal
from datetime import datetime


class AgentState(TypedDict):
    """
    State that flows through the LangGraph workflow
    
    This represents all the information that passes between nodes
    in the agent workflow.
    """
    
    # Input from user
    topic: Optional[str]
    theme: Optional[str]  # For generating ideas
    post_type: Optional[str]
    tone: Optional[str]
    
    # Generated content
    post_ideas: Optional[List[str]]
    selected_idea: Optional[str]
    content: Optional[str]
    hashtags: Optional[str]
    variations: Optional[List[dict]]
    
    # Review and feedback
    review_score: Optional[int]
    review_feedback: Optional[str]
    needs_improvement: bool
    improvement_feedback: Optional[str]
    
    # Post metadata
    post_id: Optional[int]
    word_count: Optional[int]
    char_count: Optional[int]
    
    # Workflow control
    status: Literal[
        "generating_ideas",
        "idea_selected", 
        "generating_post",
        "post_generated",
        "reviewing",
        "awaiting_approval",
        "approved",
        "rejected",
        "needs_revision",
        "published",
        "error"
    ]
    
    # User decisions
    user_choice: Optional[str]  # approve, reject, edit, regenerate
    approved: bool
    
    # Error handling
    error: Optional[str]
    retry_count: int
    
    # Timestamps
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


def create_initial_state(
    topic: str = None,
    theme: str = None,
    post_type: str = "insight",
    tone: str = "professional"
) -> AgentState:
    """
    Create initial state for the workflow
    
    Args:
        topic: Specific topic for the post
        theme: General theme for generating ideas
        post_type: Type of post to generate
        tone: Tone of the post
    
    Returns:
        Initial agent state
    """
    return AgentState(
        topic=topic,
        theme=theme,
        post_type=post_type,
        tone=tone,
        post_ideas=None,
        selected_idea=None,
        content=None,
        hashtags=None,
        variations=None,
        review_score=None,
        review_feedback=None,
        needs_improvement=False,
        improvement_feedback=None,
        post_id=None,
        word_count=None,
        char_count=None,
        status="generating_ideas" if theme else "generating_post",
        user_choice=None,
        approved=False,
        error=None,
        retry_count=0,
        started_at=datetime.utcnow(),
        completed_at=None
    )
