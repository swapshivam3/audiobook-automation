from kafka.producer import publish_event
import config

# Start processing by sending the first event
publish_event(config.TOPICS["noise_reduction"], {"input_file": "audio.wav", "output_file": "processed_audio.wav"})
