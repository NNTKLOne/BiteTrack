from kivy.uix.screenmanager import Screen


class StatisticsScreen(Screen):

    def go_back(self):
        self.manager.current = "main"