from yt_dlp import YoutubeDL

def download_video(url, quality, destination, progress_callback):
    ydl_opts = {
        'format': quality,
        'outtmpl': f'{destination}/%(title)s.%(ext)s',
        'progress_hooks': [progress_callback],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url]) 