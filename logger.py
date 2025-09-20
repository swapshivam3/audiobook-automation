from config import WEBHOOK_URL
import requests

def log_publish(message):    
    data = {
        "content": '`' + message + '`'
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"Failed to send message to Discord: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception occurred while sending message to Discord: {str(e)}")
    