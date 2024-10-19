import streamlit as st
from google.cloud import speech
from google.cloud import texttospeech
import openai
import moviepy.editor as mp


# Creating the Streamlit Web App
st.title('Video Audio Replacement')

# Upload video file
uploaded_video = st.file_uploader("Upload a video file", type=["mp4"])



#Extracting Audio
if uploaded_video:
    video = mp.VideoFileClip(uploaded_video.name)
    audio = video.audio

    # Transcribe the audio using Google Speech-to-Text API
    client = speech.SpeechClient()
    audio_content = audio.to_soundarray().tobytes()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )
    response = client.recognize(config=config, audio=audio)
    transcript = ''.join([result.alternatives[0].transcript for result in response.results])


#Correcting the Transcription
    # Correct the transcription using GPT-4
    openai.api_key = '22ec84421ec24230a3638d1b51e3a7d'
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=f"Correct the following transcription: {transcript}",
        max_tokens=1000
    )
    corrected_transcript = response.choices[0].text.strip()

#Generating AI Voice
    #Convert corrected text to speech using Google Text-to-Speech
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=corrected_transcript)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Journey"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

#Syncing and Replacing Audio
    output_audio_path = "output_audio.wav"
    with open(output_audio_path, "wb") as out:
        out.write(response.audio_content)
    
    final_video = video.set_audio(mp.AudioFileClip(output_audio_path))
    final_video.write_videofile("final_output.mp4")

    st.video("final_output.mp4")