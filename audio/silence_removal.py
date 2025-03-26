import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def trim_long_silences(input_file, output_file, silence_threshold=-50, min_silence_len=2000, keep_silence=1000):
    audio = AudioSegment.from_file(input_file)

    # Detect silent parts longer than `min_silence_len`
    silent_ranges = silence.detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_threshold)

    # Process audio by trimming only the long silences
    trimmed_audio = AudioSegment.empty()
    last_end = 0
    for start, end in silent_ranges:
        # Keep silence only if it's short, otherwise replace it with `keep_silence` ms silence
        trimmed_audio += audio[last_end:start]
        if end - start > min_silence_len:
            trimmed_audio += AudioSegment.silent(duration=keep_silence)
        last_end = end

    trimmed_audio += audio[last_end:]  # Add remaining part of the audio

    # Save output while keeping original quality
    trimmed_audio.export(output_file, format="wav")
    print(f"Processed audio saved as {output_file}")

trimmed_audio = "trimmed_audio.wav"

trim_long_silences(output_file, trimmed_audio)
