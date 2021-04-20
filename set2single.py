from pydub import AudioSegment
from tqdm import tqdm
import os
import os.path as osp

def mp32wav():
    if not osp.exists('single'): os.mkdir('single')
    mp3_list = os.listdir('source_audios')
    for mp3 in tqdm(mp3_list):
        seg = AudioSegment.from_mp3(osp.join('source_audios', mp3))
        print(osp.join('source_audios', 'single', mp3))
        f = seg.set_channels(1).export(osp.join('single', mp3))

if __name__ == "__main__":
    mp32wav()