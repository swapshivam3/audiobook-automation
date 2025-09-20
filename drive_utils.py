from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from config import SERVICE_ACCOUNT_FILE
import os
from logger import log_publish
from config import LOCAL_COMBINED_PATH

settings = {
    "client_config_backend": "service",
    "service_config": {
        "client_json_file_path": SERVICE_ACCOUNT_FILE,
    },
}
drive = None

def get_drive():
    global drive
    if drive is None:
        gauth = GoogleAuth(settings=settings) 
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)
    return drive

def cleanup_old_files(output_folder_id):
    drive = get_drive()
    file_list = drive.ListFile({'q': f"'{output_folder_id}' in parents and trashed=false"}).GetList()
    log_publish(f"[drive] cleanup_old_files: found {len(file_list)} files in folder {output_folder_id}")
    for file in file_list:
        try:
            file.Delete()
            log_publish(f"[drive] Deleted: {file.get('title', '<unknown>')}")
        except Exception as e:
            log_publish(f"[drive] ERROR deleting file id={file.get('id','<unknown>')} title={file.get('title','<unknown>')} error={str(e)}")


def list_files(folder_id):
    drive = get_drive()
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    log_publish(f"[drive] list_files: found {len(file_list)-2} files in folder {folder_id}")
    return file_list

def download_file(file_id, file_title, destination):
    drive = get_drive()
    file_drive = drive.CreateFile({'id': file_id})
    try:
        file_drive.GetContentFile(os.path.join(destination, file_title))
        log_publish(f"[drive] Downloaded: {os.path.join(destination, file_title)}")
    except Exception as e:
        log_publish(f"[drive] ERROR downloading file id={file_id} title={file_title} error={str(e)}")
        raise e

def upload_to_drive(file_path, folder_id):
    file_name = os.path.basename(file_path)
    drive = get_drive()
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    print(f"Uploaded: {file_name} to Google Drive (Folder ID: {folder_id})")
    
    
def get_image_file(folder_id):
    drive = get_drive()
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        title = file.get('title', '')
        if title.endswith(('.jpg', '.jpeg', '.png')):
            log_publish(f"[drive] Found image file: {file.get('title', '<unknown>')} id={file.get('id','<unknown>')}")
            file_id = file['id']
            file_drive = drive.CreateFile({'id': file_id})
            file_drive.GetContentFile(os.path.join(LOCAL_COMBINED_PATH, title))
            return file
    log_publish(f"[drive] No image file found in folder {folder_id}")
    return None