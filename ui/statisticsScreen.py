from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from database.database import Database

# Sukuriame DB objektą
db = Database()

class StatisticsScreen(Screen):

    def on_enter(self):
        self.ids['spinner'].text = 'Visi'
        self.set_filter('Visi')

    def load_statistics_data(self, filter_type):
        #  Išvalome esamus duomenis
        stats_list = self.ids.stats_list
        stats_list.clear_widgets()

        #  Pasirenkame duomenis iš DB pagal filtrą
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
            stats_list.add_widget(Label(text="Duomenų nerasta", size_hint_y=None, height=40))
            return

        #  Pridedame produktus į GUI
        for product in products:
            product_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            product_button = Button(
                text=f"{product['product_name']} - {product['category']}",
                size_hint_x=0.8
            )

            delete_button = Button(
                text="Pašalinti",
                size_hint_x=0.2,
                on_press=lambda btn, p_id=product['id']: self.confirm_delete(p_id)
            )

            product_layout.add_widget(product_button)
            product_layout.add_widget(delete_button)
            stats_list.add_widget(product_layout)

    def confirm_delete(self, product_id):
        # Sukuriame patvirtinimo langą
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Ar tikrai norite ištrinti šį įrašą?")
        button_layout = BoxLayout(spacing=10)

        confirm_button = Button(text="Taip", on_press=lambda btn: self.delete_product(product_id, popup))
        cancel_button = Button(text="Atšaukti", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(label)
        popup_layout.add_widget(button_layout)

        popup = Popup(title="Patvirtinimas", content=popup_layout, size_hint=(0.5, 0.3))
        popup.open()

    def delete_product(self, product_id, popup):
        # Ištriname įrašą iš DB
        db.delete_product(product_id)

        # Uždaryti patvirtinimo langą
        popup.dismiss()

        # Atnaujinti sąrašą
        self.load_statistics_data(self.ids['spinner'].text)

        # Pranešimo langas su "OK" mygtuku
        success_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        success_label = Label(text="Įrašas sėkmingai ištrintas.")

        ok_button = Button(text="OK", size_hint=(1, 0.3))

        # Sukuriame popup langą ir perduodame jam nuorodą, kad mygtukas galėtų jį uždaryti
        success_popup = Popup(title="Sėkminga operacija", size_hint=(0.5, 0.3))
        ok_button.bind(on_press=success_popup.dismiss)

        success_layout.add_widget(success_label)
        success_layout.add_widget(ok_button)

        success_popup.content = success_layout
        success_popup.open()

    def set_filter(self, value):
        #  Atnaujiname statistiką pagal pasirinktą filtrą
        self.load_statistics_data(value)

    def go_back(self):
        self.manager.current = "main"