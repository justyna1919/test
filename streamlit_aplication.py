import streamlit as st
import requests
import os
import json
import csv
import pyttsx3
from konwersja_mowy_vosk import konwersja_mowy_vosk
from dotenv import load_dotenv

# Ustawienia
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\TEMP18\CERTY_NOWE\trusted_202405.pem"
load_dotenv()

# Pobierz klucz API
api_key = os.getenv("API_KEY")
url = r"https://genai.corpnet.pl:8443/ollama_apikey/api/generate"
headers = {"Authorization": api_key}  # Schowałam swój klucz


# Wczytanie danych CSV z cache
@st.cache_data
def load_csv():
    with open("data.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        return "\n".join([", ".join(row) for row in reader])


csv_data = load_csv()

# Inicjalizacja kontekstu rozmowy (na tym etapie te dane są nieistotne, dla mnie najważniejsze jest działanie aplikacji)
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = (
        "Dane z pliku CSV:\n"
        + csv_data
        + "\nZawsze odpowiadaj maksymalnie dwoma zdaniami."
    )

# Flaga do kontrolowania nasłuchiwania
if "listening" not in st.session_state:
    st.session_state.listening = False


# Funkcja do odświeżania strony za pomocą JavaScript
def refresh_page():
    st.markdown("<script>window.location.reload();</script>", unsafe_allow_html=True)


# Funkcja do obsługi nasłuchiwania i zadawania pytań
def listen_and_respond():
    user_input = konwersja_mowy_vosk()
    st.session_state.last_user_input = user_input
    st.write("Twoje pytanie:", user_input)

    # Tworzenie promptu
    prompt_text = st.session_state.conversation_context + "\n" + user_input

    prompt = {
        "model": "llama3.1:8b",
        "prompt": prompt_text,
        "role": "user",
    }

    # Wysyłanie zapytania do API
    response = requests.post(url, headers=headers, json=prompt, stream=True)

    output = ""
    for line in response.iter_lines():
        if line:
            body = json.loads(line)
            if body.get("done") is False:
                output += body.get("response", "")
            else:
                # Aktualizacja kontekstu
                st.session_state.conversation_context += (
                    "\n" + user_input + "\n" + output
                )
                st.write("Odpowiedź AI:", output)

                # Konwersja tekstu na mowę
                engine = pyttsx3.init()
                engine.setProperty("rate", 130)
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[0].id)
                engine.say(output)
                engine.runAndWait()
                break


# Interfejs użytkownika
st.title("Asystent głosowy z AI")
st.write(
    "Kliknij przycisk, aby rozpocząć nasłuchiwanie. Po zadaniu pytania, możesz mówić dalej bez klikania."
)

# Przycisk do rozpoczęcia nasłuchiwania lub kontynuacji
if st.button("Rozpocznij nasłuchiwanie") or st.session_state.listening:
    st.session_state.listening = True
    listen_and_respond()
    # Odśwież stronę za pomocą JavaScript
    refresh_page()
    # Nie używamy st.experimental_rerun() - odświeżanie jest obsługiwane przez JavaScript

# Przycisk do zatrzymania nasłuchiwania
if st.button("Zatrzymaj nasłuchiwanie"):
    st.session_state.listening = False

st.sidebar.markdown("---")

# Sidebar for Mode Selection
mode = st.sidebar.radio(
    "Wybierz tryb:", options=["Pobieranie danych ", "Zapytaj asystenta"], index=1
)

st.sidebar.markdown("---")

