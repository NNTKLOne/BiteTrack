import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

# Your Groq API Key
API_KEY = "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"
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

class LlamaApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

    def call_llama_api(self, query):
        try:
            # Promptas atrinkti tik maisto patiekalams
            prompt = (
                f"Extract only the food items from the following meal description and format it as a dish:\n\n"
                f"{query}\n\n"
                f"Format response as 'Dish: [dish name]'."
            )

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 100,
                "top_p": 1
            }

            # Siųsti HTTP requestą
            response = requests.post(BASE_URL, headers=headers, data=json.dumps(data), verify=False)
            response.raise_for_status()

            # Išrinkti rezultatą iš atsakymo
            result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"text": result}

        except requests.exceptions.RequestException as e:
            # Ryšio klaidos
            return {"error": f"Klaida jungiantis: {str(e)}"}

        except Exception as e:
            # Kitos klaidos
            return {"error": f"Klaida, jungiantis prie API: {str(e)}"}

    def process_response(self, response):
        if "error" in response:
            return response["error"]
        else:
            result = response.get("text", "Negauta atsakymo")
            return f"Aptiktas patiekalas:\n{result}"

class LlamaAppMain(App):
    def build(self):
        return LlamaApp()

if __name__ == "__main__":
    LlamaAppMain().run()
