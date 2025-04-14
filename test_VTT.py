import unittest
from unittest.mock import patch, MagicMock, ANY
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import os

# Importuojama pagrindinė programos klasė
from main import TranscriptionApp

# Tikslus kelias iki temp.wav failo
TEMP_WAV_PATH = r'C:\Users\User\Desktop\Programavimas\Projects\Python\PythonApplication3\UnitTests\temp.wav'

class TestTranscriptionApp(unittest.TestCase):
    def setUp(self):
        # Naudojamas `patch`, kad būtų galima perimti Groq klasę
        with patch('main.Groq') as self.mock_groq:
            self.app = TranscriptionApp()

            # Sukuriamas netikras metodas, kad mygtuko paspaudimas nesukeltų klaidų
            self.app.on_mic_button_press = MagicMock()

            # Paleidžiama programos sąsaja (UI)
            self.app.build()

    def test_build_method(self):
        # Tikrinama, ar sukurti elementai yra tinkamo tipo
        layout = self.app.build()
        self.assertIsInstance(layout, FloatLayout) # Patikrinama, ar išdėstymas yra FloatLayout
        self.assertIsInstance(self.app.label, Label) # Patikrinama, ar etiketė yra Label tipo
        self.assertIsInstance(self.app.language_spinner, Spinner) # Patikrinama, ar kalbos pasirinkiklis yra Spinner tipo
        self.assertIsInstance(self.app.mic_button, Button) # Patikrinama, ar mygtukas yra Button tipo

    def test_get_language_code(self):
        # Tikrinama, ar kalbos kodas grąžinamas teisingai
        self.assertEqual(self.app.get_language_code('English'), 'en') # Anglų kalba → 'en'
        self.assertEqual(self.app.get_language_code('Lithuanian'), 'lt') # Lietuvių kalba → 'lt'
        self.assertEqual(self.app.get_language_code('Spanish'), 'en') # Jei kalba nežinoma → numatytasis 'en'

    def test_update_label(self):
        # Tikrinama, ar etiketei priskiriamas tekstas atnaujinamas teisingai
        test_text = "Test transcription text"
        self.app.update_label(test_text)
        self.assertEqual(self.app.label.text, test_text) # Patikrinama, ar tekstas atnaujintas etiketei

    @patch('main.Groq')
    def test_run_transcription(self, mock_groq):
        # Sukuriamas netikras Groq klientas
        mock_client = MagicMock()
        mock_transcription = MagicMock()
        mock_transcription.text = "Mock transcription" # Nustatomas grąžinamas transkripcijos tekstas
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        mock_groq.return_value = mock_client # `Groq()` turi grąžinti `mock_client`

        self.app.client = mock_client

        # Tikrinama, ar temp.wav failas egzistuoja
        assert os.path.exists(TEMP_WAV_PATH), f"Failas nerastas: {TEMP_WAV_PATH}"

        # Paleidžiama transkripcija naudojant temp.wav
        self.app.run_transcription(TEMP_WAV_PATH)

        # Tikrinama, ar transkripcija buvo iškviesta teisingai
        mock_client.audio.transcriptions.create.assert_called_once_with(
            file=(TEMP_WAV_PATH, ANY),
            model='whisper-large-v3-turbo',
            language='en',
            response_format='verbose_json'
        )

        # Tikrinama, ar etiketė buvo atnaujinta su transkripcijos tekstu
        Clock.tick()
        self.assertEqual(self.app.label.text, "Mock transcription")

if __name__ == '__main__':
    unittest.main()
