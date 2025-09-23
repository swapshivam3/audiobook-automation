from rq import Queue, Retry
from redis import Redis
from rq.job import Job
from sanitize import sanitize
from drive_utils import download_file
from config import LOCAL_DOWNLOAD_PATH
from noise_reduce import transform_audio
import time

redis_client = Redis(host='localhost', port=6379, db=0)

q_sanitize = Queue("sanitize", connection=redis_client, default_result_ttl=3600)
q_noise = Queue("noisereduction", connection=redis_client, default_result_ttl=3600)
q_download = Queue("download", connection=redis_client, default_result_ttl=3600)

def enqueue_pipeline(file_id, file_title, batch_id):
    job1 = q_download.enqueue(download_file, file_id, file_title, LOCAL_DOWNLOAD_PATH, retry=Retry(max=3))
    job2 = q_sanitize.enqueue(sanitize, file_title, batch_id, depends_on=job1, retry=Retry(max=3))
    job3 = q_noise.enqueue(transform_audio, file_title, batch_id, depends_on=job2, retry=Retry(max=3))
    return job3

def requeue_noise(file_title, batch_id):
    job2 = q_noise.enqueue(transform_audio, file_title, batch_id, retry=Retry(max=3))
    return job2