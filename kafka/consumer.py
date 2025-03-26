from kafka import KafkaConsumer
import json
import config
from processing.noise_reduction import apply_noise_reduction
from processing.silence_removal import trim_silence
from processing.merging import merge_audio_files
from video.image_to_video import create_video
from video.youtube_upload import upload_to_youtube
from kafka.producer import publish_event

def consume_topic(topic, process_function, next_topic=None):
    """Consume messages from a Kafka topic and process them."""
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=config.KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    for message in consumer:
        data = message.value
        output = process_function(**data)

        if next_topic:
            publish_event(next_topic, output)

# Consumers
def start_consumers():
    consume_topic(config.TOPICS["noise_reduction"], apply_noise_reduction, config.TOPICS["silence_trimming"])
    consume_topic(config.TOPICS["silence_trimming"], trim_silence, config.TOPICS["merge"])
    consume_topic(config.TOPICS["merge"], merge_audio_files, config.TOPICS["video_creation"])
    consume_topic(config.TOPICS["video_creation"], create_video, config.TOPICS["youtube_upload"])
    consume_topic(config.TOPICS["youtube_upload"], upload_to_youtube)
