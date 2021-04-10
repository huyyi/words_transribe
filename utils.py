def play_list(audio_list: list) -> None:
    """播放所有片段

    Args:
        audio_list (list): 片段的列表
    """    
    from pydub.playback import play
    [play(x) for x in audio_list]

def cuts_dura(cuts: list) -> None:
    """打印所有分段的时长

    Args:
        cuts (list): 分段的列表
    """
    duration = [len(x) for x in cuts]
    for i in range(len(cuts)):
        print(i, ':', duration[i])

def read_pickle(pickle_dir: str)->list:
    """读pickle文件
    """    
    import pickle
    with open(pickle_dir, 'rb') as f:
        cuts = pickle.load(f)
    return cuts

def read_config():
    import yaml
    with open('config.yml', 'r', encoding='utf-8') as f:
        configs = yaml.load(f, Loader=yaml.BaseLoader)
    return configs

config = read_config()

def aggregate_audio(sound_list):
    from pydub import AudioSegment
    t = AudioSegment.empty()
    for sound in sound_list:
        t += sound
        t += AudioSegment.silent(config['silent_duration'])
    return t