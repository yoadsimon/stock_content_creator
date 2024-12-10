import os
import sys
import wave
import json
from vosk import Model, KaldiRecognizer
import contextlib
import difflib


@contextlib.contextmanager
def suppress_os_stdout_stderr():
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()

    saved_stdout_fd = os.dup(original_stdout_fd)
    saved_stderr_fd = os.dup(original_stderr_fd)

    devnull_fd = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull_fd, original_stdout_fd)
    os.dup2(devnull_fd, original_stderr_fd)
    os.close(devnull_fd)

    try:
        yield
    finally:

        os.dup2(saved_stdout_fd, original_stdout_fd)
        os.dup2(saved_stderr_fd, original_stderr_fd)
        os.close(saved_stdout_fd)
        os.close(saved_stderr_fd)


def get_word_timings(audio_path, model_path):
    with suppress_os_stdout_stderr():
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        model = Model(model_path)

        wf = wave.open(audio_path, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio file must be WAV format mono PCM.")

        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        word_timings = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'result' in result:
                    word_timings.extend(result['result'])

        final_result = json.loads(rec.FinalResult())
        if 'result' in final_result:
            word_timings.extend(final_result['result'])

        wf.close()

    words = [{'word': w['word'], 'start': w['start'], 'end': w['end']} for w in word_timings]
    return words


def get_sentences_timings(audio_path, model_path, sentences: list[str]):
    words = get_word_timings(audio_path, model_path)
    recognized_words = [w['word'].strip().lower().replace("*", "").replace('"', "'") for w in words]
    sentence_timings = []
    n = len(recognized_words)
    for sentence in sentences:
        sentence_words = sentence.strip().split()
        sentence_words = [w.strip().lower().replace("*", "").replace('"', "'") for w in sentence_words]
        m = len(sentence_words)
        max_mismatches = 9 # Allows for some mismatches
        best_ratio = 0
        best_start = None
        best_end = None
        # Adjust window sizes to account for insertions/deletions
        for window_size in range(m - max_mismatches, m + max_mismatches + 1):
            if window_size <= 0:
                continue
            for i in range(n - window_size + 1):
                window_words = recognized_words[i:i + window_size]
                # Compute matching ratio
                s = difflib.SequenceMatcher(None, sentence_words, window_words)
                ratio = s.ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_start = i
                    best_end = i + window_size - 1
        if best_ratio > 0.6:  # Threshold for accepting a match
            start_time = words[best_start]['start']
            end_time = words[best_end]['end']
            sentence_timings.append({
                'sentence': sentence,
                'start': start_time,
                'end': end_time
            })
        else:
            # Could not find a good match
            sentence_timings.append({
                'sentence': sentence,
                'start': None,
                'end': None
            })
    return sentence_timings
