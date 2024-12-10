import boto3
import os
from dotenv import load_dotenv

load_dotenv()


def text_to_audio(text, audio_path="results/output_audio.mp3", wav_audio_path="results/output_audio.wav"):
    polly_client = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    ).client('polly')

    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Gregory',
        Engine='neural',
        # TextType='ssml'
    )

    if "AudioStream" in response:
        with open(audio_path, 'wb') as file:
            file.write(response['AudioStream'].read())
    else:
        raise Exception("Could not stream audio")

    from pydub import AudioSegment
    audio_segment = AudioSegment.from_mp3(audio_path)
    audio_segment.export(wav_audio_path, format="wav")


# if __name__ == "__main__":
#     text_with_ssml = ""
#     text_to_audio(text_with_ssml)
