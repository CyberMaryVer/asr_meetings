import yaml
import torch
import os
from torch import package
from postprocess_txt import merge_txt

PATH_TO_DATA = os.path.dirname(__file__)

# SILERO
SILERO_DIR = "silero_punkt"
SILERO_WEIGHTS = os.path.join(SILERO_DIR, "v1_4lang_q.pt")


def download_silero(model_dir=SILERO_DIR):
    torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                                   'latest_silero_models.yml',
                                   progress=False)

    with open('latest_silero_models.yml', 'r', encoding="utf-8") as yaml_file:
        models = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    model_conf = models.get('te_models').get('latest')
    model_url = model_conf.get('package')
    os.makedirs(model_dir, exist_ok=True)
    if not os.path.isfile(SILERO_WEIGHTS):
        torch.hub.download_url_to_file(model_url, SILERO_WEIGHTS, progress=True)


if not os.path.exists("./silero_punkt"):
    download_silero()
imp = package.PackageImporter(SILERO_WEIGHTS)
model = imp.load_pickle("te_model", "model")


def apply_te(text, save=False, lan="ru"):
    enh_text = model.enhance_text(text, lan=lan)

    if save:
        with open("res.txt", "w", encoding="utf-8") as writer:
            writer.write(enh_text)

    return enh_text


def apply_punkt_to_text(text_file, save=False):
    text = merge_txt(text_file)

    enh_text = []
    for sent in text.split("."):
        sent = apply_te(sent)
        enh_text.append(sent)

    text = ' '.join(enh_text)
    text = text.replace(",,", ",")

    if save:
        with open("punkt.txt", "w", encoding="utf-8") as writer:
            writer.write(text)
    return text


if __name__ == "__main__":
    pass
