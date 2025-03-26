# config.py
KAFKA_BROKER = "localhost:9092"
TOPICS = {
    "noise_reduction": "audio_noise",
    "silence_trimming": "audio_silence",
    "merge": "audio_merge",
    "video_creation": "video_create",
    "youtube_upload": "youtube_upload",
}
