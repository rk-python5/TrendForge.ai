"""
Trend Scout Service — fetches trends from HN, Reddit, RSS.
LLM scores relevance. Redis caches results (24h TTL).
"""

import json
import asyncio
from datetime import datetime
from typing import Optional
import httpx
import feedparser
from app.config import settings
from app.redis_client import redis_client
from app.supabase_client import supabase
from app.services.llm_service import llm_service

CACHE_TTL = 86400  # 24 hours


class TrendService:
    """Fetches, analyzes, and caches trending topics."""

    # ── Hacker News ──────────────────────────────────────

    async def fetch_hackernews(self, limit: int = 15) -> list[dict]:
        """Fetch top stories from Hacker News."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            story_ids = resp.json()[:limit]

            tasks = [self._fetch_hn_item(client, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for s in stories:
            if isinstance(s, dict) and s.get("title"):
                results.append({
                    "title": s["title"],
                    "source": "hackernews",
                    "source_url": s.get("url", f"https://news.ycombinator.com/item?id={s['id']}"),
                    "summary": None,
                    "engagement_count": s.get("score", 0),
                    "category": "tech",
                    "metadata": {"comments": s.get("descendants", 0), "by": s.get("by", "")},
                })
        return results

    async def _fetch_hn_item(self, client: httpx.AsyncClient, item_id: int) -> dict:
        resp = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
        return resp.json()

    # ── Reddit ───────────────────────────────────────────

    async def fetch_reddit(self, subreddits: list[str] | None = None, limit: int = 10) -> list[dict]:
        """Fetch hot posts from Reddit."""
        subs = subreddits or ["technology", "artificial", "MachineLearning", "programming"]
        results = []
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "TrendForge/1.0"}) as client:
            for sub in subs:
                try:
                    resp = await client.get(f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}")
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    for post in data.get("data", {}).get("children", []):
                        d = post["data"]
                        results.append({
                            "title": d["title"],
                            "source": "reddit",
                            "source_url": f"https://reddit.com{d['permalink']}",
                            "summary": (d.get("selftext") or "")[:300] or None,
                            "engagement_count": d.get("score", 0),
                            "category": sub,
                            "metadata": {
                                "subreddit": sub,
                                "comments": d.get("num_comments", 0),
                                "author": d.get("author", ""),
                            },
                        })
                except Exception:
                    continue
        return results

    # ── RSS ──────────────────────────────────────────────

    async def fetch_rss(self, feeds: list[str] | None = None, limit: int = 10) -> list[dict]:
        """Parse RSS feeds."""
        default_feeds = [
            "https://hnrss.org/newest?points=100",
            "https://techcrunch.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/technology-lab",
        ]
        urls = feeds or default_feeds
        results = []

        for url in urls:
            try:
                feed = await asyncio.to_thread(feedparser.parse, url)
                for entry in feed.entries[:limit]:
                    results.append({
                        "title": entry.get("title", ""),
                        "source": "rss",
                        "source_url": entry.get("link", ""),
                        "summary": (entry.get("summary") or "")[:300] or None,
                        "engagement_count": 0,
                        "category": "tech",
                        "metadata": {"feed_url": url, "published": entry.get("published", "")},
                    })
            except Exception:
                continue
        return results

    # ── LLM Relevance Scoring ────────────────────────────

    async def score_relevance(self, trends: list[dict]) -> list[dict]:
        """Score trend relevance using LLM (batch of titles)."""
        if not trends:
            return trends

        titles = "\n".join(f"{i+1}. {t['title']}" for i, t in enumerate(trends[:25]))
        prompt = f"""You are a content relevance scorer for a LinkedIn professional in {settings.user_industry} with expertise in {settings.user_expertise}.

Rate each topic from 0.0 to 1.0 for LinkedIn post relevance.
Return ONLY a JSON array of numbers, one per topic, in the same order.

Topics:
{titles}

JSON array of scores:"""

        try:
            raw = await llm_service.generate(prompt, temperature=0.2)
            # Extract JSON array from response
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start >= 0 and end > start:
                scores = json.loads(raw[start:end])
                for i, t in enumerate(trends[:25]):
                    t["relevance_score"] = float(scores[i]) if i < len(scores) else 0.5
            else:
                for t in trends:
                    t["relevance_score"] = 0.5
        except Exception:
            for t in trends:
                t["relevance_score"] = 0.5

        return trends

    # ── Fetch All + Cache ────────────────────────────────

    async def fetch_all_trends(self, use_cache: bool = True) -> list[dict]:
        """Fetch from all sources, score, cache, and save to Supabase."""

        # Check cache
        if use_cache and redis_client:
            try:
                cached = await redis_client.get("trends:latest")
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

        # Fetch from all sources in parallel
        hn, reddit, rss = await asyncio.gather(
            self.fetch_hackernews(),
            self.fetch_reddit(),
            self.fetch_rss(),
            return_exceptions=True,
        )

        all_trends = []
        for batch in [hn, reddit, rss]:
            if isinstance(batch, list):
                all_trends.extend(batch)

        # Deduplicate by title (lowercase)
        seen = set()
        unique = []
        for t in all_trends:
            key = t["title"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(t)
        all_trends = unique

        # Score relevance
        all_trends = await self.score_relevance(all_trends)

        # Sort by relevance * engagement
        all_trends.sort(
            key=lambda t: (t.get("relevance_score", 0) * 0.7) + (min(t.get("engagement_count", 0) / 1000, 1) * 0.3),
            reverse=True,
        )

        # Save to Supabase
        for t in all_trends[:30]:
            try:
                supabase.table("trending_topics").insert({
                    "title": t["title"][:255],
                    "source": t["source"],
                    "source_url": t.get("source_url"),
                    "summary": t.get("summary"),
                    "relevance_score": t.get("relevance_score", 0.5),
                    "engagement_count": t.get("engagement_count", 0),
                    "category": t.get("category"),
                    "metadata": json.dumps(t.get("metadata", {})),
                }).execute()
            except Exception:
                pass

        # Cache for 24h
        if redis_client:
            try:
                serializable = [{k: v for k, v in t.items()} for t in all_trends[:50]]
                await redis_client.setex("trends:latest", CACHE_TTL, json.dumps(serializable))
            except Exception:
                pass

        return all_trends[:50]

    async def get_trends_from_db(
        self,
        source: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get trends from Supabase with filters."""
        query = supabase.table("trending_topics").select("*").order("discovered_at", desc=True)
        if source:
            query = query.eq("source", source)
        if category:
            query = query.eq("category", category)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return {"trends": result.data, "count": len(result.data)}


trend_service = TrendService()
