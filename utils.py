def play_list(audio_list):
    from pydub.playback import play
    [play(x) for x in audio_list]