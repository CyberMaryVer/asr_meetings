import os
from torch import package
from postprocess_txt import merge_txt


model_dir = "silero_punkt"
model_path = os.path.join(model_dir, "v1_4lang_q.pt")
imp = package.PackageImporter(model_path)
model = imp.load_pickle("te_model", "model")


def apply_te(text, save=False, lan="ru"):
    enh_text = model.enhance_text(text, lan=lan)

    if save:
        with open("res.txt", "w", encoding="utf-8") as writer:
            writer.write(enh_text)

    return enh_text


def apply_punkt_to_text(text_file=None, raw_text=None, save=False):
    if text_file is not None:
        text = merge_txt(txt_file=text_file)
    elif raw_text is not None:
        text = merge_txt(data=raw_text)
    else:
        raise AttributeError("Should indicate text_file or raw_text attribute")

    enh_text = []
    for sent in text.split("."):
        sent = apply_te(sent)
        enh_text.append(sent)

    text = ' '.join(enh_text)
    text = text.replace(",,", ",").replace(" ,", ",")

    if save:
        with open("punkt.txt", "w", encoding="utf-8") as writer:
            writer.write(text)
    return text


if __name__ == "__main__":
    FILE = "test.txt"
    text = apply_punkt_to_text(FILE)
    print(text[:254])
