from df.enhance import enhance, init_df, load_audio, save_audio
from df.utils import download_file
import torch
import torchaudio
from config import LOCAL_SANITIZED_PATH, LOCAL_NOISE_REDUCED_PATH, LOCAL_CHUNKED_PATH
import os
import gc
from logger import log_publish

model = None
df_state = None

def get_model():
    global model, df_state
    if model is None:
        model, df_state, _ = init_df()

    return model, df_state

def get_chunks(file_path):
    file_name = os.path.basename(file_path)
    chunked_file_prefix = file_name.replace('.wav', '_chunk_')
    chunk_files = []
    for f in os.listdir(LOCAL_CHUNKED_PATH):
        if f.startswith(chunked_file_prefix) and f.endswith('.wav'):
            chunk_files.append(os.path.join(LOCAL_CHUNKED_PATH, f))
    return chunk_files 

def transform_audio(file_path, batch_id): 
    model, df_state = get_model()
    file_path = os.path.join(LOCAL_SANITIZED_PATH, file_path)
    chunk_list = get_chunks(file_path)
    noise_reduced_chunk_list = []
    for chunk in chunk_list:
        log_publish(f"[noise_reduce] START chunk={chunk}")
        audio, _ = load_audio(chunk, sr=df_state.sr())
        noise_reduced = chunk.replace(LOCAL_CHUNKED_PATH, LOCAL_NOISE_REDUCED_PATH)
        enhanced = enhance(model, df_state, audio)
        save_audio(noise_reduced, enhanced, df_state.sr())
        noise_reduced_chunk_list.append(noise_reduced)
        log_publish(f"[noise_reduce] DONE noise_reduced={noise_reduced}")
    return noise_reduced_chunk_list
