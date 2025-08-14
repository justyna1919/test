import pyaudio
import json
from vosk import Model, KaldiRecognizer


def konwersja_mowy_vosk():
    # Ścieżka do modelu
    model_path = "C:/vosk-models/polish/vosk-model-small-pl-0.22"

    # Inicjalizacja modelu
    model = Model(model_path)

    # Ustawienia mikrofonu
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=4000,
    )
    stream.start_stream()

    recognizer = KaldiRecognizer(model, 16000)

    print("Rozpoczęto nasłuchiwanie. Mów teraz...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                if text:
                    return text
                # Przerwij po słowie "koniec"
                if "koniec" in text.lower():
                    break
    except KeyboardInterrupt:
        print("Zakończono nasłuchiwanie.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


# Opcjonalnie, można dodać blok testowy
if __name__ == "__main__":
    wynik = konwersja_mowy_vosk()
    if wynik:
        print("Rozpoznany tekst:", wynik)
