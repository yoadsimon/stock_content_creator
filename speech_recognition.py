import os
import json
from vosk import Model, KaldiRecognizer
import wave


def get_word_timings(audio_path, model_path):
    # Load the Vosk model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    model = Model(model_path)

    # Open the audio file
    wf = wave.open(audio_path, "rb")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        # Convert audio to mono WAV format
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

    # Get the final partial result
    final_result = json.loads(rec.FinalResult())
    if 'result' in final_result:
        word_timings.extend(final_result['result'])

    # Close the audio file
    wf.close()

    # Extract word timings
    words = []
    for w in word_timings:
        words.append({
            'word': w['word'],
            'start': w['start'],
            'end': w['end']
        })

    return words