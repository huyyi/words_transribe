from trans_code import group_pickle
from utils import read_config
import os.path as osp
import os

configs = read_config()
os.environ['Path'] += (';' + osp.abspath(configs['ffmpeg_bin']))

if __name__ == "__main__":
    a = group_pickle('pickle\あ-1')
