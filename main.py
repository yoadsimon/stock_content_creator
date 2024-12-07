import datetime
import glob
import logging
import time
from audio_synthesis import text_to_audio
from create_content import create_content
from utils.consts import MARKET_TIME_ZONE
from utils.utils import setup_logging
from video_creation import create_video
from speech_recognition import get_word_timings
from pydub import AudioSegment
import os

setup_logging()


def main():
    os.makedirs('results', exist_ok=True)

    logging.info("Starting the script.")

    now = datetime.datetime.now(MARKET_TIME_ZONE)
    mock_data_input_now = now.replace(hour=9, minute=0, second=0, microsecond=0)
    text = create_content(mock_data_input_now=mock_data_input_now)

    text = text.replace("*", "")
    audio_path = "results/output_audio.wav"
    video_path = "results/output_video.mp4"
    model_path = "models/vosk-model-small-en-us-0.15"
    background_videos_dir = "inputs"

    logging.info("Fetching list of background videos.")
    background_videos = glob.glob(os.path.join(background_videos_dir, "*.mp4"))

    logging.info("Converting text to audio...")
    start_time = time.time()
    text_to_audio(text, audio_path)
    logging.info(f"Text to audio conversion completed in {time.time() - start_time:.2f} seconds.")

    audio = AudioSegment.from_file(audio_path)
    logging.info(f"Generated audio duration: {audio.duration_seconds} seconds")

    logging.info("Analyzing audio for word timings...")
    start_time = time.time()
    word_timings = get_word_timings(audio_path, model_path)
    logging.info(f"Word timings extraction completed in {time.time() - start_time:.2f} seconds.")

    logging.info("Creating video with text...")
    start_time = time.time()
    create_video(audio_path, video_path, word_timings, background_videos)
    logging.info(f"Video creation completed in {time.time() - start_time:.2f} seconds.")

    logging.info("Script finished successfully.")


if __name__ == "__main__":
    main()
