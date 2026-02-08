"""
Hashtag generation and management tools
"""

from typing import List
from tools.llm import llm


class HashtagGenerator:
    """
    Generate and manage hashtags for LinkedIn posts
    """
    
    # Common LinkedIn hashtags by category
    POPULAR_HASHTAGS = {
        "tech": ["#Technology", "#Tech", "#Innovation", "#Digital", "#AI", "#MachineLearning"],
        "business": ["#Business", "#Entrepreneurship", "#Leadership", "#Strategy", "#Growth"],
        "career": ["#Career", "#CareerGrowth", "#ProfessionalDevelopment", "#JobSearch", "#Networking"],
        "marketing": ["#Marketing", "#DigitalMarketing", "#ContentMarketing", "#SocialMedia", "#Branding"],
        "productivity": ["#Productivity", "#TimeManagement", "#WorkLifeBalance", "#Efficiency"],
        "learning": ["#Learning", "#Education", "#Skills", "#PersonalGrowth", "#Development"],
    }
    
    def __init__(self):
        """Initialize hashtag generator"""
        self.llm = llm
    
    def generate(self, topic: str, post_content: str, count: int = 5) -> str:
        """
        Generate hashtags for a post
        
        Args:
            topic: Post topic
            post_content: The post content
            count: Number of hashtags to generate
        
        Returns:
            Space-separated hashtags
        """
        hashtags = self.llm.generate_hashtags(topic, post_content, count)
        return hashtags
    
    def get_popular_by_category(self, category: str, count: int = 5) -> List[str]:
        """
        Get popular hashtags by category
        
        Args:
            category: Category name (tech, business, career, etc.)
            count: Number of hashtags to return
        
        Returns:
            List of hashtags
        """
        hashtags = self.POPULAR_HASHTAGS.get(category.lower(), [])
        return hashtags[:count]
    
    def combine_hashtags(self, generated: str, popular: List[str]) -> str:
        """
        Combine AI-generated and popular hashtags
        
        Args:
            generated: AI-generated hashtags string
            popular: List of popular hashtags
        
        Returns:
            Combined hashtag string
        """
        # Parse generated hashtags
        gen_tags = [tag.strip() for tag in generated.split() if tag.startswith('#')]
        
        # Combine without duplicates (case-insensitive)
        all_tags = []
        seen_lower = set()
        
        for tag in gen_tags + popular:
            tag_lower = tag.lower()
            if tag_lower not in seen_lower:
                all_tags.append(tag)
                seen_lower.add(tag_lower)
        
        return ' '.join(all_tags[:10])  # Max 10 hashtags


# Global instance
hashtag_generator = HashtagGenerator()
