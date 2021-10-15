import streamlit as st
from pathlib import Path
import pydub
from vosk_transcriber import vosk_transcribe
from silero_punctuation import apply_punkt_to_text
from spacy_formatter import format_for_streamlit
from get_weights import check_and_load
from datetime import datetime
from PIL import Image
import os

# SETTINGS
model_settings = {"Vosk": {"MICROSERVICE": "0.0.0.0", "ENABLED": "True"},
                  "🤗": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"},
                  "Nemo": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"}}


def show_img(img_path, width=300):
    img_to_show = Image.open(img_path)
    st.image(img_to_show, width=width)


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
    from pydub.silence import split_on_silence

    # sound = AudioSegment.from_file("/path/to/file.mp3", format="mp3")

    chunks = split_on_silence(
        sound,

        # split on silences longer than 1000ms (1 sec)
        min_silence_len=1000,

        # anything under -16 dBFS is considered silence
        silence_thresh=-42,

        # keep 200 ms of leading/trailing silence
        keep_silence=200
    )
    for idx, chunk in enumerate(chunks[1:]):
        code = get_counter_code(idx)
        chunk_name = f"chunk_{code}.wav"
        save_path = Path(folder) / chunk_name
        chunk.export(save_path, format="wav")
        print(f"chunk_{code} is saved")

    return chunks


@st.cache()
def save_audio(file, folder="audio"):
    os.makedirs(folder, exist_ok=True)
    datetoday = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # clear the folder to avoid storage overload
    clear_folder(folder)

    try:
        with open("log.txt", "a") as f:
            f.write(f"{file.name} - {file.size} - {datetoday};\n")
    except Exception as e:
        print(f"{type(e)}: {e}")

    if file.name.endswith("wav"):
        audio = pydub.AudioSegment.from_wav(file)
    elif file.name.endswith("ogg"):
        audio = pydub.AudioSegment.from_ogg(file)
    elif file.name.endswith('mp3'):
        audio = pydub.AudioSegment.from_mp3(file)
    elif file.name.endswith('m4a'):
        audio = pydub.AudioSegment.from_file(file, "m4a")
    elif file.name.endswith("aac"):
        audio = pydub.AudioSegment.from_file(file, "aac")
    else:
        return 1

    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    split_on_chunks(audio, folder=folder)
    # for chunk in chunks:
    #     save_path = Path(folder) / (chunk.chunkname + ".wav")
    #     audio.export(save_path, format="wav")
    # save_path = Path(folder) / (file.name + ".wav")
    # audio.export(save_path, format="wav")

    return 0


def main():
    # side_img = Image.open("images/logo_red.png")
    with st.sidebar:
        show_img("images/logo_red.png")

    st.sidebar.subheader("Menu")
    website_menu = st.sidebar.selectbox(options=("Главная", "Документация проекта", "Команда", "Оставить отзыв",),
                                        label="Page",
                                        key="0")
    st.set_option('deprecation.showfileUploaderEncoding', False)

    if website_menu == "Главная":
        num = None
        if st.sidebar.checkbox("Debug mode"):
            num = st.sidebar.number_input("chunks", min_value=10, max_value=100, step=10)
        st.sidebar.subheader("Model")
        model = st.sidebar.selectbox("API", ("Vosk", "🤗", "Nemo"))
        st.sidebar.subheader("Settings")
        st.sidebar.write(model_settings[model])
        st.markdown("## Аудио файл")
        test = st.checkbox("Использовать тестовый файл")

        with st.container():
            col1, col2 = st.columns((4, 1))

            with col1:
                audio_file = st.file_uploader("Загрузите аудио файл", type=['wav', 'mp3', 'ogg'])

                if audio_file is not None:
                    if not os.path.exists("audio"):
                        os.makedirs("audio")
                    with st.spinner("Идет загрузка аудио..."):
                        is_saved = save_audio(audio_file)
                    if is_saved == 1:
                        st.warning("File size is too large. Try another file.")
                    elif is_saved == 0:
                        try:
                            st.audio(audio_file, format='audio/wav', start_time=0)
                        except Exception as e:
                            audio_file = None
                            st.error(f"Error {type(e)} - {e}. Try again.")
                    else:
                        st.error("Unknown error")
                else:
                    if test:
                        st.audio("test.wav", format='audio/wav', start_time=0)
                        st.session_state.update({"test": "true"})
            with col2:
                st.markdown("Статус:")
                if audio_file is not None:
                    st.success("Файл загружен")
                else:
                    st.error("Файл не загружен")

        if audio_file is not None or test:
            st.markdown("## Текст")
            if "test" not in st.session_state.keys():
                st.sidebar.subheader("Audio file")
                file_details = {"Filename": audio_file.name, "FileSize": audio_file.size}
                st.sidebar.write(file_details)

            if st.button("Получить транскрипцию"):
                # if "res" not in st.session_state:
                #     st.session_state.update({"res": ""})
                with st.container():
                    col1, col2 = st.columns((4, 1))
                    with col1:
                        # st.text("Транскрипция")
                        with st.spinner("Идет загрузка транскрипции..."):
                            if test:
                                data = apply_punkt_to_text("raw.txt")
                                format_for_streamlit(data)
                            else:
                                res = vosk_transcribe(logfile="res.txt", num=num)
                                # if "res" in st.session_state:
                                #     st.session_state["res"] = res
                                data = apply_punkt_to_text("res.txt")
                                format_for_streamlit(data)
                    with col2:
                        # TODO: convert to .docx
                        show_img("images/wrd.png", width=100)
                        st.download_button("Скачать .docx", data=data)
                        show_img("images/txt.png", width=100)
                        st.download_button("Скачать .txt", data=data)


if __name__ == "__main__":
    # page settings
    check_and_load()
    st.set_page_config(page_title="web-app", page_icon=":vhs:", layout="wide")
    main()
