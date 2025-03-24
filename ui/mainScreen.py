from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from ui.statisticsScreen import StatisticsScreen
from database.database import Database
from LLM import send_query  # Importing function from LLM.py
from voiceToText import VoiceToText
from kivy.clock import Clock

# Laikinas produktų sąrašas (produktų, kurie gali būti išsaugoti į DB)
PRODUCTS = []
db = Database()

# Užkrauname UI failą
Builder.load_file("UI.kv")


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.voice_to_text = VoiceToText()

    def start_recording(self):
        if not self.voice_to_text.is_recording:
            self.ids.transcription.text = "🔴 Įrašymas pradėtas... Paspauskite dar kartą, kad sustabdytumėte."
            self.voice_to_text.start_recording(self.handle_transcription_result)
        else:
            self.ids.transcription.text = "🔎 Transkribuojama..."
            self.voice_to_text.is_recording = False

    def handle_transcription_result(self, result):
        # Schedule UI update on the main thread
        Clock.schedule_once(lambda dt: self.update_transcription(result))

    def update_transcription(self, result):
        self.ids.transcription.text = result
        self.send_to_llm()

    def set_language(self, language):
        self.voice_to_text.set_language(language)
        self.ids.transcription.text = f"Kalba pakeista į: {language}"

    def clear_text(self):
        self.ids.transcription.text = ""

        # OPS-37
    def send_to_llm(self):
        query = self.ids.transcription.text
        self.clear_text()
        # Send query to LLM to get products
        result = send_query(query)

        # Display results in the UI
        self.display_results(result)

        # OPS-39
    def save_to_database(self, result):

        """Save recognized products into the database"""
        # Assuming result is a string with product names listed in a specific format
        # Example result: "- Patiekalas: Kebabas su česnakiniu padažu\n- Patiekalas: Cepelinai su kiauliena"

        lines = result.split("\n")
        for line in lines:
            if line.strip().startswith("- Patiekalas:"):
                product_name = line.split(":")[1].strip()

                # Add only the product_name to PRODUCTS list
                PRODUCTS.append({
                    "product_name": product_name,
                })

                print(f"Product added: {product_name}")
                # Save the product to the database
                db.add_product(product_name)

    def display_results(self, result):
        """Display recognized products below the 'Atpažinti produktai' section."""
        # OPS-12
        self.ids.transcription.text = result
        self.update_product_list(result)

    def load_statistics(self):
        self.manager.current = "statistics"

    def update_product_list(self, result):
        product_list = self.ids.product_list
        product_list.clear_widgets()

        lines = result.split("\n")
        for line in lines:
            if line.strip().startswith("- Patiekalas:"):
                product_name = line.split(":")[1].strip()

                # Add a button for each recognized product
                product_button = Button(
                    text=product_name,
                    size_hint_y=None,
                    height=40
                )
                product_list.add_widget(product_button)

        #OPS-12
    def update_from_text(self):
        """Update the product list based on the TextInput content."""
        product_list = self.ids.product_list
        product_list.clear_widgets()

        text = self.ids.transcription.text.strip()
        if not text:
            return

        lines = text.split("\n")

        for line in lines:
            if line.strip().startswith("- Patiekalas:"):
                product_name = line.split(":", 1)[1].strip()

                # Add a button for each recognized product
                product_button = Button(
                    text=product_name,
                    size_hint_y=None,
                    height=40,
                    on_press=lambda x, name=product_name: self.remove_product(name)
                )
                product_list.add_widget(product_button)


class MyApp(App):
    def build(self):
        self.db = db
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(StatisticsScreen(name="statistics"))
        return sm


if __name__ == "__main__":
    MyApp().run()
