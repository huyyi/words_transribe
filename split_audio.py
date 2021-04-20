from pydub import AudioSegment
import os.path as osp
import os
from utils import read_pickle
import pykakasi
from tqdm import tqdm
import csv
from multiprocessing import Pool

def parse_res(word:dict, audio:AudioSegment):
    """通过识别结果找到对应音频输出

    Args:
        word (dict): {"Confidence": int, 'Transcript': str, 'word': List[Dict[str, str]]}
    Returns:
        [tuple]: [description]
    """
    trans_text = word['Transcript']
    word_text = find_word(trans_text)
    start_time = word['word'][0]['start_time'].total_seconds() * 1000
    end_time = word['word'][-1]['end_time'].total_seconds() * 1000
    word_audio = audio[start_time:end_time+500]
    return (word_text, word_audio)

def find_word(text:str) -> str:
    """找连续相同字符
    输入：12312322412 输出：123


    Args:
        text (str)

    Returns:
        str
    """
    t = ''
    for i in range(len(text)):
        t += text[i]
        a = text[i+1:i+len(t)+1]
        if t == a:
            return t
    return ''
    

def parse_one_file(file_name:str):
    kks = pykakasi.kakasi()
    roma_name = kks.convert(file_name)[0]['hepburn']
    audio = AudioSegment.from_mp3(osp.join('single', file_name)+'.mp3')
    trans_res = read_pickle(osp.join('res', file_name))
    results = []
    with tqdm(enumerate(trans_res), desc='处理文件%s'%file_name, total=len(trans_res), ncols=80) as t:
        try:
            for (idx, res) in t:
                a, b = parse_res(res, audio)
                if a:
                    print('%d找到单词:%s' % (idx,a))
                else:
                    print('找词失败')
                word_reading_name = roma_name + '-%d.mp3'%idx
                b.export(osp.join('reading', word_reading_name), format='mp3')
                word_hira = kks.convert(a)[0]['hira']
                results.append({'file_name':word_reading_name, 'word':a, 'word_hira':word_hira, 'Transcript': res['Transcript']})
        except KeyboardInterrupt:
            t.close()
            raise
    return results

def parse_all():
    file_list = os.listdir('res')
    pool = Pool()
    results = []
    for file in file_list:
        results.append(pool.apply_async(parse_one_file, args=(file, )))
    pool.close()
    pool.join()
    with open('result.csv', 'a+', encoding='utf-8', newline='') as results_file:
        writer = csv.DictWriter(results_file, fieldnames=['file_name', 'word', 'word_hira', 'Transcript'])
        for x in results:
            writer.writerows(x.get())

if __name__ == "__main__":
    f = open('result.csv', 'w', encoding='utf-8', newline='')
    f.close()
    parse_all()
    # find_word('暗記暗記丸暗記')
