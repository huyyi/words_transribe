import os
from pathlib import Path
from multiprocessing import Pool
from google.cloud import speech
import io
import os.path as osp
import pickle

wav_dir = Path('wav')
res_dir = Path('./res')
bad_log = Path('./bad_request.txt')
processed_log = Path('./processed.txt')
bad_request = []

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ja-jp",
        # enable_word_confidence=True
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))

def res_pickle() -> dict:
    if osp.exists(res_dir):
        with open(res_dir, 'rb') as f:
            res = pickle.load(f)
    return res

def transcribe(wav):
    client = speech.SpeechClient()

    with io.open(wav, 'rb') as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code='ja-jp'
    )

    response = client.recognize(config=config, audio=audio)

    try:
        result = [x.alternatives[0].transcript for x in response.results]
    except IndexError:
        bad_request.append(wav)
    return result

def trans_kana_sub(sub_path):
    kana_res = dict()
    wav_list = os.listdir(sub_path)
    for wav in wav_list:
        result = transcribe(osp.join(sub_path, wav))
        print("处理文件%s转录结果：%s" % (wav, result))
        kana_res[wav] = result
    return kana_res




def trans_all():
    kana_sub = os.listdir(wav_dir)
    pass

if __name__ == "__main__":
    pass
