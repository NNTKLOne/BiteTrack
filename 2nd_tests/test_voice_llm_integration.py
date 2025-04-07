import pytest
import os
from voiceToText import VoiceToText
from LLM import send_query
import logging

# Nutildyti nereikalingus log'us testavimo metu
for noisy_module in ['httpx', 'httpcore', 'groq']:
    logging.getLogger(noisy_module).setLevel(logging.CRITICAL)


def test_audio_transcription_and_llm_response_lt():
    # 1. Failo egzistavimo patikrinimas
    file_path = os.path.join(os.path.dirname(__file__), "audio_test.wav")
    assert os.path.isfile(file_path), f" Failas nerastas: {file_path}"

    # 2. Inicijuojam transkripcijos klasę ir nustatome lietuvių kalbą
    vtt = VoiceToText()
    vtt.audio_file_path = file_path
    vtt.set_language("Lithuanian")

    # 3. Transkribuojame
    transcribed_text = vtt._run_transcription()

    if isinstance(transcribed_text, bytes):
        pytest.fail(" Transkribavimo funkcija grąžino bytes – tikėtasi tekstas (str).")

    assert isinstance(transcribed_text, str), " Transkribavimo rezultatas netinkamas (ne str)."
    assert transcribed_text.strip(), " Transkribuotas tekstas tuščias."

    print(f"\n Transkribuotas tekstas:\n{transcribed_text}")

    # 4. Siunčiame tekstą į LLM
    llm_response = send_query(transcribed_text)

    print(f"\n LLM atsakymas:\n{llm_response}")

    # 5. Tikriname, ar atsakyme yra bent vienas patiekalas arba pranešimas, kad nerasta
    assert "Patiekalas" in llm_response or "Maisto produktų nerasta" in llm_response, \
        " LLM atsakyme nėra nei patiekalų, nei 'Maisto produktų nerasta'."
