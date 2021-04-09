from pydub import AudioSegment
from pydub.silence import split_on_silence
import pickle
import os
from os import path as osp
from tqdm import tqdm
from multiprocessing import Process

pickle_dir = 'pickle'
audio_dir = 'source_audios'

cre_dir = os.path.join('D:\Projects\words_audio', 'speech2text-307412-4fbc2f5d8a92.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cre_dir
os.environ['https_proxy'] = 'http://localhost:7890'
os.environ['http_proxy'] = 'http://localhost:7890'
# os.environ['GRPC_VERBOSITY'] = 'DEBUG'
# os.environ['GRPC_TRACE'] = "handshaker"

def cuts_dura(cuts):
    duration = [len(x) for x in cuts]
    for i in range(len(cuts)):
        print(i, ':', duration[i])

def find_word(cuts):
    words = []
    drop_words = []
    total_bipe = 0
    word = []
    for cut in cuts:
        if abs(len(cut) - 2339) <= 5:
            total_bipe += 1
            if len(word) < 2 or abs(len(word[0]) - len(word[1])) >= 100:
                drop_words.append(word.copy())
            else:
                words.append(word[1:])
            word.clear()
        else:
            word.append(cut)
    return words, drop_words
    
def split_cuts(cuts):
    all_words = []
    word = []
    for cut in cuts:
        dura = len(cut)
        if abs(dura - 2339) <= 5:
            all_words.append(word.copy())
            word.clear()
        else:
            word.append(cut)
    return all_words

def remove_dup(words):
    for word in words:
        if abs(len(word[0]) - len(word[1])) <= 5:
            del word[0]
    return 0

def get_cuts():
    file_list = os.listdir(audio_dir)
    for file in tqdm(file_list):
        if osp.exists(osp.join(pickle_dir, file[:-4])):
            print("文件已处理，跳过")
            continue
        print("处理文件：", file)
        p = Process(target=read_file, args=(file,))
        print("开启进程")
        p.start()
    return 0

def read_file(file):
    """读mp3文件根据静音拆分成片段保存为pickle

    Args:
        file (string): 文件名
    """    
    print("开始处理文件")
    audio = AudioSegment.from_mp3(osp.join(audio_dir, file))
    cuts = split_on_silence(audio, silence_thresh=-50)
    with open(osp.join(pickle_dir, file[:-4]), 'wb') as f:
        pickle.dump(cuts, f)
    return 0

def read_pickle(pickle_dir):
    with open(pickle_dir, 'rb') as f:
        cuts = pickle.load(f)
    return cuts

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    import io

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ja-jp"
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))


if __name__ == "__main__":
    get_cuts()
    # words = read_pickle('pickle\あ-1')