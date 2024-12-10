import datetime
import glob
import logging
import time
from audio_synthesis import text_to_audio
from create_content import create_content
from utils.consts import MARKET_TIME_ZONE
from utils.open_ai import match_text_to_video
from utils.utils import setup_logging
from video_creation import create_video
from speech_recognition import get_word_timings, get_sentences_timings
from pydub import AudioSegment
import os

setup_logging()


def check_part_of_text_map(part_of_text_map):
    for video_name in part_of_text_map.values():
        if not os.path.exists(f"inputs/{video_name}"):
            logging.error(f"Video {video_name} not found in inputs directory.")
    # open_one_by_one and check if the video is valid

    pass


def main():
    os.makedirs('results', exist_ok=True)

    logging.info("Starting the script.")

    now = datetime.datetime.now(MARKET_TIME_ZONE)
    mock_data_input_now = now.replace(hour=9, minute=0, second=0, microsecond=0)
    text = create_content(use_temp_file=True, mock_data_input_now=mock_data_input_now)
    # text = "Hi! My name is Gregory. I will read any text you type here."
    text = text.replace("*", "").replace('"', "'")
    part_of_text_map = {}
    for t in text.split('. '):
        part_of_text_map.update(match_text_to_video(t))
    check_part_of_text_map(part_of_text_map)
    audio_path = "results/output_audio.mp3"
    video_path = "results/output_video.mp4"
    wav_audio_path = "results/output_audio.wav"

    model_path = "models/vosk-model-small-en-us-0.15"
    background_videos_dir = "inputs"

    logging.info("Fetching list of background videos.")
    background_videos = glob.glob(os.path.join(background_videos_dir, "*.mp4"))
    background_videos = background_videos if background_videos else None
    logging.info("Converting text to audio...")
    start_time = time.time()
    text_to_audio(text, audio_path, wav_audio_path)

    logging.info(f"Text to audio conversion completed in {time.time() - start_time:.2f} seconds.")

    audio = AudioSegment.from_file(audio_path)
    logging.info(f"Generated audio duration: {audio.duration_seconds} seconds")

    logging.info("Analyzing audio for word timings...")
    start_time = time.time()
    word_timings = get_word_timings(wav_audio_path, model_path)
    sentences_timings = get_sentences_timings(wav_audio_path, model_path, sentences=list(part_of_text_map.keys()))
    logging.info(f"Word timings extraction completed in {time.time() - start_time:.2f} seconds.")

    logging.info("Creating video with text...")
    start_time = time.time()
    create_video(audio_path=audio_path,
                 video_path=video_path,
                 word_timings=word_timings,
                 part_of_text_map=part_of_text_map,
                 background_videos=background_videos,
                 sentences_timings=sentences_timings)
    logging.info(f"Video creation completed in {time.time() - start_time:.2f} seconds.")

    logging.info("Script finished successfully.")


if __name__ == "__main__":
    main()
