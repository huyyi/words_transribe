import os
from pathlib import Path
import sys
from typing import List
from google.cloud import speech
import io
import os.path as osp
from tqdm import tqdm
from utils import read_config
import csv

configs = read_config()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = osp.abspath(configs['google_ca_dir'])



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

def trans_word(word_file: str) -> List[str]:
    client = speech.SpeechClient()
    with io.open(word_file, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ja-jp"    
        )
    response = client.recognize(config=config, audio=audio)

    print("%d个结果：" % len(response.results))
    for result in response.results:
        print(u"结果 {}".format(result.alternatives[0].transcript))
    return [x.alternatives[0].transcript for x in response.results]


if __name__ == "__main__":
    word_list = os.listdir(Path(r'wav\word'))
    fieldnames = ['name', 'res']
    os.system('cls')
    if not osp.exists('bad_word.txt'): 
        f = open('bad_word.txt', 'w', encoding='utf-8')
        f.close()
        bad_word = []
    else:
        with open('bad_word.txt', 'r', encoding='utf-8') as f:
            bad_word = f.readlines()

    if not osp.exists('result.csv'): 
        f = open('result.csv', 'w', encoding='utf-8', newline='')
        f.close()
        finished = []
    else:
        with open('result.csv', 'r', encoding='utf-8', newline='') as res_file:
            reader = csv.DictReader(res_file, fieldnames=fieldnames)
            finished = [x['name'] for x in reader]
        
    
    with open('result.csv', 'a+', encoding='utf-8', newline='') as results_file, \
        open('bad_word.txt', 'a+', encoding='utf-8') as bad_word_file:
        writer = csv.DictWriter(results_file, fieldnames=fieldnames)

        for word in tqdm(word_list, desc='转录进度', total=len(word_list), ncols=80):
            print('\n处理文件%s' % word, end=': ')
            if word in finished or word in bad_word:
                print('跳过')
                continue
            try:
                res = trans_word(osp.join(Path(r'wav\word'), word))
                print("转录成功！\n结果：%s" % str(res))
                writer.writerow({'name':word, 'res':res})
                finished.append(word)
            except KeyboardInterrupt:
                break
            except:
                print('\n转录失败')
                bad_word.append(word)
                bad_word_file.write(word)
            os.system('cls')