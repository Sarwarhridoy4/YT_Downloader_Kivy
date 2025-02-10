from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from modules.ui_components import MainScreen



Window.size = (360, 640)  # Set window size to simulate a mobile display

class YouTubeDownloaderApp(MDApp):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    YouTubeDownloaderApp().run()
