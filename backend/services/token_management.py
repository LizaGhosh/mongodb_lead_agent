"""Token management utilities for context sharing"""

def count_tokens(text):
    """Count tokens in text (simple estimate: 1 token ≈ 4 characters)"""
    return len(text) // 4


def should_compress(text, max_tokens=4000):
    """Check if text should be compressed"""
    return count_tokens(text) > max_tokens


def compress_context(text, max_length=2000):
    """Simple compression by truncation (for demo)"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"
