import random
from moviepy.editor import AudioFileClip, VideoFileClip, TextClip, concatenate_videoclips, CompositeVideoClip


def load_audio(audio_path):
    return AudioFileClip(audio_path)


def match_text_part_to_sentence(text_part, sentences_timings):
    sentence = None
    for s in sentences_timings:
        if s['sentence'].strip().lower().replace("*", "").replace('"', "'") == \
                text_part.strip().lower().replace("*", "").replace('"', "'"):
            sentence = s
            break  # Exit the loop once a match is found
    if not sentence:
        return None, None
    next_sentence = None
    sentences_timings = sorted(sentences_timings, key=lambda x: x['start'])
    for s in sentences_timings:
        if s['start'] is not None and s['start'] > sentence['start']:
            next_sentence = s
            break
    return sentence, next_sentence


def load_background_clips(background_videos, total_audio_duration, part_of_text_map, sentences_timings):
    if background_videos is None:
        return None, []  # Return an empty list for bg_videos

    background_clips = []
    bg_videos = []  # List to keep references to bg_video instances
    current_duration = 0

    # Iterate over each text segment and its corresponding video from the map
    for text_part, video_name in part_of_text_map.items():
        if current_duration >= total_audio_duration:
            break

        # Use the specific video file for the text segment
        file_name = f"inputs/{video_name}"
        # print(f"Attempting to load video: {file_name}")
        try:
            bg_video = VideoFileClip(file_name)
            bg_videos.append(bg_video)  # Keep a reference to prevent premature closing
        except Exception as e:
            print(f"Error loading video '{file_name}': {e}")
            continue

        if bg_video.reader is None:
            print(f"Video reader is None for video '{file_name}'. Skipping.")
            continue

        sentence, next_sentence = match_text_part_to_sentence(text_part, sentences_timings)
        if sentence is None:
            print(f"Could not find a matching sentence for text part: {text_part}")
            continue  # Do not close bg_video here

        start_time = sentence['start']

        if next_sentence is not None:
            clip_duration = next_sentence['start'] - start_time
        else:
            clip_duration = sentence['end'] - start_time

        video_duration = bg_video.duration

        if clip_duration > video_duration:
            print(f"Clip duration is greater than video duration for video '{file_name}'")
            clip_duration = video_duration

        if clip_duration <= 0:
            print(f"Clip duration is non-positive after adjustments for text part: {text_part}")
            continue  # Do not close bg_video here

        # Create the subclip with adjusted timings
        bg_clip = bg_video.subclip(0, clip_duration)
        bg_clip = bg_clip.resize((640, 480))
        background_clips.append(bg_clip)
        current_duration += clip_duration
        # Do not close bg_video here; it is needed by bg_clip

    # Repeat background video to fill remaining duration
    while current_duration < total_audio_duration:
        file_name = f"inputs/Interactive_Trading_Screen.mp4"
        print(f"Attempting to load video: {file_name}")
        try:
            bg_video = VideoFileClip(file_name)
            bg_videos.append(bg_video)  # Keep a reference to prevent premature closing
        except Exception as e:
            print(f"Error loading video '{file_name}': {e}")
            break

        if bg_video.reader is None:
            print(f"Video reader is None for video '{file_name}'. Exiting loop.")
            break

        clip_duration = min(bg_video.duration, total_audio_duration - current_duration)
        bg_clip = bg_video.subclip(0, clip_duration)
        bg_clip = bg_clip.resize((640, 480))
        background_clips.append(bg_clip)
        current_duration += clip_duration
        # Do not close bg_video here; it is needed by bg_clip

    if background_clips:
        try:
            concatenated_background = concatenate_videoclips(background_clips)
        except Exception as e:
            print(f"Error concatenating video clips: {e}")
            # Do not close bg_videos here
            return None, bg_videos  # Return bg_videos
        # Do not close bg_videos yet
        return concatenated_background, bg_videos
    else:
        # Do not close bg_videos yet
        return None, bg_videos


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


def create_video(audio_path, video_path, word_timings, background_videos, part_of_text_map, sentences_timings):
    audio = load_audio(audio_path)
    total_audio_duration = audio.duration

    background, bg_videos = load_background_clips(background_videos=background_videos,
                                                  total_audio_duration=total_audio_duration,
                                                  part_of_text_map=part_of_text_map,
                                                  sentences_timings=sentences_timings)

    clips = generate_text_clips(word_timings)

    video = CompositeVideoClip([background] + clips) if background else CompositeVideoClip(clips)
    video = video.set_audio(audio)
    video.write_videofile(video_path, fps=24, audio_codec='aac')

    # Close resources
    video.close()
    audio.close()
    for bg_video in bg_videos:
        bg_video.close()

# def get_random_clip_timing(bg_video, remaining_duration):
#     min_clip_duration = 3
#     max_clip_duration = 7
#     available_duration = bg_video.duration
#
#     effective_min_duration = min(min_clip_duration, available_duration)
#     effective_max_duration = min(max_clip_duration, available_duration)
#
#     max_start_time = max(0, available_duration - effective_min_duration)
#     start_time = random.uniform(0, max_start_time)
#     max_possible_duration = available_duration - start_time
#     clip_max_duration = min(effective_max_duration, max_possible_duration)
#
#     clip_min_duration = min(effective_min_duration, clip_max_duration)
#     clip_duration = random.uniform(clip_min_duration, clip_max_duration)
#
#     return start_time, clip_duration
