import os

from gtts import gTTS
from pydub import AudioSegment

def text_to_audio(text, file_path):
    tts = gTTS(text=text, lang='en')
    temp_mp3_path = 'temp_audio.mp3'
    tts.save(temp_mp3_path)

    # Convert MP3 to WAV PCM format
    sound = AudioSegment.from_mp3(temp_mp3_path)
    sound = sound.set_channels(1)  # Mono
    sound = sound.set_sample_width(2)  # 16-bit samples
    sound.export(file_path, format='wav')
    os.remove(temp_mp3_path)