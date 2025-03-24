import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from database.database import Database

from ui.statisticsScreen import StatisticsScreen

# Laikinas produktų sąrašas (vietoj DB)
PRODUCTS = []
db = Database()

# Užkrauname UI failą
Builder.load_file("UI.kv")

class MainScreen(Screen):

    def start_recording(self):
        print("🔴 Pradėtas įrašymas...")
        self.ids.transcription.text = "Tai pavyzdinis transkribuotas tekstas."

    def clear_text(self):
        self.ids.transcription.text = ""

    def send_to_llm(self):
        self.clear_text()
        # Siuntimas į LLM būtų čia

    def load_statistics(self):
        self.manager.current = "statistics"

    def update_product_list(self):
        product_list = self.ids.product_list
        product_list.clear_widgets()

        for product in PRODUCTS:
            product_button = Button(
                text=f"{product['product_name']} - {product['category']}",
                size_hint_y=None,
                height=40
            )
            product_button.bind(on_release=lambda btn, p=product: self.edit_product(p))
            product_list.add_widget(product_button)

    def add_product(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation="vertical", spacing=10)
        name_input = TextInput(hint_text="Produkto pavadinimas")
        category_input = TextInput(hint_text="Kategorija")

        def save_product():
            if name_input.text and category_input.text:
                PRODUCTS.append({
                    "product_name": name_input.text,
                    "category": category_input.text
                })
                db.add_product(name_input.text, category_input.text)
                self.update_product_list()
                popup.dismiss()

        save_button = Button(text="Išsaugoti", size_hint_y=None, height=40)
        save_button.bind(on_release=lambda x: save_product())

        content.add_widget(name_input)
        content.add_widget(category_input)
        content.add_widget(save_button)

        popup = Popup(title="Pridėti naują produktą", content=content, size_hint=(0.8, 0.5))
        popup.open()

    def edit_product(self, product):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation="vertical", spacing=10)
        name_input = TextInput(text=product['name'])
        category_input = TextInput(text=product['category'])

        def save_changes():
            product['name'] = name_input.text
            product['category'] = category_input.text
            self.update_product_list()
            popup.dismiss()

        def delete_product():
            #db.delete_product()
            self.update_product_list()
            popup.dismiss()

        save_button = Button(text="Atnaujinti", size_hint_y=None, height=40)
        save_button.bind(on_release=lambda x: save_changes())

        delete_button = Button(text="Ištrinti", size_hint_y=None, height=40)
        delete_button.bind(on_release=lambda x: delete_product())

        content.add_widget(name_input)
        content.add_widget(category_input)
        content.add_widget(save_button)
        content.add_widget(delete_button)

        popup = Popup(title="Redaguoti produktą", content=content, size_hint=(0.8, 0.5))
        popup.open()

class MyApp(App):
    def build(self):
        self.db = db
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(StatisticsScreen(name="statistics"))
        return sm

if __name__ == "__main__":
    #db.add_product(
    #    "7day",
    #    "bakery",
    #   datetime.datetime.strptime("2025-03-14 00:00:00", '%Y-%m-%d %H:%M:%S'))
    MyApp().run()
