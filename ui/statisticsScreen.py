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

            # Jei nėra duomenų, rodome pranešimą
        if not products:
            stats_list.add_widget(Label(text="Duomenų nerasta", size_hint_y=None, height=40))
            return

        #  Pridedame produktus į GUI
        for product in products:
            product_button = Button(
                text=f"{product['product_name']}",
                size_hint_y=None,
                height=40
            )
            stats_list.add_widget(product_button)

    def set_filter(self, value):
        #  Atnaujiname statistiką pagal pasirinktą filtrą
        self.load_statistics_data(value)

    def go_back(self):
        self.manager.current = "main"