import streamlit as st
from PIL import Image
from time import time
import os

from get_weights import check_and_load
check_and_load()

from preprocess_audio import save_audio
from vosk_transcriber import vosk_transcribe
from silero_punctuation import apply_punkt_to_text
from spacy_formatter import format_for_streamlit

# SETTINGS
st.set_page_config(page_title="web-app", page_icon=":vhs:", layout="wide")

model_settings = {"Vosk_SM": {"MICROSERVICE": "0.0.0.0", "ENABLED": "True"},
                  "Vosk_LG": {"MICROSERVICE": "0.0.0.0", "ENABLED": "True"},
                  "🤗": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"},
                  "Nemo": {"MICROSERVICE": "0.0.0.0", "ENABLED": "False"}}


def show_img(img_path, width=300):
    img_to_show = Image.open(img_path)
    st.image(img_to_show, width=width)


@st.cache
def get_weights():
    check_and_load()


def get_edited_text(data_key="data"):
    # get data
    if data_key not in st.session_state.keys():
        return None
    else:
        return st.session_state[data_key]


def get_transcription(audio_file, data_key="data", num=None, test=False):
    # get transcription and apply punctuation
    if data_key in st.session_state.keys() and "file_size" in st.session_state.keys() and \
            st.session_state["file_size"] == audio_file.size:
        data = st.session_state[data_key]
    else:
        with st.spinner("Идет загрузка транскрипции..."):
            if test:
                data = apply_punkt_to_text("test_text")
            else:
                vosk_transcribe(logfile="res.txt", num=num, vosk_model="small")
                data = apply_punkt_to_text("res.txt")
        st.session_state.update({data_key: data})
    return data


def st_show_text(audio_file, data_key="data", editor=False, test=False, num=None):
    if st.button("Получить транскрипцию", key="transcribe"):
        placeholder = st.empty()
        data = get_transcription(audio_file, data_key, num, test)

        with placeholder:
            col1, col2 = st.columns((4, 1))

            with col1:
                if editor:
                    st.session_state.update({"edit": True})
                else:
                    st.session_state.update({"edit": False})
                    format_for_streamlit(data)

            with col2:
                if not editor:
                    st_download(data)

    if editor and "edit" in st.session_state.keys():
        placeholder = st.empty()
        with st.container():
            col1, col2 = st.columns((4, 1))

            with col1:
                with st.form("editor_api"):
                    data = st.text_area("Редактировать", height=800, key="edit_txt",
                                        value=get_edited_text(data_key))
                    if st.form_submit_button("Сохранить изменения 💾"):
                        st.markdown("Изменения сохранены ✅")
                        st.session_state.update({data_key: data})

                        with open("edited.txt", "w", encoding="utf-8") as writer:
                            writer.write(get_edited_text(data_key))
            with col2:
                # TODO: convert to .docx
                data = st.session_state[data_key]
                if data is not None:
                    st_download(data)


def st_download(data):
    show_img("images/wrd.png", width=100)
    st.download_button("Скачать .docx", data=data, file_name="asr.docx", key="wrd")
    show_img("images/txt.png", width=100)
    st.download_button("Скачать .txt", data=data, file_name="asr.txt", key="txt")


def main():
    # side_img = Image.open("images/logo_red.png")
    with st.sidebar:
        show_img("images/logo_red.png", width=250)

    st.sidebar.subheader("Меню")
    website_menu = st.sidebar.selectbox(options=("Главная", "Документация проекта", "Команда", "Оставить отзыв",),
                                        label="Page",
                                        key="0")
    st.set_option('deprecation.showfileUploaderEncoding', False)

    if website_menu == "Главная":

        editor = st.sidebar.checkbox("Редактор")
        st.sidebar.text("")

        settings_form = st.sidebar.form("settings")
        with settings_form:
            st.subheader("Настройки")
            test = st.checkbox("Использовать тестовый файл")
            frag = st.checkbox("Использовать для фрагмента")
            num_frag = st.number_input("chunks", min_value=10, max_value=100, step=10)
            num = num_frag if frag else None
            model = st.selectbox("Модель", ("Vosk_SM", "Vosk_LG", "🤗", "Nemo"))
            st.form_submit_button("Применить")

        if model not in ["Vosk_SM"]:
            st.sidebar.warning("Данная модель не подключена. Будет использоваться Vosk_SM")

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
                st.markdown("Модель:")
                st.write(model_settings[model])
                st.markdown("Статус:")
                if audio_file is not None:
                    st.success("Файл загружен")
                else:
                    st.error("Файл не загружен")

        if audio_file is not None and not test:
            st.session_state.update({"file_size": audio_file.size})
            st.markdown("## Текст")
            st.sidebar.subheader("Audio file")
            file_details = {"Filename": audio_file.name, "FileSize": audio_file.size}
            st.sidebar.write(file_details)
            st_show_text(audio_file, data_key="data", editor=editor, test=test, num=num)

        elif test:
            st_show_text(audio_file, editor=editor, data_key="test_data", test=test, num=num)


if __name__ == "__main__":
    get_weights()
    main()
