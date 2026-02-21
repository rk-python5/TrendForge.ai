"""
Content generation service — orchestrates LLM + Supabase.
Adapted from agents/content_generator.py.
"""

from app.services.llm_service import llm_service
from app.supabase_client import supabase
from app.config import settings


class ContentService:
    """Generates LinkedIn posts and manages content lifecycle."""

    def __init__(self):
        self.llm = llm_service

    async def generate_post(
        self,
        topic: str,
        post_type: str | None = None,
        tone: str | None = None,
        save_to_db: bool = True,
        generate_hashtags: bool = True,
        source_trend_id: int | None = None,
    ) -> dict:
        """Generate a complete LinkedIn post."""
        post_type = post_type or settings.default_post_type
        tone = tone or settings.tone

        # Generate content
        content = await self.llm.generate_post(
            topic=topic,
            post_type=post_type,
            tone=tone,
        )

        # Generate hashtags
        hashtags = ""
        if generate_hashtags:
            hashtags = await self.llm.generate_hashtags(topic, content)

        # Calculate metrics
        word_count = len(content.split())
        estimated_read_time = int(word_count * 0.5)

        # Save to Supabase
        post_id = None
        if save_to_db:
            result = supabase.table("posts").insert({
                "topic": topic,
                "content": content,
                "post_type": post_type,
                "tone": tone,
                "hashtags": hashtags,
                "word_count": word_count,
                "estimated_read_time": estimated_read_time,
                "status": "draft",
                "source_trend_id": source_trend_id,
            }).execute()
            post_id = result.data[0]["id"] if result.data else None

        return {
            "post_id": post_id,
            "topic": topic,
            "content": content,
            "hashtags": hashtags,
            "post_type": post_type,
            "tone": tone,
            "word_count": word_count,
            "estimated_read_time": estimated_read_time,
        }

    async def generate_ideas(self, theme: str, count: int = 5) -> list[str]:
        """Generate post topic ideas from a theme."""
        prompt = f"""You are a LinkedIn content strategist for {settings.user_name}, who works in {settings.user_industry} with expertise in {settings.user_expertise}.

Generate {count} specific, engaging LinkedIn post topic ideas related to: {theme}

Each idea should be specific, relevant, engaging, and different from each other.
Return only the topic ideas, one per line, numbered 1-{count}."""

        response = await self.llm.generate(prompt, temperature=0.8)
        ideas = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                idea = line.lstrip("0123456789.-) ").strip()
                if idea:
                    ideas.append(idea)
        return ideas[:count]

    async def review_post(self, content: str) -> dict:
        """Review a post for quality."""
        return await self.llm.review_post(content)

    async def improve_post(self, post_id: int, feedback: str) -> dict:
        """Improve an existing post based on feedback."""
        # Fetch original
        result = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if not result.data:
            raise ValueError(f"Post {post_id} not found")

        original = result.data
        improved_content = await self.llm.generate(
            f"Improve this LinkedIn post based on feedback: {feedback}\n\nOriginal:\n{original['content']}\n\nImproved post:",
            temperature=0.6,
        )

        # Update in DB
        supabase.table("posts").update({
            "content": improved_content,
            "word_count": len(improved_content.split()),
            "estimated_read_time": int(len(improved_content.split()) * 0.5),
        }).eq("id", post_id).execute()

        return {"post_id": post_id, "content": improved_content, "status": "updated"}


# Global instance
content_service = ContentService()
