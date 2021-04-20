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
        if abs(len(item) - 2339) <= 100:
            word_no += 1
            word.append(words[last_bip+1:idx]) # 单词发音会重复两遍，选择last_bip+2
            last_bip = idx
        else:
            continue
    return word

def assemble_word(word:List[AudioSegment]):
    """组装cuts

    Args:
        word (List[AudioSegment]): 以滴声分度的segments

    Returns:
        [AudioSegment]: 组装后的音频
    """    
    t = AudioSegment.empty()
    for cut in word:
        t += cut
    return t

def save2wav_multiprocess():
    pickle_list = os.listdir(pickle_dir)
    pool = Pool()
    for pic in pickle_list:
        pool.apply_async(save2wav_with_sentence, args=(osp.join(pickle_dir, pic), ))
    pool.close()
    pool.join()


def save2wav_with_sentence(pickle_path: str):
    """以滴声分界，组装成句

    Args:
        pickle_path (str): pick文件路径
    """    
    if not osp.exists(osp.join(wav_dir, 'word')):
        os.mkdir(osp.join(wav_dir, 'word'))

    pickle_name = pickle_path[-3:]
    word_no = 0
    word_group = group_pickle(pickle_path)
    try:
        with tqdm(word_group, desc="组合中", total=len(word_group)) as t:
            for x in t:
                word_no += 1
                t = assemble_word(x)
                if not t:
                    continue
                word_filename = pickle_name + '-' + str(word_no) + '.wav'
                f = t.set_channels(1).export(osp.join(wav_dir, 'word', word_filename), format='wav')
    except KeyboardInterrupt:
        t.close()
        raise
    t.close()

if __name__ == "__main__":
    # save2wav_multiprocess()
    pass