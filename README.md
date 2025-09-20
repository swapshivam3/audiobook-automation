# Podcast Processor Pipeline

## Features

* Supports downloading of audio files from Google Drive
* Automatically sanitizes audio files to remove silence
* Allows for manual re-noising of audio files to remove background noise
* Supports re-combining of trimmed audio files into a single video
* Supports uploading of processed videos to YouTube
* Supports restarting of system services for maintenance
* Supports checking of system logs for errors
* Supports automatic cleanup of old files

## System Requirements

* A Linux-based system
* A Redis server
* A RQ worker
* A YouTube account
* A Google account with OAuth 2 credentials
* The DeepFilter library for audio processing
* The FFMPEG library for video processing
