import os
import sys
import wave
import json
from vosk import Model, KaldiRecognizer
import contextlib


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
