from moviepy.editor import *
import os


def create_video(text, audio_path, video_path, word_timings):
    audio = AudioFileClip(audio_path)

    # Create a background clip
    background = ColorClip(size=(640, 480), color=(0, 0, 0))
    background = background.set_duration(audio.duration)

    clips = []

    for timing in word_timings:
        word = timing['word']
        start_time = timing['start']
        duration = timing['end'] - timing['start']

        # Create text clip
        text_clip = TextClip(
            word,
            fontsize=70,
            color='white',
            size=(640, 480),
            method='caption',
            font='Arial'  # Ensure 'Arial' font is available on your system
        )
        text_clip = (
            text_clip.set_start(start_time)
            .set_duration(duration)
            .set_pos('center')
        )
        clips.append(text_clip)

    # Combine background and text clips
    video = CompositeVideoClip([background] + clips)

    video = video.set_audio(audio)

    # Write the final video file
    video.write_videofile(video_path, fps=24, audio_codec='aac')

    # Close all clips
    video.close()
    audio.close()
