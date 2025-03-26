import os
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

class AudioMerger:
    def __init__(self, story_name):
        """
        Initialize the AudioMerger with the folder path and story name.
        Reminder: Pass the story_name which is scraped from the Google Drive folder.
        """
        self.combined_audio = AudioSegment.empty()
        self.timestamps = []
        self.current_time = 0
        self.OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER") + story_name

    def concat_wav_files(self, file_list):
        for file_name in file_list:
            audio = AudioSegment.from_wav(file_name)
            self.timestamps.append((file_name, self.current_time))
            self.combined_audio += audio
            self.current_time += len(audio)

        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
        output_filename = os.path.join(OUTPUT_FOLDER, 'combined.wav')
        self.combined_audio.export(output_filename, format="wav")

        print("\nTimestamps for each clip in the merged file:")
        for clip_name, timestamp in self.timestamps:
            minutes = timestamp // 60000
            seconds = (timestamp % 60000) // 1000
            print(f"{clip_name}: {minutes:02d}:{seconds:02d} minutes")

        return output_filename

