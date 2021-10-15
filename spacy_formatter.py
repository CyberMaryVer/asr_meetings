import streamlit as st
import spacy

nlp = spacy.load('ru_core_news_md')
ENTITIES = ["PER", "ORG", "DATE", "MONEY", "GPE"]


def format_red_text(text, url=""):
    return f'''<span style="background: rgb(204,34,34); padding: 0.45em 0.6em; margin: 0px 0.25em; line-height: '
                f'1; border-radius: 0.35em;">{text}</span>'''


def entity_info(text, eob):
    ent_info = f'''<b style="font-size:8px">    {eob}</b>''' if eob else ""
    return f'''<span style="background: rgb(246, 241, 234); padding: 0.45em 0.6em; margin: 0px 0.25em; line-height: '
                f'1; border-radius: 0.35em;">{text}{ent_info}</span>'''


def text2tokens(text, ents):
    doc = nlp(text)
    space = " "
    html = ""
    for token in doc:
        if token.ent_type_ in ents:
            html += space + entity_info(token.text, False)
        elif token.tag_ == "PRP" or token.pos == "NUM":
            html += space + entity_info(token.text, False)
        elif token.pos == "PUNCT":
            html += token.text
        else:
            html += space + token.text  # + (space+token.tag_)

    return html


def format_string_as_spacy(text):
    st_text = text2tokens(text, ents=ENTITIES)
    st.markdown(st_text, unsafe_allow_html=True)


# @st.cache
def format_for_streamlit(text, text_file=None):
    if text is None and text_file is not None:
        with open(text_file, "r") as reader:
            text = nlp(reader.read())
    elif text is None:
        return
    format_string_as_spacy(text)
