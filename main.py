import .utils
import .audio

#create a DriveAPI object
drive_api = utils.DriveAPI()
drive_api.clean_previous_files()



#run a loop here for each file downloaded from drive
noise_reducer = audio.NoiseReducer(story_name)

audio_merger = audio.AudioMerger(story_name)
audio_merger.