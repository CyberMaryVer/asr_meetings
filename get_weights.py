from silero_punctuation import download_silero
import subprocess
import os

PATHS = ["https://alphacephei.com/kaldi/models/vosk-model-ru-0.10.zip",
         "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.15.zip"]
PATH_TO_DATA = "."


def download_vosk(small=True):
    os.makedirs("weights", exist_ok=True)
    asr_model_path = PATHS[1] if small else PATHS[0]
    subprocess.run(f"wget -O ${PATH_TO_DATA}/model.zip ${asr_model_path}")
    subprocess.run(f"unzip ${PATH_TO_DATA}/model.zip -d /weights/")
    subprocess.run("mv \"vosk-model-small-ru-0.15\" vosk-model-small-ru")


if __name__ == "__main__":
    download_silero()
    download_vosk()
