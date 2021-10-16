import streamlit as st
from pathlib import Path
import pydub
from pydub.silence import split_on_silence, detect_silence
from datetime import datetime
from time import time
import os


class AudioFile:
    def __init__(self, file_path):
        self.name = file_path
        self.audio = self._extract_audio()
        self.size = os.stat(self.name).st_size

    def _extract_audio(self):
        with open(self.name, "rb") as reader:
            audio = reader.read()
        return audio


def get_counter_code(counter, level=3):
    zeros = "0" * (level - len(str(counter)))
    code = f"{zeros}{counter}"
    return code


def clear_folder(folder):
    # clear the folder to avoid storage overload
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def split_on_chunks(sound, folder="audio"):
    dBFS = sound.dBFS
    # sound = AudioSegment.from_file("/path/to/file.mp3", format="mp3")
    silence = detect_silence(sound, min_silence_len=1000, silence_thresh=dBFS - 16)
    silence = [((start / 1000), (stop / 1000)) for start, stop in silence]  # in sec
    print(silence)

    chunks = split_on_silence(
        sound,

        # split on silences longer than 1000ms (1 sec)
        min_silence_len=1000,

        # anything under -16 dBFS is considered silence
        silence_thresh=dBFS - 26,

        # keep 200 ms of leading/trailing silence
        keep_silence=200
    )
    for idx, chunk in enumerate(chunks[:]):
        code = get_counter_code(idx)
        chunk_name = f"chunk_{code}.wav"
        save_path = Path(folder) / chunk_name
        chunk.export(save_path, format="wav")
        # print(f"chunk_{code} is saved")

    return chunks


def read_from_binary(file_name, file):
    if file_name.endswith("wav"):
        audio = pydub.AudioSegment.from_wav(file)
    elif file_name.endswith("ogg"):
        audio = pydub.AudioSegment.from_ogg(file)
    elif file_name.endswith('mp3'):
        audio = pydub.AudioSegment.from_mp3(file)
    elif file_name.endswith('m4a'):
        audio = pydub.AudioSegment.from_file(file, "m4a")
    elif file_name.endswith("aac"):
        audio = pydub.AudioSegment.from_file(file, "aac")
    else:
        return None
    return audio


@st.cache(show_spinner=False)
def save_audio(file, folder="audio"):
    time_st = time()
    os.makedirs(folder, exist_ok=True)
    datetoday = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # clear the folder to avoid storage overload
    clear_folder(folder)

    try:
        with open("log.txt", "a") as f:
            f.write(f"{file.name} - {file.size} - {datetoday};\n")
    except Exception as e:
        print(f"{type(e)}: {e}")

    audio = read_from_binary(file_name=file.name, file=file)

    if audio is None:
        return False

    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    split_on_chunks(audio, folder=folder)

    time_all = time() - time_st
    print(time_all)
    return True


if __name__ == "__main__":
    with open("test.mp3", "rb") as reader:
        sound = reader.read()