from moviepy.editor import AudioFileClip
import os 


def split_audio(mp3_file_folder,mp3_chunck_folder):
    # ensure the chunk folder exists
    os.makedirs(mp3_chunck_folder,exist_ok=True)
    
    # process each audio file in the folder 
    for file_name in os.listdir(mp3_file_folder):
        if file_name.endswith(".mp3"):
            print(f"Splitting Episode ID : {file_name}")
            
            
            # Load the audio file using Moviepy
            audio_path = os.path.listdir(mp3_file_folder,file_name)
            audio_clip = AudioFileClip(audio_path)
            
            # define chunk duration (eg . 30 seconds)
            chunk_duration = 30 
            duration = int(audio_clip.duration)
            start_time = 0
            
            ## split audio into chunks 
            while start_time < duration:
                end_time = min(start_time+chunk_duration,duration)
                chunk = audio_clip.subclip(start_time, end_time)
                
                
                
                # save the chunk 
                chunk_file_name = f"{file_name[:-4]}_chunk_{start_time}-{end_time}.mp3"
                chunk_file_path = os.path.join(mp3_chunck_folder, chunk_file_name)
                chunk.write_audiofile(chunk_file_path,codec="mp3")
                
                # update start time 
                start_time+=chunk_duration
                
            # close the audio file 
            audio_clip.close()
            