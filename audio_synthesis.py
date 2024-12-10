import boto3
import os
import json
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()


def text_to_audio(
        text,
        audio_path="results/output_audio.mp3",
        wav_audio_path="results/output_audio.wav"
):
    polly_client = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    ).client('polly')

    response_audio = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Gregory',
        Engine='neural',
        # TextType='ssml'
    )

    if "AudioStream" in response_audio:
        with open(audio_path, 'wb') as file:
            file.write(response_audio['AudioStream'].read())
    else:
        raise Exception("Could not stream audio")

    audio_segment = AudioSegment.from_mp3(audio_path)
    audio_segment.export(wav_audio_path, format="wav")

    audio_duration_ms = len(audio_segment)

    response_marks = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='json',
        SpeechMarkTypes=['word', 'sentence'],
        VoiceId='Gregory',
        Engine='neural',
        # TextType='ssml'
    )

    if 'AudioStream' in response_marks:
        speech_marks_data = response_marks['AudioStream'].read().decode('utf-8').split('\n')
        speech_marks = []

        for mark in speech_marks_data:
            if mark.strip():
                speech_marks.append(json.loads(mark))

        list_of_sentences = []
        current_sentence = None
        current_words_in_sentence = []

        for i, mark in enumerate(speech_marks):
            if mark['type'] == 'sentence':

                if current_sentence is not None:

                    current_sentence['end'] = mark['time']

                    if current_words_in_sentence:
                        current_words_in_sentence[-1]['end'] = mark['time']
                    current_sentence['words_in_sentence'] = current_words_in_sentence
                    list_of_sentences.append(current_sentence)

                current_sentence = {
                    "sentence": mark['value'],
                    "start": mark['time'],

                }
                current_words_in_sentence = []
            elif mark['type'] == 'word':

                word_dict = {
                    "word": mark['value'],
                    "start": mark['time'],

                }

                if current_words_in_sentence:
                    current_words_in_sentence[-1]['end'] = mark['time']
                current_words_in_sentence.append(word_dict)

        if current_sentence is not None:

            if current_words_in_sentence:
                current_words_in_sentence[-1]['end'] = audio_duration_ms

            current_sentence['end'] = audio_duration_ms
            current_sentence['words_in_sentence'] = current_words_in_sentence
            list_of_sentences.append(current_sentence)

        return list_of_sentences

    else:
        raise Exception("Could not retrieve speech marks")

# Example usage
# if __name__ == "__main__":
#     text_input = "Today, NVIDIA Corporation's stock has faced a significant drop due to a newly launched antitrust investigation by Chinese regulators, casting uncertainty over potential anti-monopoly violations. The scrutiny is linked to NVIDIA's $6.9 billion acquisition of Mellanox Technologies, raising investor concerns amid heightened US-China tensions. Broader market trends also indicate a downturn, with major indices slipping as investors react to ongoing geopolitical and regulatory pressures. Meanwhile, despite competitive challenges and overall market declines, analysts highlight NVIDIA's strong position in the AI chip market, presenting a mixed sentiment for its future stock performance."
#     text_to_audio(text_input)