from audio_synthesis import text_to_audio
from video_creation import create_video
from pydub import AudioSegment


def main():
    text = "Hello Melina, I made this video for you. I hope you like it."
    audio_path = "results/output_audio.wav"  # Update extension to .wav
    video_path = "results/output_video.mp4"

    # Create audio from text
    text_to_audio(text, audio_path)

    # Verify audio duration
    audio = AudioSegment.from_file(audio_path)
    print(f"Generated audio duration: {audio.duration_seconds} seconds")

    # Create video with synchronized text
    create_video(text, audio_path, video_path)


if __name__ == "__main__":
    main()
