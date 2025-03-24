import sounddevice as sd
import wave
import threading
import numpy as np
from groq import Groq
from kivy.clock import Clock


class VoiceToText:
    def __init__(self):
        self.is_recording = False
        self.recording_thread = None
        self.audio_file_path = "temp.wav"
        self.language_code = 'en'
        self.client = Groq(api_key="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")

    def start_recording(self, callback):
        if not self.is_recording:
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._record_audio, args=(callback,))
            self.recording_thread.start()
        else:
            self.is_recording = False

    def _record_audio(self, callback):
        try:
            device_info = sd.query_devices(kind='input')
            sample_rate = int(device_info['default_samplerate'])
            channels = device_info['max_input_channels']

            if channels < 1:
                raise ValueError("Microphone not found or channels unavailable")

            filename = self.audio_file_path

            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(sample_rate)

                def audio_callback(indata, frames, time_info, status):
                    if status:
                        print(f"Recording status: {status}")

                    # Normalize and amplify audio data
                    gain = 10.0  # loudness
                    amplified_data = np.clip(indata * gain, -32768, 32767).astype(np.int16)

                    # Write to the file
                    wf.writeframes(amplified_data.tobytes())

                    if not self.is_recording:
                        raise sd.CallbackStop()

                with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='int16', callback=audio_callback):
                    print("🔴 Recording started...")
                    while self.is_recording:
                        sd.sleep(200)

            # Check if the file is empty
            if self._is_audio_file_empty(filename):
                raise ValueError("Audio file is empty. Recording failed!")

            # When recording ends, start transcription
            result = self._run_transcription()
            # Use Clock.schedule_once to update UI in main thread
            Clock.schedule_once(lambda dt: callback(result))

        except Exception as e:
            print(f"⚠️ Error during recording: {e}")
            Clock.schedule_once(lambda dt: callback(f"Klaida įrašant: {e}"))

    def _is_audio_file_empty(self, filename):
        try:
            with wave.open(filename, 'rb') as wf:
                frames = wf.getnframes()
                return frames == 0
        except Exception:
            return True

    def _run_transcription(self):
        try:
            with open(self.audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(self.audio_file_path, audio_file.read()),
                    model="whisper-large-v3-turbo",
                    language=self.language_code,
                    response_format="verbose_json",
                )

                # Ensure transcription is converted to a dictionary
                if hasattr(transcription, 'text'):
                    return transcription.text  # Access the text directly if available
                elif isinstance(transcription, dict):
                    return transcription.get("text", "")
                else:
                    raise TypeError(f"Unexpected transcription response type: {type(transcription)}")

        except Exception as e:
            return f"Klaida transkribuojant: {e}"
        # OPS-27 + OPS-23 - Augustas Česnavičius
    def set_language(self, language):
        language_map = {
            'English': 'en',
            'Lithuanian': 'lt'
        }
        self.language_code = language_map.get(language, 'en')
