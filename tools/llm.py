"""
LLM integration using Ollama
"""

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.settings import settings
from typing import Optional


class OllamaLLM:
    """
    Wrapper for Ollama LLM operations
    """
    
    def __init__(self, model: str = None, base_url: str = None):
        """Initialize Ollama LLM"""
        self.model = model or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url
        
        self.llm = Ollama(
            model=self.model,
            base_url=self.base_url,
            temperature=0.7,  # Creative but not too random
        )
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Creativity level (0.0 - 1.0)
        
        Returns:
            Generated text
        """
        # Update temperature if different
        self.llm.temperature = temperature
        
        response = self.llm.invoke(prompt)
        return response.strip()
    
    def generate_post(
        self,
        topic: str,
        post_type: str = "insight",
        tone: str = "professional",
        user_name: str = None,
        user_industry: str = None,
        user_expertise: str = None,
        max_length: int = None
    ) -> str:
        """
        Generate a LinkedIn post
        
        Args:
            topic: What the post should be about
            post_type: Type of post (insight, tip, story, question, achievement, opinion)
            tone: Tone of the post (professional, casual, inspirational, educational)
            user_name: User's name for personalization
            user_industry: User's industry
            user_expertise: User's area of expertise
            max_length: Maximum post length in characters
        
        Returns:
            Generated LinkedIn post
        """
        # Use settings if not provided
        user_name = user_name or settings.user_name
        user_industry = user_industry or settings.user_industry
        user_expertise = user_expertise or settings.user_expertise
        max_length = max_length or settings.max_post_length
        
        # Build the prompt based on post type
        prompt = self._build_post_prompt(
            topic=topic,
            post_type=post_type,
            tone=tone,
            user_name=user_name,
            user_industry=user_industry,
            user_expertise=user_expertise,
            max_length=max_length
        )
        
        # Generate the post
        post_content = self.generate(prompt, temperature=0.7)
        
        return post_content
    
    def _build_post_prompt(
        self,
        topic: str,
        post_type: str,
        tone: str,
        user_name: str,
        user_industry: str,
        user_expertise: str,
        max_length: int
    ) -> str:
        """Build a prompt for post generation"""
        
        # Base context
        context = f"""You are {user_name}, a professional in {user_industry} with expertise in {user_expertise}.
You are writing a LinkedIn post to share valuable insights with your network."""
        
        # Post type specific instructions
        type_instructions = {
            "insight": "Share a valuable insight or observation from your experience. Make it thought-provoking and relevant to your industry.",
            "tip": "Share a practical tip or actionable advice that your audience can implement. Be specific and helpful.",
            "story": "Tell a compelling story from your professional experience. Include a challenge, what you learned, and a key takeaway.",
            "question": "Ask a thought-provoking question to engage your audience. Provide context and encourage discussion.",
            "achievement": "Share a professional achievement or milestone. Be humble but proud, and provide context on what you learned.",
            "opinion": "Share your informed opinion on an industry topic or trend. Back it up with reasoning and invite discussion."
        }
        
        instruction = type_instructions.get(post_type, type_instructions["insight"])
        
        # Tone guidelines
        tone_guidelines = {
            "professional": "Use professional language. Be clear, credible, and authoritative.",
            "casual": "Use conversational language. Be relatable and friendly, but still professional.",
            "inspirational": "Use motivating language. Inspire and uplift your audience.",
            "educational": "Use clear, teaching language. Break down complex topics simply.",
            "thought-provoking": "Use questioning language. Challenge assumptions and encourage deep thinking."
        }
        
        tone_guide = tone_guidelines.get(tone, tone_guidelines["professional"])
        
        # Build the full prompt
        prompt = f"""{context}

TOPIC: {topic}

POST TYPE: {post_type}
INSTRUCTIONS: {instruction}

TONE: {tone_guide}

REQUIREMENTS:
- Maximum length: {max_length} characters
- Write in first person
- Make it engaging and valuable
- Use line breaks for readability
- Do NOT use hashtags (we'll add them separately)
- Do NOT include your name or title in the post
- End with a call-to-action or question when appropriate

Write the LinkedIn post now:"""
        
        return prompt
    
    def generate_hashtags(self, topic: str, post_content: str, count: int = 5) -> str:
        """
        Generate relevant hashtags for a post
        
        Args:
            topic: Post topic
            post_content: The actual post content
            count: Number of hashtags to generate
        
        Returns:
            Space-separated hashtags
        """
        prompt = f"""Based on this LinkedIn post, generate {count} relevant hashtags.

TOPIC: {topic}

POST CONTENT:
{post_content}

Generate exactly {count} relevant hashtags. Return only the hashtags, separated by spaces, starting with #.
Do not include any other text or explanations.

Example format: #AI #Technology #Innovation #Leadership #CareerGrowth

Hashtags:"""
        
        hashtags = self.generate(prompt, temperature=0.5)
        
        # Clean up the response
        hashtags = hashtags.strip()
        # Remove any extra text, keep only hashtags
        hashtags = ' '.join([word for word in hashtags.split() if word.startswith('#')])
        
        return hashtags[:count*20]  # Limit total length
    
    def improve_post(self, original_post: str, feedback: str) -> str:
        """
        Improve a post based on feedback
        
        Args:
            original_post: The original post content
            feedback: Specific feedback on what to improve
        
        Returns:
            Improved post content
        """
        prompt = f"""You are improving a LinkedIn post based on user feedback.

ORIGINAL POST:
{original_post}

FEEDBACK:
{feedback}

Please rewrite the post incorporating the feedback. Keep the same general topic and message, but make the requested improvements.

IMPROVED POST:"""
        
        improved = self.generate(prompt, temperature=0.6)
        return improved.strip()


# Global LLM instance
llm = OllamaLLM()
