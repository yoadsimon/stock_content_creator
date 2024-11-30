from moviepy.editor import *
import pygame
import os
import string

def create_video(text, audio_path, video_path):
    words = text.split()
    # Clean words by removing punctuation for accurate length measurement
    cleaned_words = [word.strip(string.punctuation) for word in words]
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # Estimate duration for each word based on word length
    estimated_durations = [len(word) for word in cleaned_words]
    total_estimated_duration = sum(estimated_durations)

    # Calculate scaling factor to match total audio duration
    scaling_factor = audio_duration / total_estimated_duration

    # Calculate actual duration for each word
    word_durations = [duration * scaling_factor for duration in estimated_durations]

    clips = []

    for i, word in enumerate(words):
        duration = word_durations[i]
        text_clip = TextClip(word, fontsize=70, color='white', size=(640, 480), method='caption')
        text_clip = (
            text_clip.on_color(size=(640, 480), color=(0, 0, 0))
            .set_duration(duration)
            .set_pos('center')
        )
        clips.append(text_clip)

    # Concatenate all the text clips
    concat_clip = concatenate_videoclips(clips, method='compose')

    # Set the audio
    concat_clip = concat_clip.set_audio(audio)

    # Write the final video file
    concat_clip.write_videofile(video_path, fps=24, audio_codec='aac')

    # Close all clips
    for clip in clips:
        clip.close()
    concat_clip.close()
    audio.close()