import subprocess
from pathlib import Path
from config import FOLDER_ID
from logger import log_publish

def make_video(image_path: str, audio_path: str, output_path: str = None):
    """
    Combine a static image and an audio file into a 720p 24fps MP4 video (YouTube ready).
    
    :param image_path: Path to the image file (e.g. "cover.jpg")
    :param audio_path: Path to the audio file (e.g. "song.mp3")
    :param output_path: Optional output video filename (default: <audio_basename>.mp4)
    """
    image = Path(image_path)
    audio = Path(audio_path)
    
    if output_path is None:
        output_path = audio.with_suffix(".mp4")  # use same name as audio
    
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",                # loop image until audio ends
        "-i", str(image),
        "-i", str(audio),
        "-vf", "scale=1280:720,fps=24",
        "-r", "24",                  # enforce framerate
        "-c:v", "libx264",
        "-preset", "slow",           # smaller file, good quality
        "-crf", "18",                # visually lossless for still image
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",              # max AAC bitrate (YouTube friendly)
        "-shortest",                 # stop when audio ends
        str(output_path)
    ]
    
    log_publish(f"Starting video generation")
    subprocess.run(cmd, check=True)
    log_publish(f"Video Generated")
    return str(output_path)

# Example usage:
# video_file = make_video("cover.jpg", "song.mp3")
# print("Created video:", video_file)
