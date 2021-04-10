import os
import os.path as osp
from pathlib import Path
import pickle
from typing import Dict, List
from utils import read_config
from pydub import AudioSegment
from multiprocessing import Pool
from tqdm import tqdm


configs = read_config()
wav_dir = Path(configs['wav_dir'])
pickle_dir = Path(configs['pickle_dir'])

if not osp.exists(wav_dir):
    os.mkdir(wav_dir)

def group_pickle(pickle_dir:str):
    """以滴声分界，将分段组合

    Args:
        pickle_dir (str): pickle文件的路径
    """    
    with open(pickle_dir, 'rb') as f:
        words = pickle.load(f)

    word_no = 0
    last_bip = 0
    word = []

    for idx, item in enumerate(words):
        if abs(len(item) - 2339) <= 5:
            word_no += 1
            word.append(words[last_bip+2:idx]) # 单词发音会重复两遍，选择last_bip+2
            last_bip = idx
        else:
            continue
    return word

def assemble_word(word:List[AudioSegment], word_repeat:int=1, sentence_repeat:int=1) -> Dict[str, AudioSegment]:
    t = AudioSegment.empty()
    if not word: return None
    t += word[0] * word_repeat
    t += AudioSegment.silent(500)
    if len(word) > 1:
        for sentence in word[1:]:
            t += sentence * sentence_repeat
    return {'word': word[0], 'assemble': t}

def save2wav(pickle_path: Path):
    if not osp.exists(osp.join(wav_dir, 'word')):
        os.mkdir(osp.join(wav_dir, 'word'))
    if not osp.exists(osp.join(wav_dir, 'assemble')):
        os.mkdir(osp.join(wav_dir, 'assemble'))
    pickle_name = pickle_path[-3:]
    word_no = 0
    word_group = group_pickle(pickle_path)
    for x in word_group:
        word_no += 1
        t = assemble_word(x)
        if not t:
            continue
        word_filename = pickle_name + '-' + str(word_no) + '.wav'
        f = t['word'].set_channels(1).export(osp.join(wav_dir, 'word', word_filename), format='wav')
        word_filename = pickle_name + '-' + str(word_no) + '.mp3'
        f = t['assemble'].set_channels(1).export(osp.join(wav_dir, 'assemble', word_filename), format='mp3')
    

def save2wav_multiprocess():
    pickle_list = os.listdir(pickle_dir)
    pool = Pool()
    for pic in pickle_list:
        pool.apply_async(save2wav, args=(osp.join(pickle_dir, pic), ))
    pool.close()
    pool.join()


if __name__ == "__main__":
    save2wav_multiprocess()
