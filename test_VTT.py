import unittest
from unittest.mock import patch, MagicMock, ANY
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import os

# Import the app class
from main import TranscriptionApp

# Correct full path to temp.wav
TEMP_WAV_PATH = r'C:\Users\User\Desktop\Programavimas\Projects\Python\PythonApplication3\UnitTests\temp.wav'

class TestTranscriptionApp(unittest.TestCase):
    def setUp(self):
        with patch('main.Groq') as self.mock_groq:
            self.app = TranscriptionApp()

            # ✅ Mock the button binding so it doesn't raise an error
            self.app.on_mic_button_press = MagicMock()

            self.app.build()

    def test_build_method(self):
        layout = self.app.build()
        self.assertIsInstance(layout, FloatLayout)
        self.assertIsInstance(self.app.label, Label)
        self.assertIsInstance(self.app.language_spinner, Spinner)
        self.assertIsInstance(self.app.mic_button, Button)

    def test_get_language_code(self):
        self.assertEqual(self.app.get_language_code('English'), 'en')
        self.assertEqual(self.app.get_language_code('Lithuanian'), 'lt')
        self.assertEqual(self.app.get_language_code('Spanish'), 'en')

    def test_update_label(self):
        test_text = "Test transcription text"
        self.app.update_label(test_text)
        self.assertEqual(self.app.label.text, test_text)

    @patch('main.Groq')  # Patch Groq directly
    def test_run_transcription(self, mock_groq):
        # Setup mock Groq client
        mock_client = MagicMock()
        mock_transcription = MagicMock()
        mock_transcription.text = "Mock transcription"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        mock_groq.return_value = mock_client  # Ensure Groq() returns the mock

        self.app.client = mock_client

        # Ensure the file exists before running transcription
        assert os.path.exists(TEMP_WAV_PATH), f"File not found: {TEMP_WAV_PATH}"

        # ✅ Pass the file path directly to the method
        self.app.run_transcription(TEMP_WAV_PATH)

        # Verify that transcription was processed
        mock_client.audio.transcriptions.create.assert_called_once_with(
            file=(TEMP_WAV_PATH, ANY),
            model='whisper-large-v3-turbo',
            language='en',
            response_format='verbose_json'
        )

        # Verify label was updated with transcription
        Clock.tick()
        self.assertEqual(self.app.label.text, "Mock transcription")


if __name__ == '__main__':
    unittest.main()
