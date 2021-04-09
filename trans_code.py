import os
import os.path as osp
from pathlib import Path
from multiprocessing import Pool
import pickle

wav_dir = Path('./wav')
pickle_dir = Path('./pickle')

if not osp.exists(wav_dir):
    os.mkdir(wav_dir)

def pickle2wav(pickle_dir):
    kana_sub = osp.join(wav_dir, pickle_dir[-3])
    if not osp.exists(kana_sub):
        os.mkdir(kana_sub)
    with open(pickle_dir, 'rb') as f:
        words = pickle.load(f)
    word_no = 1
    in_word_no = 0
    bip_flag = 0
    for word in words:
        if abs(len(word) - 2339) <= 5: # 是滴声则跳过，下一次还跳过
            bip_flag = 1
            word_no += 1
            in_word_no = 0
            continue
        elif bip_flag:
            bip_flag = 0
            continue
        file_name = pickle_dir[-3:] + '-' + str(word_no) + '-' + str(in_word_no) + '.wav'
        print(file_name)
        word = word.set_channels(1)
        f = word.export(osp.join(kana_sub, file_name), format='wav')
        in_word_no += 1

def trans_code():
    pickle_list = os.listdir(pickle_dir)
    pool = Pool()
    for pickle_file in pickle_list:
        pickle_path = osp.join(pickle_dir, pickle_file)
        pool.apply_async(pickle2wav, args=(pickle_path, ))
    pool.close()
    pool.join()


if __name__ == "__main__":
    pickle2wav('pickle\あ-1')