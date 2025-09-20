import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
FOLDER_ID = os.getenv("FOLDER_ID")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
LOCAL_DOWNLOAD_PATH = os.getenv("LOCAL_DOWNLOAD_PATH", "/home/azureuser/podcat-processor/media/downloads/")
LOCAL_SANITIZED_PATH = os.getenv("LOCAL_SANITIZED_PATH", "/home/azureuser/podcat-processor/media/sanitized/")
LOCAL_NOISE_REDUCED_PATH = os.getenv("LOCAL_NOISE_REDUCED_PATH", "/home/azureuser/podcat-processor/media/noise_reduced/")
LOCAL_COMBINED_PATH = os.getenv("LOCAL_COMBINED_PATH", "/home/azureuser/podcat-processor/media/combined/")
WEBHOOK_URL=os.getenv("WEBHOOK_URL")
LOCAL_CHUNKED_PATH = os.getenv("LOCAL_CHUNKED_PATH", "/home/azureuser/podcat-processor/media/chunked/")