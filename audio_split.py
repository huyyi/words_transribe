from utils import read_config
from pydub import AudioSegment
from pydub.silence import split_on_silence
import pickle
import os
import os.path as osp
from multiprocessing import Pool
import sys
from utils import read_config

configs = read_config()

sys.path.append(osp.abspath(configs['ffmpeg_bin']))
pickle_dir = configs['pickle']
audio_dir = configs['source_audios']

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

def get_cuts():
    file_list = os.listdir(audio_dir)
    pool = Pool()
    for file in file_list:
        if osp.exists(osp.join(pickle_dir, file[:-4])):
            print("文件已处理，跳过")
            continue
        print("处理文件：", file)
        pool.apply_async(read_file, args=(file))
    pool.close()
    pool.join()
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

if __name__ == "__main__":
    get_cuts()