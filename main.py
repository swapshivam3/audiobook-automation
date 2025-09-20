from config import OUTPUT_FOLDER_ID, FOLDER_ID, WEBHOOK_URL
from drive_utils import cleanup_old_files, list_files, upload_to_drive, get_image_file
from queue_manager import enqueue_pipeline
import uuid
import os
import shutil
from redis import Redis
from rq import Queue
from rq.registry import FailedJobRegistry
from config import LOCAL_DOWNLOAD_PATH, LOCAL_SANITIZED_PATH, LOCAL_NOISE_REDUCED_PATH, LOCAL_COMBINED_PATH, LOCAL_CHUNKED_PATH
import time
from combine_audio import combine, trim_long_silences
import glob
from logger import log_publish
from video_generator import make_video
from youtube_utils import handle_youtube_flow



QUEUES = ["download", "sanitize", "noisereduction", "combine"]
WORK_DIRS = [
    LOCAL_DOWNLOAD_PATH,
    LOCAL_SANITIZED_PATH,
    LOCAL_NOISE_REDUCED_PATH,
    LOCAL_COMBINED_PATH,
    LOCAL_CHUNKED_PATH
]

def cleanup_all():
    for WORK_DIR in WORK_DIRS:
        if os.path.exists(WORK_DIR):
            shutil.rmtree(WORK_DIR)
            os.makedirs(WORK_DIR, exist_ok=True)
            log_publish(f"Cleaned work dir {WORK_DIR}")

    redis_conn = Redis(host='localhost', port=6379, db=0)
    for name in QUEUES:
        failed = FailedJobRegistry(name, connection=redis_conn)
        for job_id in failed.get_job_ids():
            failed.remove(job_id, delete_job=True)
        
    log_publish("Cleanup done.")


def start(videoname):
    # cleanup doesnt work: need a service account uploaded file, check
    try:
        cleanup_old_files(OUTPUT_FOLDER_ID)
    except Exception as e:
        pass
    list_of_files = list_files(FOLDER_ID)
    
    job_list = []
    batch_id = str(uuid.uuid4())
    
    for file in list_of_files:
        # skip if not wav file
        if not file['title'].lower().endswith('.wav'):
            continue
        job_id = enqueue_pipeline(file['id'], file['title'], batch_id)
        job_list.append(job_id)

    # Wait for all jobs to finish or 10 minutes timeout
    
    timeout = time.time() + 60*10  # 10 minutes from now
    while time.time() < timeout:
        all_finished = all([job.is_finished for job in job_list])
        if all_finished:
            break
        else:
            time.sleep(5)
            
    if timeout <= time.time():
        log_publish("Timeout reached while waiting for jobs to finish.")
    
    local_files_list = glob.glob(os.path.join(LOCAL_DOWNLOAD_PATH, "*.wav"))    
    # after all jobs are finished, trigger combine
    combined_file = combine(local_files_list)
    trim_silenced = trim_long_silences(combined_file)
    image_file = get_image_file(FOLDER_ID)
    video_output_path = make_video(os.path.join(LOCAL_COMBINED_PATH,image_file.get('title', '')), trim_silenced)
    handle_youtube_flow(videoname)
    
# def renoise_reduce():
#     cleanup_old_files(OUTPUT_FOLDER_ID)
#     local_files_list = glob.glob(os.path.join(LOCAL_SANITIZED_PATH, "*.wav"))    
#     log_publish("Re-noise reducing files")
#     for file_path in local_files_list:
#         transform_audio(os.path.basename(file_path), "manual")
    
def recombine():
    cleanup_old_files(OUTPUT_FOLDER_ID)
    local_files_list = glob.glob(os.path.join(LOCAL_DOWNLOAD_PATH, "*.wav"))    
    log_publish("Recombining files")
    combined_file = combine(local_files_list)
    return combined_file

def resilence():
    cleanup_old_files(OUTPUT_FOLDER_ID)
    combined_file = os.path.join(LOCAL_COMBINED_PATH,'trimmed_audio.wav')
    log_publish("Resilencing file: " + combined_file)
    trim_silenced = trim_long_silences(combined_file)
    return trim_silenced

def regenerate_video():
    trim_silenced = os.path.join(LOCAL_COMBINED_PATH,'silenced.wav')
    image_file = get_image_file(FOLDER_ID)
    video_output_path = make_video(os.path.join(LOCAL_COMBINED_PATH,image_file.get('title', '')), trim_silenced)
    return video_output_path

def upload_video_to_youtube(videoname):
    handle_youtube_flow(videoname)

if __name__ == "__main__":
    cleanup_all()
    jobs = start()
    log_publish("Enqueued Jobs:", jobs)