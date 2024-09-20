import os
import threading
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from yt_dlp import YoutubeDL, DownloadError
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp

Window.size = (360, 640)  # Set window size to simulate a mobile display

KV = '''
ScreenManager:
    DownloaderScreen:

<DownloaderScreen>:
    name: "downloader"

    MDBoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 10

        MDLabel:
            text: "YouTube Video Downloader"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H4"

        MDTextField:
            id: url_input
            hint_text: "Enter YouTube video URL"
            size_hint_y: None
            height: "40dp"

        MDRaisedButton:
            text: "Select Video Quality"
            pos_hint: {"center_x": 0.5}
            on_release: app.open_quality_dropdown()

        MDLabel:
            id: quality_label
            text: "Select Video Quality"
            halign: "center"

        MDRaisedButton:
            text: "Select Destination Folder"
            pos_hint: {"center_x": 0.5}
            on_release: app.select_folder()

        MDLabel:
            id: destination_label
            text: "No folder selected"
            halign: "center"

        MDRaisedButton:
            text: "Download"
            pos_hint: {"center_x": 0.5}
            on_release: app.start_download()

        MDProgressBar:
            id: progress_bar
            value: 0
            size_hint_y: None
            height: dp(4)

        MDLabel:
            id: eta_label
            text: "ETA: N/A"
            halign: "center"
'''


class DownloaderScreen(Screen):
    pass


class DownloaderApp(MDApp):
    destination_folder = ObjectProperty(None)
    selected_height = '720'  # Default to 720p

    def build(self):
        # Load the layout from the KV string
        return Builder.load_string(KV)

    def open_quality_dropdown(self):
        # Define dropdown menu items with video height options
        quality_options = [
            {"text": "1080p", "callback": lambda x: self.set_quality('1080')},
            {"text": "720p", "callback": lambda x: self.set_quality('720')},
            {"text": "480p", "callback": lambda x: self.set_quality('480')},
            {"text": "360p", "callback": lambda x: self.set_quality('360')},
        ]

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": option["text"],
                "on_release": lambda x=option: option["callback"](x)
            } for option in quality_options
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=3,
            max_height=dp(200),
        )
        self.menu.caller = self.root.get_screen('downloader').ids.quality_label
        self.menu.open()

    def set_quality(self, height):
        self.selected_height = height
        self.root.get_screen('downloader').ids.quality_label.text = f"Selected Quality: {height}p"
        self.menu.dismiss()

    def select_folder(self):
        # Open a popup with a file chooser in folder mode
        content = FileChooserListView(path=os.path.expanduser("~"), filters=["*"], dirselect=True)
        select_button = MDRaisedButton(text="Select", on_release=lambda x: self.folder_selected(content.path))
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        layout.add_widget(content)
        layout.add_widget(select_button)
        self.popup = Popup(title="Select Destination Folder", content=layout, size_hint=(0.9, 0.9))
        self.popup.open()

    def folder_selected(self, folder_path):
        if folder_path:
            self.destination_folder = folder_path
            self.root.get_screen('downloader').ids.destination_label.text = self.destination_folder
            self.popup.dismiss()

    def start_download(self):
        # Get the URL and check folder
        url = self.root.get_screen('downloader').ids.url_input.text

        if not url or not self.destination_folder:
            self.show_message("Please enter a URL and select a destination folder.")
            return

        # Start the download in a separate thread to keep UI responsive
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        # Set yt-dlp format dynamically using the selected height and provided pattern
        video_format = f'bv*[height<={self.selected_height}][ext=mp4]+ba*[ext=m4a]'
        ydl_opts = {
            'format': video_format,
            'outtmpl': os.path.join(self.destination_folder, '%(title)s.%(ext)s'),
            'n_threads': 4,  # Limit to 4 threads
            'progress_hooks': [self.progress_hook]
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except DownloadError:
            self.show_message("An error occurred during the download process.")
            return

        self.show_message("Download complete!")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress_percent = d.get('downloaded_bytes', 0) * 100 / d.get('total_bytes', 1)
            # Schedule UI updates via Kivy's clock
            Clock.schedule_once(lambda dt: self.update_progress_bar(progress_percent), 0)

            # Show ETA
            eta = d.get('eta', 'N/A')
            Clock.schedule_once(lambda dt: self.update_eta_label(eta), 0)

        if d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.update_progress_bar(100), 0)
            Clock.schedule_once(lambda dt: self.update_eta_label("Complete"), 0)

    def update_progress_bar(self, value):
        self.root.get_screen('downloader').ids.progress_bar.value = value

    def update_eta_label(self, eta):
        self.root.get_screen(
            'downloader').ids.eta_label.text = f"ETA: {eta} seconds" if eta != 'Complete' else "ETA: Complete"

    def show_message(self, message):
        popup = Popup(
            title="Message",
            content=MDLabel(text=message, halign="center"),
            size_hint=(0.7, 0.3),
        )
        popup.open()


if __name__ == '__main__':
    DownloaderApp().run()
