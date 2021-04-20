import os
import os.path as osp
from utils import read_config
import pickle
from multiprocessing import Pool
configs = read_config()

def transcribe_gcs(gcs_uri):
    print('Process', gcs_uri)
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech_v1p1beta1 as speech
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = osp.abspath(configs['google_ca_dir'])

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="ja-jp",
        enable_word_time_offsets=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.

    res = []
    for result in response.results:
        alternative = result.alternatives[0]
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(alternative.transcript))
        print("Confidence: {}".format(alternative.confidence))
        words = []
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            words.append({'word':word, 'start_time': start_time, 'end_time': end_time})
            print(
                f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
            )
        res.append({"Transcript":alternative.transcript, "Confidence":alternative.confidence, 'word':words})

    with open(osp.join('res', gcs_uri[-7:-4]), 'wb') as f:
        pickle.dump(res, f)

def main():
    base_url = 'gs://audio_storage_stt/single/'
    file_list = os.listdir('single')
    pool = Pool()
    for file in file_list:
        pool.apply_async(transcribe_gcs, args=(base_url + file, ))
    pool.close()
    pool.join()
    

if __name__ == "__main__":
    # transcribe_gcs("gs://audio_storage_stt/single/あ-2.mp3")
    main()