import random
from moviepy.editor import AudioFileClip, VideoFileClip, TextClip, concatenate_videoclips, CompositeVideoClip


def load_audio(audio_path):
    return AudioFileClip(audio_path)


def load_background_clips(background_videos, total_audio_duration):
    if background_videos is None:
        return None
    background_clips = []
    current_duration = 0

    while current_duration < total_audio_duration:
        bg_video_path = random.choice(background_videos)
        bg_video = VideoFileClip(bg_video_path)

        if bg_video.duration < 0.5:
            bg_video.close()
            continue

        start_time, clip_duration = get_random_clip_timing(bg_video, total_audio_duration - current_duration)

        if clip_duration < 0.5:
            bg_video.close()
            continue

        bg_clip = bg_video.subclip(start_time, start_time + clip_duration)
        bg_clip = bg_clip.resize((640, 480))
        background_clips.append(bg_clip)
        current_duration += clip_duration

    return concatenate_videoclips(background_clips) if background_clips else None


def get_random_clip_timing(bg_video, remaining_duration):
    min_clip_duration = 3
    max_clip_duration = 7
    available_duration = bg_video.duration

    effective_min_duration = min(min_clip_duration, available_duration)
    effective_max_duration = min(max_clip_duration, available_duration)

    max_start_time = max(0, available_duration - effective_min_duration)
    start_time = random.uniform(0, max_start_time)
    max_possible_duration = available_duration - start_time
    clip_max_duration = min(effective_max_duration, max_possible_duration)

    clip_min_duration = min(effective_min_duration, clip_max_duration)
    clip_duration = random.uniform(clip_min_duration, clip_max_duration)

    return start_time, clip_duration


def generate_text_clips(word_timings):
    clips = []
    for timing in word_timings:
        word = timing['word']
        start_time = timing['start']
        duration = timing['end'] - timing['start']
        text_clip = TextClip(word, fontsize=70, color='white', size=(640, 480), method='caption', font='Arial')
        text_clip = (text_clip.set_start(start_time)
                     .set_duration(duration)
                     .set_pos('center'))
        clips.append(text_clip)
    return clips


def create_video(audio_path, video_path, word_timings, background_videos):
    audio = load_audio(audio_path)
    total_audio_duration = audio.duration
    background = load_background_clips(background_videos, total_audio_duration)

    clips = generate_text_clips(word_timings)

    video = CompositeVideoClip([background] + clips) if background else CompositeVideoClip(clips)
    video = video.set_audio(audio)
    video.write_videofile(video_path, fps=24, audio_codec='aac', verbose=False, logger=None,
                          ffmpeg_params=['-loglevel', 'quiet'])

    video.close()
    audio.close()