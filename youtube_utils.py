#!/usr/bin/env python3

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from logger import log_publish as log
from config import LOCAL_COMBINED_PATH


def get_youtube_service(credentials_file='client_secrets.json', token_file='token.pickle', log_publish=log):
    """
    Get YouTube service - sends auth URL to Discord if needed
    
    Args:
        credentials_file (str): OAuth credentials file 
        token_file (str): Where to save the auth token
        log_publish (function): Discord webhook function (only for auth URL)
        
    Returns:
        YouTube API service object or None if auth needed
    """
    scopes = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/youtube'
    ]
    creds = None
    
    # Load existing token
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Check if we need new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Auto-refresh expired token
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        else:
            # Need new auth - send URL to Discord
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            
            # Try different redirect methods
            try:
                # Method 1: Out-of-band (classic)
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                auth_url, _ = flow.authorization_url(
                    access_type='offline',
                    prompt='consent',
                    include_granted_scopes='true'
                )
            except:
                # Method 2: Localhost fallback
                try:
                    auth_url, _ = flow.authorization_url(
                        access_type='offline', 
                        prompt='consent'
                    )
                except Exception as e:
                    if log_publish:
                        log_publish(f"❌ **OAuth Setup Error**\n```{str(e)}```\n\nCheck Google Cloud Console setup!")
                    return None
            
            if log_publish:
                auth_message = f"""🎬 **YouTube Brand Channel Authentication**

**Important:** Make sure you're logged into the Google account that manages your brand channel!

**Setup Check:**
1. ✅ OAuth client type = "Desktop Application" 
2. ✅ YouTube Data API v3 enabled
3. ✅ OAuth consent screen configured

**Authorization:**
Click this link: {auth_url}

⚠️ **During authorization, you'll be asked to select which channel to use. Choose your BRAND CHANNEL, not your personal channel!**

After clicking "Allow", you'll get a code. Use:
`complete_youtube_auth('YOUR_CODE_HERE')`"""
                log_publish(auth_message)
            
            return None  # Auth required
    
    return build('youtube', 'v3', credentials=creds)


def complete_youtube_auth(auth_code, credentials_file='client_secrets.json', token_file='token.pickle'):
    """
    Complete authentication with code from user
    
    Args:
        auth_code (str): Authorization code from Google
        
    Returns:
        bool: True if successful
    """
    try:
        scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube'
        ]
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
        
        # Try both redirect methods
        try:
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            flow.fetch_token(code=auth_code.strip())
        except:
            # Fallback method
            flow.fetch_token(code=auth_code.strip())
            
        creds = flow.credentials
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        # Test credentials and show which channel is selected
        youtube = build('youtube', 'v3', credentials=creds)
        channels = youtube.channels().list(part='snippet', mine=True).execute()
        
        if channels.get('items'):
            channel = channels['items'][0]
            log(f"✅ Authenticated successfully!")
            log(f"🎬 Selected Channel: {channel['snippet']['title']}")
            log(f"📺 Channel ID: {channel['id']}")
            return True
        else:
            log("❌ No YouTube channel found")
            return False
        
    except Exception as e:
        log(f"Auth completion error: {e}")
        return False


