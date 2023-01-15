import streamlit as st
import spacy
from PIL import Image
import pytesseract
import pandas as pd
import PyPDF2
import sys
import re



@st.cache(allow_output_mutation=True)
def load_model(lang):
    models = {"it": "it_core_news_lg", "en": "en_core_web_md"}
    try:
        nlp = spacy.load(models[lang])
        return nlp
    except KeyError:
        st.error("Language not supported.")

def convert_pdf_to_txt(file):
    pdf_file = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_file.pages:
        text += page.extract_text()
    return text


def extract_text(file, lang):
    file_name = file.name
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Users\User\AppData\Local\Programs\Python\Python310\lib\site-packages\pytesseract'
    if file_name.endswith("pdf"):
        text = convert_pdf_to_txt(file)
    elif file_name.endswith(("jpg", "jpeg", "png")):
        # st.write("OCR non ancora disponibile ma ci stiamo lavorando")
        # sys.exit()
        text = pytesseract.image_to_string(file, lang=lang)
    else:
        with open(file, 'r') as f:
            text = f.read()
    st.write("TESTO ESTRATTO: \n" + text)
    return text

def process_text(text, nlp):
    doc = nlp(text)
    # Estrae date con regex
    date_formats = "(\d{1,2}[-/]\d{1,2}[-/]\d{4})|(\d{1,2}\s[a-zA-Z]{3,9}\s\d{4})|([a-zA-Z]{3,9}\s\d{4})|(^(1[0-9]{3}|20[0-9]{2}|2100)$)"
    # Crea oggetto iterabile dalle date matchate
    iterable_dates = re.finditer(date_formats, text)
    # Converte l'oggetto iterabile in una lista per farlo entrare nel dataframe di Pandas
    matched_dates = [match.group() for match in iterable_dates]
    # estrae luoghi ed entità usando le etichette di spacy
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    entities_df = pd.DataFrame(entities, columns=["Entity", "Label"])
    places_df = entities_df[entities_df['Label'] == 'LOC']
    dates_df = pd.DataFrame(matched_dates, columns=["Dates"])
    # estrazione date con dateparser
    return entities_df, places_df, dates_df

def main():
    st.title("Estrattore di testo")
    
    uploaded_file = st.file_uploader("carica un file pdf (jpg e png non ancora supportati)", type=["txt", "pdf", "jpg", "jpeg", "png"])
    lang = st.selectbox("Scegli la lingua", ["it", "en"])

    nlp = load_model(lang)
    if uploaded_file is not None:
        st.subheader("Trascrizione")
        text = extract_text(uploaded_file, lang)
        entities_df, places_df, dates_df = process_text(text, nlp)
        st.subheader("Entità estratte")
        st.dataframe(entities_df)
        if st.button("Scarica CSV entità"):
            entities_df.to_csv("entities.csv", index=False)
            st.success("File scaricato!")
        st.subheader("Luoghi estratti: ")
        st.dataframe(places_df)
        st.subheader("Date estratte: ")
        st.dataframe(dates_df)
        


# TO DO:
# - sistemare OCR per riconoscimento testo da jpg e png (vedi https://github.com/guilhermedonizetti/OCR_Python/blob/master/main.py)
# - inserire un flag per attivare l'analisi del testo
# - estrarre le date
# - estrarre link wikidata delle entità
# - estrarre un abstract del testo
# - tradurre il testo in inglese


if __name__== "__main__":
    main()