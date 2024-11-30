
from audio_synthesis import text_to_audio
from video_creation import create_video
from speech_recognition import get_word_timings
from pydub import AudioSegment
import os

def main():
    # Ensure the results directory exists
    os.makedirs('results', exist_ok=True)

    text = "Hello, how are you doing today?"
    audio_path = "results/output_audio.wav"  # Ensure it's a WAV file
    video_path = "results/output_video.mp4"
    model_path = "models/vosk-model-small-en-us-0.15"
    # Create audio from text
    text_to_audio(text, audio_path)

    # Verify audio duration
    audio = AudioSegment.from_file(audio_path)
    print(f"Generated audio duration: {audio.duration_seconds} seconds")

    # Get word timings using Vosk
    word_timings = get_word_timings(audio_path, model_path)

    # Create video with synchronized text
    create_video(text, audio_path, video_path, word_timings)

if __name__ == "__main__":
    main()