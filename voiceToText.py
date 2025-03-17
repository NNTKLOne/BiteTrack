import os
from groq import Groq
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
import threading

class TranscriptionApp(App):
    def build(self):
        self.label = Label(text="Transcription pending...", halign="center", valign="middle")
        threading.Thread(target=self.run_transcription, daemon=True).start()
        return self.label

    def run_transcription(self):
        client = Groq(api_key="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")
        audio_file_path = r"C:\Users\User\Desktop\recording.mp3"
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path, audio_file.read()),
                model="whisper-large-v3-turbo",
                language="en",
                response_format="verbose_json",
            )
        Clock.schedule_once(lambda dt: self.update_label(transcription.text))

    def update_label(self, text):
        self.label.text = text

if __name__ == '__main__':
    TranscriptionApp().run()
