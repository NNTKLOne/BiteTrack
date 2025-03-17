from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

# Laikinas produktų sąrašas (vietoj DB)
PRODUCTS = []

class MainScreen(BoxLayout):

    # Pradėti įrašymą
    def start_recording(self):
        print("🔴 Pradėtas įrašymas...")
        # Čia būtų vieta Whisper API integracijai
        self.ids.transcription.text = "Tai pavyzdinis transkribuotas tekstas."

    # Išvalyti transkribuotą tekstą
    def clear_text(self):
        self.ids.transcription.text = ""

    # Atnaujinti produktų sąrašą
    def update_product_list(self):
        product_list = self.ids.product_list
        product_list.clear_widgets()

        for product in PRODUCTS:
            # Sukuriame mygtuką kiekvienam produktui
            product_button = Button(
                text=f"{product['name']} - {product['category']}",
                size_hint_y=None,
                height=40
            )
            # Pridedame redagavimo galimybę
            product_button.bind(on_release=lambda btn, p=product: self.edit_product(p))
            product_list.add_widget(product_button)

    # Pridėti naują produktą
    def add_product(self):
        content = BoxLayout(orientation="vertical", spacing=10)
        name_input = TextInput(hint_text="Produkto pavadinimas")
        category_input = TextInput(hint_text="Kategorija")

        def save_product():
            if name_input.text and category_input.text:
                PRODUCTS.append({"name": name_input.text, "category": category_input.text})
                self.update_product_list()
                popup.dismiss()

        save_button = Button(text="Išsaugoti", size_hint_y=None, height=40)
        save_button.bind(on_release=lambda x: save_product())

        content.add_widget(name_input)
        content.add_widget(category_input)
        content.add_widget(save_button)

        popup = Popup(title="Pridėti naują produktą", content=content, size_hint=(0.8, 0.5))
        popup.open()

    # Redaguoti arba ištrinti produktą
    def edit_product(self, product):
        content = BoxLayout(orientation="vertical", spacing=10)
        name_input = TextInput(text=product['name'])
        category_input = TextInput(text=product['category'])

        def save_changes():
            product['name'] = name_input.text
            product['category'] = category_input.text
            self.update_product_list()
            popup.dismiss()

        def delete_product():
            PRODUCTS.remove(product)
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
        Builder.load_file("UI.kv")
        return MainScreen()

if __name__ == "__main__":
    MyApp().run()
