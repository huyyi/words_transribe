import os
from pathlib import Path
from multiprocessing import Pool
from google.cloud import speech
import io
import os.path as osp
import pickle
from utils import read_config

configs = read_config()


def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = osp.abspath(configs['google_ca_dir'])
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ja-jp",
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(u"Transcript: {}".format(result.alternatives[0].transcript))

if __name__ == "__main__":
    pass
