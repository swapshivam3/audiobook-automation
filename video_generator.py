import subprocess
from pathlib import Path
from config import FOLDER_ID
from logger import log_publish
import re
import time
from PIL import Image

def make_video(image_path: str, audio_path: str, output_path: str = None):
    """
    Combine a static image and an audio file into a 720p 24fps MP4 video (YouTube ready).
    
    :param image_path: Path to the image file (e.g. "cover.jpg")
    :param audio_path: Path to the audio file (e.g. "song.mp3")
    :param output_path: Optional output video filename (default: <audio_basename>.mp4)
    """
    image = Path(image_path)
    audio = Path(audio_path)
    
    #resize image to fit 720p while keeping aspect ratio
    img = Image.open(image)
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
    img.save(image)  # overwrite original image
    
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
        "-preset", "ultrafast",           # smaller file, good quality
        "-crf", "28",                # visually lossless for still image
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-threads", "0",
        str(output_path)
    ]
    
    log_publish(f"Starting video generation")
    # subprocess.run(cmd, check=True)
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
    time_re = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
    last_update = 0
    
    for line in process.stderr:
        line = line.strip()
        # Print all lines containing "frame=" or "time="
        if "frame=" in line or "time=" in line:
            print(line)
        # Optional: extract time only
        match = time_re.search(line)
        if match and time.time() - last_update > 5:  # throttle updates
            print(f"Progress: {match.group(1)}")
            last_update = time.time()
    
    process.wait()
    log_publish(f"Video Generated")
    return str(output_path)

# Example usage:
# video_file = make_video("cover.jpg", "song.mp3")
# print("Created video:", video_file)
