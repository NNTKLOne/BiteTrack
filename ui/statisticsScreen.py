from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from database.database import Database

# Sukuriame DB objektą
db = Database()

class StatisticsScreen(Screen):

    def on_enter(self):
        self.ids['spinner'].text = 'Visi'
        self.set_filter('Visi')

    def load_statistics_data(self, filter_type):
        stats_list = self.ids.stats_list
        stats_list.clear_widgets()

        try:
            if filter_type == 'Visi':
                products = db.get_all_products()
            elif filter_type == 'Diena':
                products = db.get_products_today()
            elif filter_type == 'Savaitė':
                products = db.get_products_this_week()
            elif filter_type == 'Mėnuo':
                products = db.get_products_this_month()
            else:
                products = []

            if not products:
                stats_list.add_widget(Label(
                    text="Duomenų nerasta.",
                    size_hint_y=None,
                    height=40
                ))
                return

            for product in products:
                row = BoxLayout(size_hint_y=None, height=40, spacing=10)

                product_button = Button(
                    text=f"{product['product_name']}",
                    on_press=lambda btn, p=product: self.edit_product(p)
                )

                delete_button = Button(
                    text="Pašalinti",
                    size_hint_x=None,
                    width=100,
                    on_press=lambda btn, p_id=product['id']: self.confirm_delete_popup(p_id)
                )

                row.add_widget(product_button)
                row.add_widget(delete_button)
                stats_list.add_widget(row)

        except Exception as e:
            self.show_error("Nepavyko užkrauti duomenų. Bandykite dar kartą.")
            print(f"Klaida įkeliant statistiką: {e}")

    def show_error(self, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        label = Label(text=message)
        ok_button = Button(text="Gerai", size_hint_y=None, height=40)

        popup = Popup(title="Klaida", content=content, size_hint=(0.7, 0.3), auto_dismiss=False)
        ok_button.bind(on_release=popup.dismiss)

        content.add_widget(label)
        content.add_widget(ok_button)
        popup.open()

    def confirm_delete_popup(self, product_id):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Ar tikrai norite ištrinti šį produktą?")

        button_row = BoxLayout(spacing=10, size_hint_y=None, height=40)
        yes_button = Button(text="Taip")
        no_button = Button(text="Ne")

        popup = Popup(title="Patvirtinimas", content=content, size_hint=(0.7, 0.4), auto_dismiss=False)

        yes_button.bind(on_release=lambda x: self._delete_and_close(product_id, popup))
        no_button.bind(on_release=lambda x: popup.dismiss())

        button_row.add_widget(yes_button)
        button_row.add_widget(no_button)

        content.add_widget(label)
        content.add_widget(button_row)

        popup.open()

    def show_confirmation(self, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        label = Label(text=message)
        ok_button = Button(text="Gerai", size_hint_y=None, height=40)

        popup = Popup(title="Informacija", content=content, size_hint=(0.6, 0.3), auto_dismiss=False)

        ok_button.bind(on_release=popup.dismiss)
        content.add_widget(label)
        content.add_widget(ok_button)

        popup.open()

    def _delete_and_close(self, product_id, popup):
        db.delete_product(product_id)
        popup.dismiss()
        self.set_filter(self.ids.spinner.text)
        self.show_confirmation("Produktas sėkmingai pašalintas.")

    def edit_product(self, product):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        name_input = TextInput(text=product['product_name'])

        def save_changes(_):
            db.delete_product(product['id'])
            db.add_product(name_input.text)
            self.set_filter(self.ids.spinner.text)
            popup.dismiss()

        def cancel(_):
            popup.dismiss()

        save_btn = Button(text="Atnaujinti", size_hint_y=None, height=40)
        save_btn.bind(on_release=save_changes)

        delete_btn = Button(text="Atšaukti", size_hint_y=None, height=40)
        delete_btn.bind(on_release=cancel)

        content.add_widget(name_input)
        content.add_widget(save_btn)
        content.add_widget(delete_btn)

        popup = Popup(title="Redaguoti produktą", content=content, size_hint=(0.8, 0.5))
        popup.open()

    def set_filter(self, value):
        #  Atnaujiname statistiką pagal pasirinktą filtrą
        self.load_statistics_data(value)

    def go_back(self):
        self.manager.current = "main"