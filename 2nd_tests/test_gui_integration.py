# test_gui_integration.py

import os
import pytest
from datetime import datetime
from kivy.base import EventLoop
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from database.database import Database
from ui.statisticsScreen import StatisticsScreen

# Užkrauname KV failą
kv_path = os.path.join(os.path.dirname(__file__), "..", "ui", "UI.kv")
Builder.load_file(kv_path)

@pytest.fixture
def setup_statistics_screen():
    db = Database()
    db.create_tables()

    # Pridedame testinį produktą
    db.add_product("TestProduktas")

    EventLoop.ensure_window()

    sm = ScreenManager()
    screen = StatisticsScreen(name="statistics")
    screen.db = db
    sm.add_widget(screen)
    sm.current = "statistics"

    return screen

def test_product_shown_in_statistics_today(setup_statistics_screen):
    screen = setup_statistics_screen
    screen.load_statistics_data("Diena")

    # Paimame ne tik widget'us, bet ir jų vaikus
    found = False
    for row in screen.ids.stats_list.children:
        for widget in row.children:
            if isinstance(widget, Button) and "TestProduktas" in widget.text:
                found = True
                break

    assert found, "Produktas nebuvo parodytas statistikoje"
