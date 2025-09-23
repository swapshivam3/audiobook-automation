from df.enhance import enhance, init_df, load_audio, save_audio
from pydub import AudioSegment, effects
from df.utils import download_file
import torch
import subprocess
import torchaudio
from config import LOCAL_DOWNLOAD_PATH, LOCAL_SANITIZED_PATH, LOCAL_CHUNKED_PATH
import os
from logger import log_publish

def sanitize(file_path, batch_id):
    """Run ffmpeg to sanitize wav"""
    # file path is to downloads folder, need to save sanitized version in sanitized folder
    file_path = os.path.join(LOCAL_DOWNLOAD_PATH, file_path)
    sanitized = file_path.replace(LOCAL_DOWNLOAD_PATH, LOCAL_SANITIZED_PATH)
    try:
        cmd = ["ffmpeg", "-y", "-i", file_path, sanitized]
        subprocess.run(cmd, check=True)
        
        chunk_prefix = sanitized.replace('.wav', '_chunk_')
        chunk_prefix = chunk_prefix.replace(LOCAL_SANITIZED_PATH, LOCAL_CHUNKED_PATH)
        split_cmd = [
            "ffmpeg", "-y", "-i", sanitized,
            "-f", "segment", "-segment_time", "20",
            "-c", "copy", f"{chunk_prefix}%03d.wav"
        ]
        
        subprocess.run(split_cmd, check=True)
        log_publish(f"[sanitize] DONE sanitized={sanitized}")

        chunk_files = [f"{chunk_prefix}{i}.wav" for i in range(len(os.listdir(os.path.dirname(sanitized))) + 1)]
        return chunk_files
        
    except Exception as e:
        log_publish(f"[sanitize] ERROR file={file_path} error={str(e)}")
        raise e

