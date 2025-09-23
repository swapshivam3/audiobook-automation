# Function to display list of WAV files and let the user select
from pydub import AudioSegment, effects, silence
from config import LOCAL_COMBINED_PATH, LOCAL_NOISE_REDUCED_PATH, LOCAL_DOWNLOAD_PATH
import os
import glob
from logger import log_publish

def sort_noise_reduced_files(noise_reduced_files):
    """
    Sorts files like <anything>1_chunk000.wav, <anything>2_chunk001.wav, etc.
    Returns a sorted list by track order (as in file_list) and chunk number.
    """
    def extract_keys(path):
        fname = os.path.basename(path)
        # Split on '_chunk'
        parts = fname.split('_chunk_')
        if len(parts) != 2:
            return (fname, float('inf'))  # fallback
        track_part = parts[0]
        chunk_part = parts[1].split('.')[0]
        # Try to parse chunk number
        try:
            chunk_num = int(chunk_part)
        except Exception:
            chunk_num = float('inf')
        return (track_part, chunk_num)
    return sorted(noise_reduced_files, key=extract_keys)


def combine(file_list):
    # File list is the original download files
    # Convert to chunked path in order
    
    all_chunks = []
    for file_path in file_list:
        track_name = os.path.splitext(os.path.basename(file_path))[0]  # e.g., Track1
        pattern = os.path.join(LOCAL_NOISE_REDUCED_PATH, f"{track_name}_chunk*.wav")
        chunks = glob.glob(pattern)
        all_chunks.extend(chunks)

    sorted_chunks = sort_noise_reduced_files(all_chunks)
    combined_audio = AudioSegment.empty()
    
    for chunk_file in sorted_chunks:
        audio = AudioSegment.from_wav(chunk_file)
        combined_audio += audio
    
    output_filename = os.path.join(LOCAL_COMBINED_PATH,'trimmed_audio.wav')
    combined_audio.export(output_filename, format="wav")
    log_publish(f"Combined Files")

    return output_filename

# call combine on download folder files
# file_list = glob.glob(os.path.join(LOCAL_DOWNLOAD_PATH, "*.wav"))
# print(len(file_list))
# combine(file_list)
# print(len(combine(file_list)))
    
    
def trim_long_silences(input_file, silence_threshold=-50, min_silence_len=1900, keep_silence=800):
    """
    Trims long silences from an audio file.
    - silence_threshold: dBFS below which is considered silence (higher = more aggressive)
    - min_silence_len: minimum silence duration (ms) to be considered for trimming
    - keep_silence: ms of silence to keep in place of long silences
    """
    
    audio = AudioSegment.from_file(input_file)
    log_publish(f"Starting silence trimming")

    # Detect silent parts longer than `min_silence_len`
    silent_ranges = silence.detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_threshold)
    log_publish(f"Detected {len(silent_ranges)} long silences")

    # Process audio by trimming only the long silences
    trimmed_audio = AudioSegment.empty()
    last_end = 0
    total_trimmed = 0
    fade_duration = 300  # ms for fade in/out
    fade_per_cut = 100
    
    for start, end in silent_ranges:
        silence_dur = end - start
        # Keep silence only if it's short, otherwise replace it with `keep_silence` ms silence
        segment = audio[last_end:start]
        if len(segment) > 2*fade_per_cut:
        # Apply a tiny fade-out at the cut point
            segment = segment.fade_in(fade_per_cut).fade_out(fade_per_cut)
        elif len(segment) > fade_per_cut:
            segment = segment.fade_in(fade_per_cut)
            
        trimmed_audio += segment
        adaptive_keep = max(450, min(1250, int(silence_dur * 0.34)))
        trimmed_audio += AudioSegment.silent(duration=adaptive_keep)
        total_trimmed += (end - start - keep_silence)
        last_end = end

    trimmed_audio += audio[last_end:]  # Add remaining part of the audio
    # add slight end silence to remove rought cut
    trimmed_audio += AudioSegment.silent(duration=1000)
    trimmed_audio = effects.normalize(trimmed_audio) # Normalize audio
    trimmed_audio = trimmed_audio.fade_in(fade_duration).fade_out(fade_duration)

    log_publish(f"Total trimmed silence: {total_trimmed/1000:.2f} seconds")
    # Save output while keeping original quality
    output_file = trimmed_audio.export(os.path.join(LOCAL_COMBINED_PATH,"silenced.wav"), format="wav")
    
    return os.path.join(LOCAL_COMBINED_PATH,"silenced.wav")


