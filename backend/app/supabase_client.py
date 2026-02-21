"""
Supabase client setup.
"""

from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """Get a Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


# Global client instance
supabase: Client = get_supabase_client()
