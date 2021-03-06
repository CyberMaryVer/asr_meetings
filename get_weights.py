import subprocess
import os
import yaml
import torch
import gdown

PATH_TO_DATA = os.path.dirname(__file__)

# VOSK
VOSK_WEIGHTS = ["https://alphacephei.com/kaldi/models/vosk-model-ru-0.10.zip",
                "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.15.zip"]
VOSK_DIR = os.path.join(PATH_TO_DATA, "weights")

# SILERO
SILERO_DIR = "silero_punkt"
SILERO_WEIGHTS = os.path.join(SILERO_DIR, "v1_4lang_q.pt")


def download_silero():
    torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                                   'latest_silero_models.yml',
                                   progress=False)

    with open('latest_silero_models.yml', 'r', encoding="utf-8") as yaml_file:
        models = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    model_conf = models.get('te_models').get('latest')
    model_url = model_conf.get('package')
    model_dir = "silero_punkt"
    os.makedirs(model_dir, exist_ok=True)
    if not os.path.isfile(SILERO_WEIGHTS):
        torch.hub.download_url_to_file(model_url, SILERO_WEIGHTS, progress=True)


def download_vosk(small=True):
    import urllib.request
    import zipfile

    os.makedirs(VOSK_DIR, exist_ok=True)
    asr_model_path = VOSK_WEIGHTS[1] if small else VOSK_WEIGHTS[0]
    response = urllib.request.urlopen(asr_model_path)
    binary_file = response.read()
    with open(f'{PATH_TO_DATA}/weights/model.zip', 'wb') as writer:
        writer.write(binary_file)

    with zipfile.ZipFile(os.path.join(VOSK_DIR, "model.zip"), "r") as zip_ref:
        zip_ref.extractall(VOSK_DIR)
    os.rename(os.path.join(VOSK_DIR, "vosk-model-small-ru-0.15"),
              os.path.join(VOSK_DIR, "vosk-model-small-ru"))


def check_and_load(verbose=True):
    if not os.path.exists("./silero_punkt"):
        download_silero()
        if verbose:
            print("Downloading Silero...")
    if not os.path.exists("./weights/vosk-model-small-ru"):
        download_vosk()
        if verbose:
            print("Downloading Vosk...")
    if verbose:
        print("All models are downloaded")


if __name__ == "__main__":
    check_and_load()