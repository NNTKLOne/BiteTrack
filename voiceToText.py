import os
from groq import Groq
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import threading
from kivy.core.window import Window

import sounddevice as sd
import wave

class TranscriptionApp(App):
    def build(self):
        Window.size = (800, 600)               
        Window.clearcolor = (0.9, 0.9, 0.9, 1)   

        # 2) Label (text) customization
        text_color = (1, 0, 0, 1)     
        font_size = 20               
        font_name = "Roboto"       

        layout = FloatLayout()

        self.label = Label(
            text="Click the microphone to record...",
            halign="center",
            valign="middle",
            color=text_color,
            font_size=font_size,
            font_name=font_name,
            size_hint=(1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        layout.add_widget(self.label)

        self.mic_button = Button(
            size_hint=(None, None),
            size=(128, 128),
            pos_hint={'center_x': 0.5, 'y': 0},   
            background_normal="microphonePng.png",  
            background_down="microphonePng.png"     
        )
        self.mic_button.bind(on_press=self.on_mic_button_press)
        layout.add_widget(self.mic_button)

        self.is_recording = False
        self.recording_thread = None

        return layout

    def on_mic_button_press(self, instance):

        if not self.is_recording:
            self.is_recording = True
            self.label.text = "Recording... Click again to stop."
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
        else:
            self.is_recording = False
            self.label.text = "Transcribing..."
            threading.Thread(target=self.run_transcription).start()

    def record_audio(self):
        sample_rate = 48000
        channels = 2
        filename = "temp.wav"

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  
            wf.setframerate(sample_rate)

            def audio_callback(indata, frames, time_info, status):
                if status:
                    print("Recording status:", status)
                wf.writeframes(indata.tobytes())

                if not self.is_recording:
                    raise sd.CallbackStop()
            with sd.InputStream(samplerate=sample_rate,
                                channels=channels,
                                dtype='int16',  # 16-bit
                                callback=audio_callback):
                while self.is_recording:
                    sd.sleep(200) 

    def run_transcription(self):
        client = Groq(api_key="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")
        audio_file_path = "temp.wav"

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
