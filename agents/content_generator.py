"""
Content Generator Agent
Handles the creation of LinkedIn posts using LLM
"""

from typing import Dict, Optional, List
from tools.llm import llm
from tools.hashtag_tools import hashtag_generator
from storage.database import db
from storage.models import Post
from config.settings import settings


class ContentGeneratorAgent:
    """
    Agent responsible for generating LinkedIn post content
    """
    
    def __init__(self):
        """Initialize the content generator agent"""
        self.llm = llm
        self.hashtag_gen = hashtag_generator
        self.db = db
    
    def generate_post_ideas(self, theme: str, count: int = 5) -> List[str]:
        """Generate post topic ideas based on a theme"""
        
        prompt = f"""You are a LinkedIn content strategist for {settings.user_name}, who works in {settings.user_industry} with expertise in {settings.user_expertise}.

Generate {count} specific, engaging LinkedIn post topic ideas related to: {theme}

Each idea should be:
- Specific and focused
- Relevant to the industry
- Engaging and valuable to the audience
- Different from each other

Return only the topic ideas, one per line, numbered 1-{count}."""

        response = self.llm.generate(prompt, temperature=0.8)
        
        # Recursively extract string
        def extract_string(obj):
            if isinstance(obj, str):
                return obj
            elif isinstance(obj, dict):
                for key in ["content", "text", "message", "result"]:
                    if key in obj:
                        return extract_string(obj[key])
                return str(obj)
            else:
                return str(obj)
        
        response_text = extract_string(response)
        
        # Parse the response into a list
        ideas = []
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                idea = line.lstrip('0123456789.-) ').strip()
                if idea:
                    ideas.append(idea)
        
        return ideas[:count]
    
    def generate_post(
        self,
        topic: str,
        post_type: str = None,
        tone: str = None,
        expertise: str = None,
        save_to_db: bool = True,
        generate_hashtags: bool = True
    ) -> Dict:
        """Generate a complete LinkedIn post"""
        
        # Use defaults from settings if not provided
        post_type = post_type or settings.default_post_type
        tone = tone or settings.tone
        
        # Generate the post using the LLM
        post_content = self.llm.generate_post(
            topic=topic,
            post_type=post_type,
            tone=tone,
            user_name=settings.user_name,
            user_industry=settings.user_industry,
            user_expertise=settings.user_expertise,
            max_length=settings.max_post_length
        )
        
        # Recursively extract string
        def extract_string(obj):
            if isinstance(obj, str):
                return obj
            elif isinstance(obj, dict):
                for key in ["content", "text", "message", "result"]:
                    if key in obj:
                        return extract_string(obj[key])
                return str(obj)
            else:
                return str(obj)
    
        post_content = extract_string(post_content)
    
        # Generate hashtags if requested
        hashtags = ""
        if generate_hashtags:
            hashtags = ""

        # Save to database if requested
        post_id = None
        if save_to_db:
            post = db.create_post(
                topic=topic,
                content=post_content,
                post_type=post_type,
                tone=tone,
                hashtags=hashtags
            )
            post_id = post.id
    
        return {
            "topic": topic,
            "content": post_content,
            "hashtags": hashtags,
            "post_type": post_type,
            "tone": tone,
            "post_id": post_id
        }
    
    def generate_variations(
        self,
        topic: str,
        count: int = 3,
        post_type: str = None,
        tone: str = None
    ) -> List[Dict]:
        """
        Generate multiple variations of a post on the same topic
        
        Args:
            topic: What the post should be about
            count: Number of variations to generate
            post_type: Type of post
            tone: Tone of post
        
        Returns:
            List of post variations
        """
        variations = []
        
        for i in range(count):
            # Vary the temperature slightly for each variation
            temp = 0.7 + (i * 0.1)
            
            result = self.generate_post(
                topic=topic,
                post_type=post_type,
                tone=tone,
                save_to_db=False,  # Don't save variations automatically
                generate_hashtags=False  # Generate hashtags only for final choice
            )
            
            variations.append(result)
        
        return variations
    
    def improve_post(
        self,
        post_id: int,
        feedback: str,
        save_as_new: bool = False
    ) -> Dict:
        """
        Improve an existing post based on feedback
        
        Args:
            post_id: ID of the post to improve
            feedback: What to improve
            save_as_new: Whether to save as a new post or update existing
        
        Returns:
            Dictionary with improved post data
        """
        # Get the original post
        original_post = self.db.get_post(post_id)
        if not original_post:
            raise ValueError(f"Post with ID {post_id} not found")
        
        # Generate improved version
        improved_content = self.llm.generate(
            prompt=f"Improve this post based on feedback: {feedback}\n\nOriginal: {original_post.content}"
        )

        # Handle dict response
        if isinstance(improved_content, dict):
            improved_content = improved_content.get("content", str(improved_content))
        
        # Update or create new
        if save_as_new:
            # Create new post
            new_post = self.db.create_post(
                topic=f"{original_post.topic} (improved)",
                content=improved_content,
                post_type=original_post.post_type,
                tone=original_post.tone,
                hashtags=original_post.hashtags
            )
            
            return {
                "post_id": new_post.id,
                "content": improved_content,
                "status": "new_draft"
            }
        else:
            # Update existing post
            updated_post = self.db.update_post(post_id, {"content": improved_content})
            
            return {
                "post_id": post_id,
                "content": improved_content,
                "status": "updated"
            }
    
    def review_post(self, content: str) -> Dict:
        """Self-review a post for quality"""
        
        prompt = f"""You are a LinkedIn content expert. Review this post and provide constructive feedback.

POST:
{content}

Evaluate on:
1. Clarity - Is the message clear?
2. Engagement - Will it engage the audience?
3. Value - Does it provide value?
4. Length - Is it appropriate length for LinkedIn?
5. Call-to-action - Does it encourage interaction?

Provide:
- Overall score (1-10)
- Strengths (2-3 points)
- Improvements (2-3 suggestions)

Format your response as:
SCORE: X/10
STRENGTHS:
- Point 1
- Point 2
IMPROVEMENTS:
- Suggestion 1
- Suggestion 2"""

        response = self.llm.generate(prompt, temperature=0.3)
        
        # Recursively extract string from nested dicts/objects
        def extract_string(obj):
            """Recursively extract string from nested structures"""
            if isinstance(obj, str):
                return obj
            elif isinstance(obj, dict):
                # Try common keys first
                for key in ["content", "text", "message", "result"]:
                    if key in obj:
                        return extract_string(obj[key])
                # If no known key, convert to string
                return str(obj)
            else:
                return str(obj)
        
        review_text = extract_string(response)
        
        result = {
            "review": review_text,
            "content": content
        }
        
        # Try to extract score
        try:
            for line in review_text.split('\n'):
                if 'SCORE:' in line.upper():
                    score_part = line.split(':')[1].strip().split('/')[0]
                    result["score"] = int(score_part)
                    break
        except Exception as e:
            print(f"Error extracting score: {e}")
            result["score"] = 0

        return result


# Global instance
content_agent = ContentGeneratorAgent()
