import streamlit as st
from PIL import Image
from time import time
import os

from preprocess_audio import save_audio
from vosk_transcriber import vosk_transcribe
from silero_punctuation import apply_punkt_to_text
from spacy_formatter import format_for_streamlit
from get_weights import check_and_load

# SETTINGS
st.set_page_config(page_title="web-app", page_icon=":vhs:", layout="wide")

model_settings = {"Vosk_SM": {"MICROSERVICE": "0.0.0.0", "ENABLED": "True"},
                  "Vosk_LG": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"},
                  "🤗": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"},
                  "Nemo": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"}}


def show_img(img_path, width=300):
    img_to_show = Image.open(img_path)
    st.image(img_to_show, width=width)


@st.cache
def get_weights():
    check_and_load()


def get_edited_text():
    # get data
    if "data" not in st.session_state.keys():
        return None
    else:
        return st.session_state["data"]


def save_edited_text():
    # save data
    if "editor" in st.session_state.keys():
        if "data" not in st.session_state.keys():
            st.session_state.update({"data": st.session_state["editor"]})
        else:
            st.session_state["data"] = st.session_state["editor"]


def main():
    # side_img = Image.open("images/logo_red.png")
    with st.sidebar:
        show_img("images/logo_red.png", width=250)

    st.sidebar.subheader("Menu")
    website_menu = st.sidebar.selectbox(options=("🎃 Главная 🎃", "Документация проекта", "Команда", "Оставить отзыв",),
                                        label="Page",
                                        key="0")
    st.set_option('deprecation.showfileUploaderEncoding', False)

    if website_menu == "🎃 Главная 🎃":
        editor = st.sidebar.checkbox("Редактор")
        st.sidebar.write("- - - - - - -")
        st.sidebar.subheader("Настройки")
        test = st.sidebar.checkbox("Использовать тестовый файл")
        num = None
        if st.sidebar.checkbox("Использовать ASR для фрагмента"):
            num = st.sidebar.number_input("chunks", min_value=10, max_value=100, step=10)
        model = st.sidebar.selectbox("API", ("Vosk_SM", "Vosk_LG", "🤗", "Nemo"))
        st.sidebar.write(model_settings[model])
        placeholder = None
        with st.container():
            col1, col2 = st.columns((4, 1))

            with col1:
                audio_file = st.file_uploader("Загрузите аудио файл", type=['wav', 'mp3', 'ogg', 'm4a', 'aac'])

                if audio_file is not None:
                    if not os.path.exists("audio"):
                        os.makedirs("audio")
                    with st.spinner("Идет загрузка аудио..."):
                        is_saved = save_audio(audio_file)
                    if not is_saved:
                        st.warning("Файл не сохранен. Попробуйте еще раз.")
                    elif is_saved:
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

            if st.button("Получить транскрипцию", key="transcribe"):
                placeholder = st.empty()
                if "transcribe" not in st.session_state.keys():
                    st.session_state.update({"transcribe": True})

                with placeholder:
                    col1, col2 = st.columns((4, 1))

                    with col1:
                        with st.spinner("Идет загрузка транскрипции..."):
                            if test:
                                data = apply_punkt_to_text("test_text")
                            else:
                                res = vosk_transcribe(logfile="res.txt", num=num)
                                data = apply_punkt_to_text("res.txt")

                        if editor:
                            st.session_state.update({"edit": True})
                            st.session_state.update({"data": data})
                        else:
                            st.session_state.update({"edit": False})
                            format_for_streamlit(data)

                    with col2:
                        if not editor:
                            show_img("images/wrd.png", width=100)
                            st.download_button("Скачать .docx", data=data, file_name="asr.docx", key="wrd")
                            show_img("images/txt.png", width=100)
                            st.download_button("Скачать .txt", data=data, file_name="asr.txt", key="txt")

            if editor and "edit" in st.session_state.keys():
                placeholder = st.empty()
                with st.container():
                    col1, col2 = st.columns((4, 1))

                    with col1:
                        data = st.text_area("Редактировать", height=800, key="editor",
                                            value=get_edited_text())
                        if st.button("Сохранить изменения 💾"):
                            st.session_state.update({"data": data})
                            with open("edited.txt", "w", encoding="utf-8") as writer:
                                writer.write(get_edited_text())
                    with col2:
                        # TODO: convert to .docx
                        data = get_edited_text()
                        show_img("images/wrd.png", width=100)
                        st.download_button("Скачать .docx", data=data, file_name="asr.docx", key="edit_wrd")
                        show_img("images/txt.png", width=100)
                        st.download_button("Скачать .txt", data=data, file_name="asr.txt", key="edit_txt")


if __name__ == "__main__":
    get_weights()
    main()