def upload_video(video_file, title, description="", tags=None, privacy_status="public", log_publish=log):
    """
    Upload video to YouTube
    
    Args:
        video_file (str): Path to video file
        title (str): Video title
        description (str): Video description
        tags (list): Video tags
        privacy_status (str): private, unlisted, or public
        log_publish (function): Only used for auth URL if needed
        
    Returns:
        str: Video ID if successful, None if failed or auth needed
    """
    if not os.path.exists(video_file):
        return None
    
    youtube = get_youtube_service(log_publish=log)
    if not youtube:
        return None  # Authentication needed
    
    if tags is None:
        tags = []
    log(f"Uploading video: {title}")
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/*')
    
    try:
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                log(f"Upload progress: {progress}%")
        
        return response.get('id')
        
    except Exception as e:
        log(f"Upload error: {e}")
        return None


def upload_thumbnail(video_id, thumbnail_file):
    """Upload thumbnail for video"""
    if not os.path.exists(thumbnail_file):
        return False
    log(f"Updating Thumbnail")
    try:
        youtube = get_youtube_service(log_publish=log)
        if not youtube:
            return False
            
        media = MediaFileUpload(thumbnail_file, mimetype='image/jpeg')
        youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
        log(f"Thumbnail updated")
        return True
        
    except Exception as e:
        log(f"Thumbnail error: {e}")
        return False

def is_youtube_authenticated():
    """Check if YouTube is authenticated and ready"""
    try:
        youtube = get_youtube_service()
        return youtube is not None
    except:
        return False

# Example usage in your pipeline
def handle_youtube_flow(videoname):
    
    # Check if authenticated
    if not is_youtube_authenticated():
        upload_video("dummy.mp4", "test", log_publish=log)
        return
     
    VIDEO_PATH = os.path.join(LOCAL_COMBINED_PATH, 'silenced.mp4')
    # get any image file (png,jpg,jpeg) from combined path using glob
    
    image_files = [f for f in os.listdir(LOCAL_COMBINED_PATH) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if image_files:
        IMAGE_PATH = os.path.join(LOCAL_COMBINED_PATH, image_files[0])
    else:
        IMAGE_PATH = None  # No image available
     
    video_id = upload_video(VIDEO_PATH, videoname)
    log(f"Video uploaded: https://www.youtube.com/watch?v={video_id}" if video_id else "Video upload failed")
    if video_id and IMAGE_PATH:
        success = upload_thumbnail(video_id, IMAGE_PATH)
        if not success:
            log("Thumbnail upload failed")


def get_video_info(video_id):
    """Get video information"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
            
        response = youtube.videos().list(
            part='snippet,status,statistics',
            id=video_id
        ).execute()
        
        if response['items']:
            video = response['items'][0]
            return {
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'published_at': video['snippet']['publishedAt'],
                'privacy_status': video['status']['privacyStatus'],
                'view_count': video.get('statistics', {}).get('viewCount', 0),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
        return None
        
    except Exception as e:
        log(f"Get video info error: {e}")
        return None


def update_video(video_id, title=None, description=None, tags=None, privacy_status=None):
    """Update video metadata"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return False
        
        response = youtube.videos().list(part='snippet,status', id=video_id).execute()
        if not response['items']:
            return False
        
        video = response['items'][0]
        
        if title is not None:
            video['snippet']['title'] = title
        if description is not None:
            video['snippet']['description'] = description
        if tags is not None:
            video['snippet']['tags'] = tags
        if privacy_status is not None:
            video['status']['privacyStatus'] = privacy_status
        
        youtube.videos().update(part='snippet,status', body=video).execute()
        return True
        
    except Exception as e:
        log(f"Update video error: {e}")
        return False


def is_youtube_authenticated():
    """Check if YouTube is authenticated and ready"""
    try:
        youtube = get_youtube_service()
        return youtube is not None
    except:
        return False


def get_all_channels():
    """Get all channels you have access to (personal + brand channels)"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
            
        channels = youtube.channels().list(part='snippet', mine=True).execute()
        
        channel_list = []
        for channel in channels.get('items', []):
            channel_list.append({
                'name': channel['snippet']['title'],
                'id': channel['id'],
                'description': channel['snippet'].get('description', ''),
                'custom_url': channel['snippet'].get('customUrl', 'N/A')
            })
        
        return channel_list
        
    except Exception as e:
        log(f"Get channels error: {e}")
        return None


def get_channel_info():
    """Get currently authenticated channel information"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
            
        channels = youtube.channels().list(part='snippet', mine=True).execute()
        if channels['items']:
            channel = channels['items'][0]
            return {
                'name': channel['snippet']['title'],
                'id': channel['id'],
                'description': channel['snippet'].get('description', ''),
                'custom_url': channel['snippet'].get('customUrl', 'N/A'),
                'is_brand_channel': 'brand' in channel['snippet']['title'].lower() or len(channels['items']) == 1
            }
        return None
        
    except Exception as e:
        log(f"Get channel info error: {e}")
        return None

