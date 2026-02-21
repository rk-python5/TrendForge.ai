"""
LLM Service — Ollama wrapper for content generation.
Adapted from the existing tools/llm.py.
"""

import httpx
from app.config import settings


class LLMService:
    """Wrapper for Ollama LLM operations."""

    def __init__(self):
        self.model = settings.ollama_model
        self.base_url = settings.ollama_base_url

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from a prompt using Ollama."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def generate_post(
        self,
        topic: str,
        post_type: str = "insight",
        tone: str = "professional",
        user_name: str | None = None,
        user_industry: str | None = None,
        user_expertise: str | None = None,
        max_length: int | None = None,
    ) -> str:
        """Generate a LinkedIn post."""
        user_name = user_name or settings.user_name
        user_industry = user_industry or settings.user_industry
        user_expertise = user_expertise or settings.user_expertise
        max_length = max_length or settings.max_post_length

        prompt = self._build_post_prompt(
            topic, post_type, tone,
            user_name, user_industry, user_expertise, max_length
        )
        return await self.generate(prompt, temperature=0.7)

    def _build_post_prompt(
        self, topic, post_type, tone,
        user_name, user_industry, user_expertise, max_length
    ) -> str:
        """Build the post generation prompt."""
        type_instructions = {
            "insight": "Share a valuable insight or observation from your experience. Make it thought-provoking and relevant to your industry.",
            "tip": "Share a practical tip or actionable advice that your audience can implement. Be specific and helpful.",
            "story": "Tell a compelling story from your professional experience. Include a challenge, what you learned, and a key takeaway.",
            "question": "Ask a thought-provoking question to engage your audience. Provide context and encourage discussion.",
            "achievement": "Share a professional achievement or milestone. Be humble but proud, and provide context on what you learned.",
            "opinion": "Share your informed opinion on an industry topic or trend. Back it up with reasoning and invite discussion.",
        }
        tone_guidelines = {
            "professional": "Use professional language. Be clear, credible, and authoritative.",
            "casual": "Use conversational language. Be relatable and friendly, but still professional.",
            "inspirational": "Use motivating language. Inspire and uplift your audience.",
            "educational": "Use clear, teaching language. Break down complex topics simply.",
            "thought-provoking": "Use questioning language. Challenge assumptions and encourage deep thinking.",
        }

        instruction = type_instructions.get(post_type, type_instructions["insight"])
        tone_guide = tone_guidelines.get(tone, tone_guidelines["professional"])

        return f"""You are {user_name}, a professional in {user_industry} with expertise in {user_expertise}.
You are writing a LinkedIn post to share valuable insights with your network.

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

    async def generate_hashtags(self, topic: str, content: str, count: int = 5) -> str:
        """Generate hashtags for a post."""
        prompt = f"""Based on this LinkedIn post, generate {count} relevant hashtags.

TOPIC: {topic}

POST CONTENT:
{content}

Generate exactly {count} relevant hashtags. Return only the hashtags, separated by spaces, starting with #.
Do not include any other text or explanations.

Hashtags:"""
        result = await self.generate(prompt, temperature=0.5)
        # Keep only hashtag words
        hashtags = " ".join(w for w in result.split() if w.startswith("#"))
        return hashtags

    async def review_post(self, content: str) -> dict:
        """Review a post for quality."""
        prompt = f"""You are a LinkedIn content expert. Review this post and provide constructive feedback.

POST:
{content}

Evaluate on:
1. Clarity, 2. Engagement, 3. Value, 4. Length, 5. Call-to-action

Provide:
- Overall score (1-10)
- Strengths (2-3 points)
- Improvements (2-3 suggestions)

Format:
SCORE: X/10
STRENGTHS:
- Point 1
- Point 2
IMPROVEMENTS:
- Suggestion 1
- Suggestion 2"""
        review_text = await self.generate(prompt, temperature=0.3)

        score = 7  # default
        try:
            for line in review_text.split("\n"):
                if "SCORE:" in line.upper():
                    score = int(line.split(":")[1].strip().split("/")[0])
                    break
        except Exception:
            pass

        return {"review": review_text, "score": score, "content": content}


# Global instance
llm_service = LLMService()
