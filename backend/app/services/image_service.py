"""
Image Generation Service — uses Hugging Face Inference API for SDXL.
Stores images in Supabase Storage.
"""

import io
import httpx
from typing import Optional
from app.config import settings
from app.supabase_client import supabase
from app.services.llm_service import llm_service


class ImageService:
    """Generate images using Hugging Face Inference API."""

    HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    async def generate_image_prompt(self, post_content: str, topic: str) -> str:
        """Use LLM to create an optimized image generation prompt from post content."""
        prompt = f"""Create a short, vivid image generation prompt for a LinkedIn post banner image.

Post topic: {topic}
Post content (summary): {post_content[:300]}

Requirements:
- Professional, clean, modern aesthetic
- Abstract or conceptual (no text, no faces, no logos)
- Good for a 1200x627 LinkedIn banner
- Maximum 60 words

Image prompt:"""
        result = await llm_service.generate(prompt, temperature=0.6)
        return result.strip()[:300]

    async def generate_image(
        self,
        prompt: str,
        post_id: Optional[int] = None,
        width: int = 1200,
        height: int = 627,
    ) -> dict:
        """Generate an image via HF Inference API and optionally store it."""
        token = settings.huggingface_token
        if not token:
            return {
                "error": "HUGGINGFACE_TOKEN not set. Add it to .env to enable image generation.",
                "prompt": prompt,
                "image_url": None,
            }

        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": prompt,
            "parameters": {"width": min(width, 1024), "height": min(height, 1024)},
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(self.HF_API_URL, headers=headers, json=payload)
                if resp.status_code != 200:
                    return {"error": f"HF API error: {resp.status_code} {resp.text[:200]}", "prompt": prompt, "image_url": None}

                image_bytes = resp.content
        except Exception as e:
            return {"error": str(e), "prompt": prompt, "image_url": None}

        # Upload to Supabase Storage
        image_url = None
        try:
            filename = f"post_{post_id or 'temp'}_{int(__import__('time').time())}.png"
            path = f"generated/{filename}"
            supabase.storage.from_("images").upload(path, image_bytes, {"content-type": "image/png"})
            image_url = supabase.storage.from_("images").get_public_url(path)
        except Exception:
            # If storage fails, return base64 as fallback
            import base64
            image_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

        # Save to generated_images table
        if post_id:
            try:
                supabase.table("generated_images").insert({
                    "post_id": post_id,
                    "image_url": image_url,
                    "prompt": prompt,
                    "model": "stable-diffusion-xl-base-1.0",
                    "width": width,
                    "height": height,
                }).execute()

                # Update post image_url
                supabase.table("posts").update({"image_url": image_url}).eq("id", post_id).execute()
            except Exception:
                pass

        return {"image_url": image_url, "prompt": prompt, "post_id": post_id}

    async def generate_for_post(self, post_id: int) -> dict:
        """Generate an image for an existing post."""
        result = supabase.table("posts").select("topic, content").eq("id", post_id).single().execute()
        if not result.data:
            return {"error": "Post not found"}

        img_prompt = await self.generate_image_prompt(result.data["content"], result.data["topic"])
        return await self.generate_image(img_prompt, post_id=post_id)


image_service = ImageService()
