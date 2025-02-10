import re
from yt_dlp import YoutubeDL

def validate_url(url):
    # Simple regex for YouTube URL validation
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$'
    return re.match(youtube_regex, url) is not None

def fetch_video_info(url):
    ydl_opts = {'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
    return info_dict 