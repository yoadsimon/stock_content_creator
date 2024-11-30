from gtts import gTTS
from pydub import AudioSegment
import os

def text_to_audio(text, file_path):
    tts = gTTS(text=text, lang='en')
    temp_mp3_path = 'temp_audio.mp3'
    tts.save(temp_mp3_path)

    # Convert MP3 to WAV
    sound = AudioSegment.from_mp3(temp_mp3_path)
    sound.export(file_path, format='wav')
    os.remove(temp_mp3_path)