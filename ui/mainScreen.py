from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

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

                print(f"Product added: {product_name}")
                # Save the product to the database
                db.add_product(product_name)

    def display_results(self, result):
        """Display recognized products below the 'Atpažinti produktai' section."""
        # OPS-12
        self.ids.transcription.text = result
        self.save_to_products(result)
        self.update_product_list()

    def save_to_products(self, result):
        lines = result.split("\n")
        id = 1
        for line in lines:
            if line.strip().startswith("- Patiekalas:"):
                product_name = line.split(":")[1].strip()
                PRODUCTS.append({
                    "id": id,
                    "product_name": product_name
                })
                id += 1

    def load_statistics(self):
        self.manager.current = "statistics"


    def update_product_list(self):
        product_list = self.ids.product_list
        product_list.clear_widgets()

        for product in PRODUCTS:

            # Add a button for each recognized product
            product_button = Button(
                text=product["product_name"],
                size_hint_y=None,
                height=40,
                on_press=lambda btn, p_id=product["id"]: self.edit_product(p_id)
            )
            delete_button = Button(
                text="Pašalinti",
                size_hint_x=None,
                width=100,
                height=40,
                on_press=lambda btn, p_id=product["id"]: self.confirm_delete(p_id)
            )

            product_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            product_layout.add_widget(product_button)
            product_layout.add_widget(delete_button)

            # Pridedame šį BoxLayout į sąrašą
            product_list.add_widget(product_layout)

    def edit_product(self, product_id):
        # Sukuriame pop-up su galimybe redaguoti produkto pavadinimą
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)

        # Sukuriame teksto lauką su esamu produkto pavadinimu
        self.product_input = TextInput(
            text=product["product_name"],
            size_hint_y=None,
            height=40
        )

        # Sukuriame mygtukus „Išsaugoti“ ir „Atšaukti“
        button_layout = BoxLayout(spacing=10)

        save_button = Button(
            text="Išsaugoti",
            on_press=lambda btn, p_id = product_id: self.save_edited_product(p_id, popup)
        )
        cancel_button = Button(
            text="Atšaukti",
            on_press=lambda btn: popup.dismiss()
        )

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        # Sudedame tekstą ir mygtukus į pop-up langą
        popup_layout.add_widget(self.product_input)
        popup_layout.add_widget(button_layout)

        popup = Popup(
            title=f"Redaguoti produktą",
            content=popup_layout,
            size_hint=(0.5, 0.4)
        )
        popup.open()

    def save_edited_product(self, product_id, popup):
        new_product_name = self.product_input.text.strip()

        if new_product_name:
            # Atnaujinti produkto pavadinimą sąraše
            for product in PRODUCTS:
                if product["id"] == product_id:
                    product["product_name"] = new_product_name
                    break  # Baigiam ciklą, kai randam reikiamą produktą

            # Uždaryti redagavimo langą
            popup.dismiss()

            # Atnaujinti sąrašą ekrane
            self.update_product_list()

            # Sukuriame pranešimo lango turinį
            success_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            success_label = Label(text=f"Produkto pavadinimas pakeistas į '{new_product_name}'")
            ok_button = Button(text="OK", size_hint=(1, None), height=40)

            # Sukuriame Popup langą
            success_popup = Popup(
                title="Sėkminga operacija",
                content=success_layout,
                size_hint=(0.5, 0.3)
            )

            # Priskiriame mygtukui veiksmą uždaryti langą
            ok_button.bind(on_press=lambda btn: success_popup.dismiss())

            # Pridedame elementus į langą
            success_layout.add_widget(success_label)
            success_layout.add_widget(ok_button)

            # Atidarome langą
            success_popup.open()

    def confirm_delete(self, product_id):
        # Sukuriame patvirtinimo langą
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        product = product["product_name"]
        label = Label(text=f"Ar tikrai norite ištrinti {product}?")
        button_layout = BoxLayout(spacing=10)

        # Mygtukai "Taip" ir "Atšaukti"
        confirm_button = Button(text="Taip", on_press=lambda btn: self.delete_product(product_id, product, popup))
        cancel_button = Button(text="Atšaukti", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(label)
        popup_layout.add_widget(button_layout)

        popup = Popup(title="Patvirtinimas", content=popup_layout, size_hint=(0.5, 0.3))
        popup.open()

    def delete_product(self, product_id, product, popup):
        # Uždaryti patvirtinimo langą
        popup.dismiss()
        global PRODUCTS
        PRODUCTS = [product for product in PRODUCTS if product['id'] != product_id]

        # Atnaujinti produktų sąrašą (jei reikia)
        self.update_product_list()

        # Sėkmingo ištrynimo popup su "OK" mygtuku
        success_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        success_label = Label(text=f"Įrašas '{product}' sėkmingai ištrintas.")
        ok_button = Button(text="OK", on_press=lambda btn: success_popup.dismiss())

        success_popup_layout.add_widget(success_label)
        success_popup_layout.add_widget(ok_button)

        success_popup = Popup(
            title="Sėkminga operacija",
            content=success_popup_layout,
            size_hint=(0.5, 0.3)
        )
        success_popup.open()

        #OPS-12
    def update_from_text(self):
        #db.add_product("Kebabas su mėsa", "2025-01-12 08:30:00") # - jei noretume manualiai pridet kazkoki produkta, kad patikrint filtravima! 'FILTRAVIMAS'
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
