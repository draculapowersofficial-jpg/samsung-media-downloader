import os
import sys
import re
import datetime
import threading

# --- THE MAGIC TRICK: Auto-bundle pure dependencies inside Android storage ---
import subprocess
try:
    import requests
    import yt_dlp
except ImportError:
    # If the app boots and doesn't find them, it forces a quick local install into its own folder
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", os.path.dirname(__file__), "requests", "yt-dlp"])
    import requests
    import yt_dlp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

DOWNLOAD_DIR = "/sdcard/Download/MyDownloader"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

class ModernDownloaderApp(App):
    def build(self):
        self.title = "Media Downloader Pro"
        
        self.bg_dark = get_color_from_hex('#121212')      
        self.bg_card = get_color_from_hex('#1E1E1E')      
        self.accent_purple = get_color_from_hex('#6200EE')  
        self.text_white = get_color_from_hex('#FFFFFF')   
        self.text_dim = get_color_from_hex('#A0A0A0')     

        Window.clearcolor = self.bg_dark
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        title_lbl = Label(text="Media Downloader Pro", font_size='22sp', bold=True, color=self.text_white, size_hint_y=None, height=40)
        main_layout.add_widget(title_lbl)

        self.tabs = TabbedPanel(do_default_tab=False, background_color=self.bg_card)
        
        # --- Single Tab ---
        self.tab_single = TabbedPanelItem(text="Single Link", background_color=self.bg_dark)
        single_box = BoxLayout(orientation='vertical', padding=10, spacing=12)
        single_box.add_widget(Label(text="Paste Media URL below:", color=self.text_dim, size_hint_y=None, height=25))
        
        self.url_input = TextInput(multiline=False, hint_text="Paste your link here...", background_color=self.bg_card, foreground_color=self.text_white, hint_text_color=self.text_dim, size_hint_y=None, height=45)
        single_box.add_widget(self.url_input)
        
        self.type_spinner = Spinner(text="Video", values=("Video", "Audio"), background_color=self.accent_purple, size_hint_y=None, height=45)
        single_box.add_widget(self.type_spinner)
        
        download_btn = Button(text="START DOWNLOAD", background_color=self.accent_purple, bold=True, size_hint_y=None, height=50)
        download_btn.bind(on_press=self.start_single_download)
        single_box.add_widget(download_btn)
        single_box.add_widget(BoxLayout()) 
        self.tab_single.add_widget(single_box)
        
        # --- Batch Tab ---
        self.tab_batch = TabbedPanelItem(text="Batch Mode", background_color=self.bg_dark)
        batch_box = BoxLayout(orientation='vertical', padding=10, spacing=12)
        batch_box.add_widget(Label(text="Reads 'links.txt' from your Downloads folder", color=self.text_dim, font_size='14sp'))
        
        batch_btn = Button(text="RUN BATCH FILE", background_color=self.accent_purple, bold=True, size_hint_y=None, height=50)
        batch_btn.bind(on_press=self.start_batch_download)
        batch_box.add_widget(batch_btn)
        batch_box.add_widget(BoxLayout()) 
        self.tab_batch.add_widget(batch_box)

        self.tabs.add_widget(self.tab_single)
        self.tabs.add_widget(self.tab_batch)
        main_layout.add_widget(self.tabs)

        status_box = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None, height=80)
        self.status_lbl = Label(text="Ready.", color=self.text_dim, font_size='14sp')
        status_box.add_widget(self.status_lbl)
        
        main_layout.add_widget(status_box)
        return main_layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_lbl, 'text', text))

    def start_single_download(self, instance):
        url = self.url_input.text.strip()
        if url:
            threading.Thread(target=self.download_ytdl, args=(url, self.type_spinner.text), daemon=True).start()

    def start_batch_download(self, instance):
        batch_file = os.path.join(DOWNLOAD_DIR, "links.txt")
        if os.path.exists(batch_file):
            with open(batch_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            threading.Thread(target=self.process_batch, args=(urls,), daemon=True).start()
        else:
            self.update_status("Error: links.txt not found in MyDownloader folder.")

    def download_ytdl(self, url, media_type):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.update_status("Downloading...")
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_{timestamp}.%(ext)s',
            'quiet': True
        }
        if media_type == "Audio":
            ydl_opts.update({'format': 'bestaudio/best'})
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.update_status("✅ Download complete!")
        except Exception:
            self.update_status("❌ Extraction failed.")

    def process_batch(self, urls):
        for url in urls:
            self.download_ytdl(url, "Video")
        self.update_status("✅ Batch processing finished!")

if __name__ == '__main__':
    ModernDownloaderApp().run()
