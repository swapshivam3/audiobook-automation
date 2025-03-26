import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

class DriveAPI:
    def __init__(self):
        load_dotenv()  # Load environment variables here
        self.SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
        self.FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
        self.DOWNLOAD_FOLDER = "downloaded_files"
        os.makedirs(self.DOWNLOAD_FOLDER, exist_ok=True)
        self.settings = {
            "client_config_backend": "service",
            "service_config": {
                "client_json_file_path": "service.json",
            },
        }
        self.gauth, self.drive = self.setup_auth()

    def setup_auth(self):
        gauth = GoogleAuth(settings=self.settings)
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)
        return gauth, drive

    def clean_previous_files(self):
        file_list = self.drive.ListFile({"q": f"'{self.FOLDER_ID}' in parents and trashed=false"}).GetList()
        for file in file_list:
            file.Trash()

    def delete_file(self, file_name):
        file_list_del = self.drive.ListFile({'q': f"title='{file_name}'"}).GetList()
        if file_list_del:
            file_id = file_list_del[0]['id']
            print(f"File ID: {file_id}")
            file = self.drive.CreateFile({'id': file_id})
            file.Delete()
            print(f"Deleted file: {file_id}")
        else:
            print("File not found.")

    def list_files(self):
        file_list = self.drive.ListFile({'q': f"'{self.FOLDER_ID}' in parents and trashed=false"}).GetList()
        files_in_drive = sorted(file_list, key=lambda x: x['title'])
        print("Available files in Google Drive:")
        for idx, file in enumerate(files_in_drive):
            print(f"{idx + 1}: {file['title']} (ID: {file['id']})")
        return files_in_drive

    def download_files(self, files_in_drive):
        downloaded_file_paths = []
        for file in files_in_drive:
            file_path = os.path.join(self.DOWNLOAD_FOLDER, file['title'])
            print(f"Downloading {file['title']}...")
            file.GetContentFile(file_path)
            downloaded_file_paths.append(file_path)
        print("\nDownload complete. Files are saved in:", self.DOWNLOAD_FOLDER)
        return downloaded_file_paths

    def transform_files(self, downloaded_file_paths):
        output_list = []
        for file_name in downloaded_file_paths:
            output_list.append(self.transform_audio(file_name))
        return output_list

    def transform_audio(self, file_name):
        # Placeholder for the actual transform_audio implementation
        pass

    def upload_to_drive(self, file_path):
        file_name = os.path.basename(file_path)
        file_drive = self.drive.CreateFile({'title': file_name, 'parents': [{'id': self.FOLDER_ID}]})
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        print(f"Uploaded: {file_name} to Google Drive (Folder ID: {self.FOLDER_ID})")


    #write a function to return list out all the folders in the folder
    def list_folders(self):
        folder_list = self.drive.ListFile({'q': f"'{self.FOLDER_ID}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"}).GetList()
        folders_in_drive = sorted(folder_list, key=lambda x: x['title'])
        print("Available folders in Google Drive:")
        for idx, folder in enumerate(folders_in_drive):
            print(f"{idx + 1}: {folder['title']} (ID: {folder['id']})")
        return folders_in_drive

    #write a function to list all the files in a folder 
    def list_files_in_folder(self, folder_id):
        file_list = self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        files_in_drive = sorted(file_list, key=lambda x: x['title'])
        print("Available files in Google Drive:")
        for idx, file in enumerate(files_in_drive):
            print(f"{idx + 1}: {file['title']} (ID: {file['id']})")
        return files_in_drive