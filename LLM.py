import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

# Your Groq API Key
API_KEY = "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"
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"


class LlamaApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        #  įvesties vieta
        self.input_box = TextInput(
            hint_text="Įveskite tekstą ką valgėte (laikinas variantas, kol nesujungta su VTT):",
            size_hint=(1, 0.15),
            font_size=20,
            multiline=True
        )
        self.add_widget(self.input_box)

        # Send mygtukas
        self.send_button = Button(
            text="Išrinkti patiekalus",
            size_hint=(1, 0.15),
            font_size=20,
            background_color=(0, 0.5, 1, 1)
        )
        self.send_button.bind(on_press=self.send_query)
        self.add_widget(self.send_button)

        # išvesties vieta
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.output_label = Label(
            text="Aptikti patiekalai atsiras čia...",
            font_size=18,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.output_label.bind(size=self.output_label.setter('text_size'))
        self.scroll.add_widget(self.output_label)
        self.add_widget(self.scroll)

    def send_query(self, instance):
        query = self.input_box.text.strip()
        if not query:
            self.output_label.text = "Prašome įvesti tinkamą patiekalą."
            return

        response = self.call_llama_api(query)
        self.process_response(response)

    def call_llama_api(self, query):
        try:
            # Promptas atrinkti tik maisto patiekalam
            prompt = (
                "Pavyzdys:\n"
                "---EXAMPLE---\n"
                "Šiandien vakare valgiau kebabą su česnakiniu padažu. Ryte, atsikėlęs valgiau cepelinus su kiauliena.\n"
                "Atsakymas turėtų būti:\n"
                "- Patiekalas: Kebabas su česnakiniu padažu\n"
                "- Patiekalas: Cepelinai su kiauliena\n"
                "---END EXAMPLE---\n\n"
                "Patvarkyk rašybos klaidas, žodžių galūnes.\n"
                "Išrink tik maisto produktus ir sudaryk patiekalus iš toliau pateikto teksto aprašymo, kuris pateikiamas lietuvių kalba.\n"
                "Surašykite juos atskirai nuorodų formatu:\n\n"
                "---INPUT---\n"
                f"{query}\n"
                "---END INPUT---\n\n"
                "Formatuokite atsakymą kaip:\n"
                "- Patiekalas: [name]"
            )

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300,
                "top_p": 1
            }

            # siunčiam API užklausą
            response = requests.post(BASE_URL, headers=headers, data=json.dumps(data), verify=False)
            response.raise_for_status()

            # gauti rezultatą iš atsakymo
            result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"text": result}

        except requests.exceptions.RequestException as e:
            return {"error": f"Klaida jungiantis: {str(e)}"}
        except Exception as e:
            return {"error": f"Klaida, jungiantis prie API: {str(e)}"}

    def process_response(self, response):
        if "error" in response:
            self.output_label.text = f"{response['error']}"
        else:
            result = response.get("text", "Negauta atsakymo")


            dishes = result.split("\n")
            formatted_output = "Aptikti patiekalai:\n" + "\n".join(dishes)

            self.output_label.text = formatted_output

        self.output_label.size_hint_y = None
        self.output_label.height = self.output_label.texture_size[1]


class LlamaAppMain(App):
    def build(self):
        return LlamaApp()


if __name__ == "__main__":
    LlamaAppMain().run()
