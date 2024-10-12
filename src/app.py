import os 
import streamlit as st 
from moviepy.editor import AudioClip
from dotenv import load_dotenv
from groq import Groq 
from podcast.speech_to_text import audio_to_text
from podcast.embedding import store_embeddings
from podcast.question_answer import query_vector_database,transcript_chat_completion
from langchain.docstore.document import Document


# load the environment variables from .env file 
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

#ENSURE THE API_KEY IS LOADED 
if API_KEY is None:
    st.error("API KEY not found . please set the GROQ API KEY in your .env file .")
    st.stop()
    
    
# initialize the Groq Client 
client = Groq(api_key=API_KEY)


# ensure output directories exist 
mp3_file_folder = "uploaded_file"
mp3_chunk_folder = "chunks"

os.makedirs(mp3_file_folder,exist_ok=True)
os.makedirs(mp3_chunk_folder,exist_ok=True)

st.title("podcast Q&A App")

# upload audio file
uploaded_file=st.file_uploader("Upload an MP3 file", type="mp3")

# session state to store the last processed file to avoid reprocessing 
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None
if "transcriptions" not in st.session_state:
    st.session_state.transcriptions = []
    
if "docsearch" not in st.session_state:
    st.session_state.docsearch = None
    
    
# when a new file is uploaded , reset the session state for transcriptions and embeddings 
if uploaded_file is not None:
    # check if the new file is different from the last processed files 
    if uploaded_file.name != st.session_state.last_uploaded_file:
        st.session_state.transcriptions = []
        st.session_state.docsearch = None
        st.session_state.last_uploaded_file = uploaded_file.name
        
        
    # save the uploaded file 
    filepath = os.path.join(mp3_chunk_folder,uploaded_file.name)
    with open(filepath , "wb") as f :
        f.write(uploaded_file.getbuffer())
        
    # optional : To save and chunk the audio file 
    audio = AudioClip(filepath)
    chunk_length = 60 
    
    # process and trancribe each chunk only if not already done 
    if not st.session_state.transcriptions:
        for start in range(0,int(audio.duration),chunk_length):
            end = min(start + chunk_length, int(audio.duration))
            audio_chunk = audio.subclip(start,end)
            chunk_filename = os.path.join(mp3_chunk_folder,f"chunk_{start}.mp3")
            audio_chunk.write_audiofile(chunk_filename)
            
            # process and transcribe each chunk using groq
            transcription = audio_to_text(chunk_filename)
            st.session_state.transcriptions.append(transcription)
            
        # combine all transcribe each chunk using Groq
        combined_transcription = " ".join(st.session_state.transcriptions)
        st.write(f"Transcription : {combined_transcription[:500]}...") # show the first 500 charactors
        
        # Generate embeddings and store in pinecone 
        documents = [Document(page_content=combined_transcription)]
        st.session_state.docsearch = store_embeddings(documents)
        
        
# user query 
user_question = st.text_input("Ask a question about the podcast")
if user_question and st.session_state.docsearch:
    relevant_transcripts= query_vector_database(st.session_state.docsearch , user_question)
    response = transcript_chat_completion(client,relevant_transcripts,user_question)
    st.write(f"Response : {response}")