"""
Database operations and session management
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from storage.models import Base, Post, Analytics, Template, ContentIdea


class DatabaseManager:
    """
    Manages database connections and operations
    """
    
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./data/agent.db")
        
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables in the database"""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully!")
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== POST OPERATIONS ====================
    
    def create_post(
        self,
        topic: str,
        content: str,
        post_type: str = "insight",
        tone: str = "professional",
        hashtags: str = None,
        scheduled_for: datetime = None
    ) -> Post:
        """Create a new post"""
        with self.get_session() as session:
            word_count = len(content.split())
            estimated_read_time = word_count * 0.5  # ~2 words per second
            
            post = Post(
                topic=topic,
                content=content,
                post_type=post_type,
                tone=tone,
                hashtags=hashtags,
                scheduled_for=scheduled_for,
                word_count=word_count,
                estimated_read_time=int(estimated_read_time),
                status="draft"
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            
            # Create a detached copy with the data we need
            post_id = post.id
            
        # Return a fresh query result that won't be detached
        return self.get_post(post_id)
    
    def get_post(self, post_id: int) -> Optional[Post]:
        """Get a post by ID"""
        with self.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                # Expunge to detach from session so we can use it outside
                session.expunge(post)
            return post
    
    def get_all_posts(self, limit: int = 50) -> List[Post]:
        """Get all posts, most recent first"""
        with self.get_session() as session:
            posts = session.query(Post).order_by(desc(Post.created_at)).limit(limit).all()
            for post in posts:
                session.expunge(post)
            return posts
    
    def get_posts_by_status(self, status: str, limit: int = 50) -> List[Post]:
        """Get posts by status"""
        with self.get_session() as session:
            posts = session.query(Post).filter(Post.status == status).order_by(desc(Post.created_at)).limit(limit).all()
            for post in posts:
                session.expunge(post)
            return posts
    
    def update_post_status(self, post_id: int, status: str) -> Post:
        """Update post status"""
        with self.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                post.status = status
                if status == "approved":
                    post.approved_at = datetime.utcnow()
                elif status == "published":
                    post.published_at = datetime.utcnow()
                session.commit()
                session.expunge(post)
            return post
    
    def update_post_content(self, post_id: int, content: str) -> Post:
        """Update post content"""
        with self.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                post.content = content
                post.word_count = len(content.split())
                post.estimated_read_time = int(post.word_count * 0.5)
                session.commit()
                session.expunge(post)
            return post
    
    def update_post(self, post_id: int, updates: dict):
        """Update post and return refreshed object"""
        with self.SessionLocal() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                for key, value in updates.items():
                    setattr(post, key, value)
                session.commit()
                session.expunge(post)  # Use expunge like the other methods
                return post
            return None
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post"""
        with self.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                session.delete(post)
                session.commit()
                return True
            return False
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def add_analytics(
        self,
        post_id: int,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        impressions: int = 0,
        notes: str = None
    ) -> Analytics:
        """Add analytics data for a post"""
        with self.get_session() as session:
            analytics = Analytics(
                post_id=post_id,
                likes=likes,
                comments=comments,
                shares=shares,
                impressions=impressions,
                notes=notes
            )
            analytics.calculate_engagement_rate()
            session.add(analytics)
            session.commit()
            session.refresh(analytics)  # Refresh BEFORE expunge to load all data
            
            # Store the value before expunging
            engagement_rate = analytics.engagement_rate
            session.expunge(analytics)
            
            # Reattach the value
            analytics.engagement_rate = engagement_rate
            return analytics
    
    def get_post_analytics(self, post_id: int) -> List[Analytics]:
        """Get all analytics entries for a post"""
        with self.get_session() as session:
            analytics_list = session.query(Analytics).filter(Analytics.post_id == post_id).all()
            for analytics in analytics_list:
                session.expunge(analytics)
            return analytics_list
    
    # ==================== TEMPLATE OPERATIONS ====================
    
    def create_template(
        self,
        name: str,
        category: str,
        template_text: str,
        description: str = None
    ) -> Template:
        """Create a new template"""
        with self.get_session() as session:
            template = Template(
                name=name,
                category=category,
                template_text=template_text,
                description=description
            )
            session.add(template)
            session.commit()
            session.refresh(template)
            
            # Store ID before expunging
            template_id = template.id
            session.expunge(template)
        
        # Return a fresh query result
        return self.get_template(template_id)
    
    def get_template(self, template_id: int) -> Optional[Template]:
        """Get a template by ID"""
        with self.get_session() as session:
            template = session.query(Template).filter(Template.id == template_id).first()
            if template:
                session.expunge(template)
            return template
    
    def get_templates_by_category(self, category: str) -> List[Template]:
        """Get templates by category"""
        with self.get_session() as session:
            templates = session.query(Template).filter(Template.category == category).all()
            for template in templates:
                session.expunge(template)
            return templates
    
    def get_all_templates(self) -> List[Template]:
        """Get all templates"""
        with self.get_session() as session:
            templates = session.query(Template).all()
            for template in templates:
                session.expunge(template)
            return templates
    
    # ==================== CONTENT IDEAS OPERATIONS ====================
    
    def add_content_idea(
        self,
        idea: str,
        category: str = None,
        priority: str = "medium"
    ) -> ContentIdea:
        """Add a new content idea"""
        with self.get_session() as session:
            content_idea = ContentIdea(
                idea=idea,
                category=category,
                priority=priority
            )
            session.add(content_idea)
            session.commit()
            session.refresh(content_idea)
            
            # Store ID before expunging
            idea_id = content_idea.id
            session.expunge(content_idea)
        
        # Return a fresh query result
        return self.get_content_idea(idea_id)
    
    def get_content_idea(self, idea_id: int) -> Optional[ContentIdea]:
        """Get a content idea by ID"""
        with self.get_session() as session:
            idea = session.query(ContentIdea).filter(ContentIdea.id == idea_id).first()
            if idea:
                session.expunge(idea)
            return idea
    
    def get_content_ideas(self, status: str = "new") -> List[ContentIdea]:
        """Get content ideas by status"""
        with self.get_session() as session:
            ideas = session.query(ContentIdea).filter(ContentIdea.status == status).all()
            for idea in ideas:
                session.expunge(idea)
            return ideas
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> dict:
        """Get overall statistics"""
        with self.get_session() as session:
            total_posts = session.query(Post).count()
            published_posts = session.query(Post).filter(Post.status == "published").count()
            draft_posts = session.query(Post).filter(Post.status == "draft").count()
            approved_posts = session.query(Post).filter(Post.status == "approved").count()
            
            return {
                "total_posts": total_posts,
                "published": published_posts,
                "drafts": draft_posts,
                "approved": approved_posts,
                "pending_approval": draft_posts
            }


# Global database instance
db = DatabaseManager()
