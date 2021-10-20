# !/usr/bin/env python3

from vosk import Model, KaldiRecognizer
from tqdm import tqdm
import sys
import json
import os


def vosk_transcribe(filedir="audio", logfile="text.txt", num=None, vosk_model="small"):
    # SetLogLevel(-1)

    if vosk_model in ["small", "large"]:
        model_path = f"weights/vosk-model-{vosk_model}-ru"
    else:
        raise AttributeError("vosk_model attribute value should be \"large\" or \"small\"")

    if not os.path.exists(model_path):
        print("Please download the model from https://alphacephei.com/vosk/models")

    model = Model(model_path)
    # Large vocabulary free form recognition
    rec = KaldiRecognizer(model, 16000)
    # You can also specify the possible word list
    # rec = KaldiRecognizer(model, 16000, "zero oh one two three four five six seven eight nine")

    audio_files = os.listdir(filedir)
    num = len(audio_files) if num is None else num

    with open(logfile, "w", encoding="utf-8") as writer:
        writer.write("\n")

    for audio in tqdm(audio_files[:num]):
        wf = open(os.path.join(filedir, audio), "rb")
        wf.read(44)  # skip header

        while True:
            data = wf.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass
                # res = json.loads(rec.Result())

        res = json.loads(rec.FinalResult())

        with open(logfile, "a", encoding="utf-8") as writer:
            writer.write(res["text"] + "\n")

        # print(res["text"])
    # print("Done!")
    return 1


if __name__ == "__main__":
    vosk_transcribe(num=50)
    # main()
