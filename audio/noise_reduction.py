import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from df.enhance import enhance, init_df, load_audio, save_audio
from df.utils import download_file
import torch
import torchaudio

class NoiseReducer:
    def __init__(self, story_name):
        self.model, self.df_state, _ = init_df()
        self.story_folder = os.path.join("output", "stories", os.path.basename(audio_file).split("_")[0])

    def transform_audio(self, audio_file):
        audio, _ = load_audio(audio_file, sr=self.df_state.sr())
        enhanced = enhance(self.model, self.df_state, audio)
        save_audio(audio_file.replace(".wav", "_reduced.wav"), enhanced, self.df_state.sr())
        os.makedirs(story_folder, exist_ok=True)
        output_file = os.path.join(story_folder, os.path.basename(audio_file).replace(".wav", "_output.wav"))
        save_audio(output_file, enhanced, self.df_state.sr())
        return output_file