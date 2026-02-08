"""
Utility helper functions
"""

from datetime import datetime
from typing import Dict, List
import re


def format_post_for_display(content: str, hashtags: str = None) -> str:
    """
    Format a post for display with hashtags
    
    Args:
        content: Post content
        hashtags: Hashtags string
    
    Returns:
        Formatted post
    """
    if hashtags:
        return f"{content}\n\n{hashtags}"
    return content


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text
    
    Args:
        text: Text containing hashtags
    
    Returns:
        List of hashtags
    """
    return re.findall(r'#\w+', text)


def format_datetime(dt: datetime) -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted string
    """
    if dt is None:
        return "Never"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%B %d, %Y")


def validate_post_length(content: str, min_length: int = 100, max_length: int = 3000) -> Dict:
    """
    Validate post length
    
    Args:
        content: Post content
        min_length: Minimum length
        max_length: Maximum length
    
    Returns:
        Dictionary with validation results
    """
    length = len(content)
    
    return {
        "valid": min_length <= length <= max_length,
        "length": length,
        "min_length": min_length,
        "max_length": max_length,
        "too_short": length < min_length,
        "too_long": length > max_length
    }


def clean_hashtags(hashtags: str) -> str:
    """
    Clean and format hashtags
    
    Args:
        hashtags: Hashtag string
    
    Returns:
        Cleaned hashtags
    """
    # Extract only valid hashtags
    tags = extract_hashtags(hashtags)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower not in seen:
            unique_tags.append(tag)
            seen.add(tag_lower)
    
    return ' '.join(unique_tags)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in seconds
    
    Args:
        text: Text to read
        words_per_minute: Average reading speed
    
    Returns:
        Reading time in seconds
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return int(minutes * 60)


def get_post_metrics(content: str) -> Dict:
    """
    Get metrics for a post
    
    Args:
        content: Post content
    
    Returns:
        Dictionary with metrics
    """
    return {
        "character_count": len(content),
        "word_count": len(content.split()),
        "line_count": len(content.split('\n')),
        "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
        "hashtag_count": len(extract_hashtags(content)),
        "reading_time_seconds": calculate_reading_time(content)
    }
