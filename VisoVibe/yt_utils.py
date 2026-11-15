import re

def extract_yt_id(url_or_id):
    """
    Extracts either a playlist ID or a video ID from YouTube URLs, iframes, or plain IDs.
    Returns: (id_type, cleaned_id) where id_type is 'playlist' or 'video'
    """
    if not url_or_id:
        return None, None
    text = url_or_id.strip()
    
    # Check playlist first (list=...)
    playlist_match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', text)
    if playlist_match:
        return 'playlist', playlist_match.group(1)
    
    # Check direct playlist format (often starts with PL, OLAK, etc.)
    if text.startswith('PL') or text.startswith('OLAK5uy_'):
        return 'playlist', text
        
    # Check standard video patterns: v=..., youtu.be/..., embed/...
    video_patterns = [
        r'(?:v=|\/v\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in video_patterns:
        match = re.search(pattern, text)
        if match:
            return 'video', match.group(1)
            
    # Default fallback
    return 'playlist', text

