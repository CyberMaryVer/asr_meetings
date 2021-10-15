# !/usr/bin/env python3

from vosk import Model, KaldiRecognizer
from tqdm import tqdm
import sys
import json
import os


def vosk_transcribe(filedir="audio", logfile="text.txt", num=None):
    # SetLogLevel(-1)

    if not os.path.exists("weights/vosk-model-small-ru"):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        # exit (1)
    print(filedir, os.listdir(filedir))
    audio_files = os.listdir(filedir)
    model = Model("weights/vosk-model-small-ru")

    # Large vocabulary free form recognition
    rec = KaldiRecognizer(model, 16000)

    # You can also specify the possible word list
    # rec = KaldiRecognizer(model, 16000, "zero oh one two three four five six seven eight nine")

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

        print(res["text"])
    # print("Done!")
    return 1


if __name__ == "__main__":
    vosk_transcribe(num=50)
    # main()
