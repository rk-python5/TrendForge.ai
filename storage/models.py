"""
Database models for the LinkedIn AI Agent
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Post(Base):
    """
    Main posts table - stores all generated posts and their status
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")  # draft, approved, published, rejected
    post_type = Column(String(50), default="insight")  # insight, tip, story, question
    tone = Column(String(50), default="professional")
    hashtags = Column(Text, nullable=True)  # Comma-separated hashtags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    
    # Metadata
    word_count = Column(Integer, nullable=True)
    estimated_read_time = Column(Integer, nullable=True)  # in seconds
    
    # Relationships
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post(id={self.id}, topic='{self.topic[:30]}...', status='{self.status}')>"


class Analytics(Base):
    """
    Analytics table - tracks post performance
    """
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    
    # Calculated metrics
    engagement_rate = Column(Float, default=0.0)  # (likes + comments + shares) / impressions
    
    # Tracking
    tracked_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)  # Any observations about performance
    
    # Relationships
    post = relationship("Post", back_populates="analytics")
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate if impressions > 0"""
        if self.impressions > 0:
            total_engagement = self.likes + self.comments + self.shares
            self.engagement_rate = (total_engagement / self.impressions) * 100
        return self.engagement_rate
    
    def __repr__(self):
        return f"<Analytics(post_id={self.post_id}, likes={self.likes}, engagement={self.engagement_rate:.2f}%)>"


class Template(Base):
    """
    Post templates for different content types
    """
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(100), nullable=False)  # insight, tip, story, etc.
    template_text = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Template(name='{self.name}', category='{self.category}')>"


class ContentIdea(Base):
    """
    Store content ideas for future posts
    """
    __tablename__ = "content_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    idea = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    priority = Column(String(20), default="medium")  # high, medium, low
    status = Column(String(50), default="new")  # new, in_progress, completed, archived
    
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ContentIdea(id={self.id}, priority='{self.priority}', status='{self.status}')>"
