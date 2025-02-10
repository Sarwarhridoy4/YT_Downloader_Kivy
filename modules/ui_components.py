from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from modules.download_manager import download_video
from modules.utils import validate_url, fetch_video_info
import ffmpeg


class MainScreen(Screen):
    url_input = StringProperty("")
    destination_folder = StringProperty("")
    selected_quality = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(0.9, None),
            height=600,
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        self.title_label = MDLabel(
            text="YouTube Video Downloader",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.title_label)

        self.url_input_field = MDTextField(
            hint_text="Enter YouTube video URL",
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.url_input_field)

        self.quality_button = MDRaisedButton(
            text="Select Video Quality",
            on_release=self.open_quality_dropdown,
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.quality_button)

        self.quality_label = MDLabel(
            text="Select Video Quality",
            halign="center",
            size_hint_y=None,
            height=30
        )
        self.layout.add_widget(self.quality_label)

        self.select_folder_button = MDRaisedButton(
            text="Select Destination Folder",
            on_release=self.select_folder,
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.select_folder_button)

        self.destination_label = MDLabel(
            text="No folder selected",
            halign="center",
            size_hint_y=None,
            height=30
        )
        self.layout.add_widget(self.destination_label)

        self.download_button = MDRaisedButton(
            text="Download",
            on_release=self.start_download,
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.download_button)

        self.progress_bar = MDProgressBar(
            value=0,
            size_hint_y=None,
            height=20
        )
        self.layout.add_widget(self.progress_bar)

        self.eta_label = MDLabel(
            text="ETA: N/A",
            halign="center",
            size_hint_y=None,
            height=30
        )
        self.layout.add_widget(self.eta_label)

        self.add_widget(self.layout)

    def show_popup(self, title, message, color):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()

    def open_quality_dropdown(self, *args):
        url = self.url_input_field.text
        if validate_url(url):
            video_info = fetch_video_info(url)
            formats = video_info.get('formats', [])
            if not formats:
                self.show_popup("Error", "No formats available.", "red")
                return

            # Define updated quality categories based on yt-dlp official examples
            quality_options = [
                {"text": "Best Quality (Auto Merge)", "format": "bv*+ba/b"},
                {"text": "Best Quality (Forced Merge)", "format": "bv+ba/b"},
                {"text": "Medium Quality (720p max)", "format": "bestvideo[height<=720]+bestaudio/best"},
                {"text": "Low Quality", "format": "worst"}
            ]

            # Create menu items for each quality category
            menu_items = [
                {
                    "viewclass": "OneLineListItem",
                    "text": option["text"],
                    "on_release": lambda x=option: self.set_quality(x['format'])
                }
                for option in quality_options
            ]

            self.menu = MDDropdownMenu(
                caller=self.quality_button,
                items=menu_items,
                width_mult=4,
            )
            self.menu.open()
        else:
            self.show_popup("Error", "Invalid URL.", "red")

    def set_quality(self, quality_id):
        self.selected_quality = quality_id
        self.quality_label.text = f"Selected Quality: {quality_id}"
        self.menu.dismiss()

    def select_folder(self, *args):
        self.file_manager = MDFileManager(select_path=self.set_destination_folder)
        self.file_manager.show('/')

    def set_destination_folder(self, path):
        self.destination_folder = path
        self.destination_label.text = f"Folder: {path}"
        self.file_manager.close()

    def start_download(self, *args):
        url = self.url_input_field.text
        if validate_url(url) and self.selected_quality and self.destination_folder:
            # Update output template to always produce a .mp4 file
            output_template = f"{self.destination_folder}/%(title)s.mp4"
            download_video(url, self.selected_quality, output_template, self.update_progress)
            self.show_popup("Info", "Download initiated.", "blue")
        else:
            self.show_popup("Warning", "Invalid URL or no quality/folder selected.", "orange")

    def update_progress(self, progress_info):
        if progress_info.get('status') == 'downloading':
            downloaded = progress_info.get('downloaded_bytes', 0)
            total = progress_info.get('total_bytes', 1)
            self.progress_bar.value = (downloaded / total) * 100
            self.eta_label.text = f"ETA: {progress_info.get('eta', 'N/A')}"
        elif progress_info.get('status') == 'finished':
            self.progress_bar.value = 100
            self.show_popup("Success", "Download completed.", "green")
            # Ensure the file is in .mp4 format
            self.ensure_mp4_format(progress_info['filename'])

    def ensure_mp4_format(self, input_path):
        if not input_path.endswith('.mp4'):
            output_path = input_path.replace('.webm', '.mp4')
            try:
                ffmpeg.input(input_path).output(output_path, vcodec='libx264').run()
                self.show_popup("Success", "Converted to MP4 successfully.", "green")
            except Exception as e:
                self.show_popup("Error", f"Conversion to MP4 failed: {e}", "red")
