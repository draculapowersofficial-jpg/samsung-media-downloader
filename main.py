import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class MediaDownloaderApp(App):
    def build(self):
        self.title = "Universal Media Player & Downloader"
        
        # Base UI layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status Label
        self.status_label = Label(
            text="Paste a link from YouTube/TikTok, or browse downloaded files below", 
            size_hint_y=0.08,
            halign="center"
        )
        self.layout.add_widget(self.status_label)
        
        # Link Input Field
        self.url_input = TextInput(
            hint_text="Enter video or audio URL link here...", 
            multiline=False, 
            size_hint_y=0.08
        )
        self.layout.add_widget(self.url_input)
        
        # Visual Progress Bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=0.04)
        self.layout.add_widget(self.progress_bar)
        
        # Action Buttons for Online Links
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        self.stream_btn = Button(text="Stream Link", on_press=self.start_stream)
        self.download_video_btn = Button(text="Download Video", on_press=self.start_video_download)
        self.download_audio_btn = Button(text="Download MP3", on_press=self.start_audio_download)
        
        self.button_layout.add_widget(self.stream_btn)
        self.button_layout.add_widget(self.download_video_btn)
        self.button_layout.add_widget(self.download_audio_btn)
        self.layout.add_widget(self.button_layout)
        
        # Middle Split: Video Player (Top) & Offline File Browser (Bottom)
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=0.72, spacing=10)
        
        # Native Video Player
        self.video_player = Video(source='', state='stop', options={'eos': 'loop'}, size_hint_y=0.6)
        self.content_layout.add_widget(self.video_player)
        
        # Offline File Browser container
        self.browser_container = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=5)
        self.browser_label = Label(text="📁 Saved Offline Files (Tap to play):", size_hint_y=0.2, halign="left")
        self.browser_container.add_widget(self.browser_label)
        
        self.scroll_view = ScrollView(size_hint_y=0.8)
        self.file_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.file_list_layout.bind(minimum_height=self.file_list_layout.setter('height'))
        self.scroll_view.add_widget(self.file_list_layout)
        self.browser_container.add_widget(self.scroll_view)
        
        self.content_layout.add_widget(self.browser_container)
        self.layout.add_widget(self.content_layout)
        
        # Configure storage paths for your Samsung phone
        if platform == 'android':
            self.download_path = "/storage/emulated/0/Download/MediaDownloader"
        else:
            self.download_path = os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")
            
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
            except Exception:
                pass

        # Load your offline downloaded library right away on startup
        self.refresh_offline_library()

        return self.layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def update_progress(self, percent):
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', percent))

    # --- OFFLINE FILE BROWSER LOGIC ---
    def refresh_offline_library(self):
        self.file_list_layout.clear_widgets()
        if not os.path.exists(self.download_path):
            return
            
        files = [f for f in os.listdir(self.download_path) if f.endswith(('.mp4', '.mp3', '.mkv', '.webm'))]
        
        if not files:
            lbl = Label(text="No files downloaded yet.", size_hint_y=None, height=40)
            self.file_list_layout.add_widget(lbl)
            return

        for filename in files:
            full_path = os.path.join(self.download_path, filename)
            btn = Button(
                text=filename, 
                size_hint_y=None, 
                height=45, 
                background_color=(0.2, 0.6, 0.8, 1),
                halign="center"
            )
            btn.bind(on_press=lambda instance, path=full_path: self.play_offline_file(path))
            self.file_list_layout.add_widget(btn)

    def play_offline_file(self, file_path):
        self.video_player.unload()
        self.video_player.source = file_path
        self.video_player.state = 'play'
        filename = os.path.basename(file_path)
        self.update_status(f"Playing Offline File: {filename}")

    # --- YT-DLP HOOKS FOR REAL-TIME PROGRESS BAR ---
    def ytdl_progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = (downloaded / total) * 100
                self.update_progress(percent)
                self.update_status(f"Downloading... {int(percent)}%")
        elif d['status'] == 'finished':
            self.update_progress(100)
            self.update_status("Processing file conversion...")

    # --- ONLINE STREAMING LOGIC ---
    def start_stream(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("Error: Please paste a valid link first!")
            return
        self.update_status("Extracting live stream URL...")
        self.update_progress(15)
        threading.Thread(target=self._async_stream, args=(url,), daemon=True).start()

    def _async_stream(self, url):
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'nocheckcertificate': True,
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
                title = info.get('title', 'Video Stream')
                
                self.update_status(f"Streaming live: {title[:30]}...")
                self.update_progress(100)
                Clock.schedule_once(lambda dt: self._play_video(stream_url))
        except Exception as e:
            self.update_status(f"Streaming failed: {str(e)[:40]}")
            self.update_progress(0)

    def _play_video(self, stream_url):
        self.video_player.unload()
        self.video_player.source = stream_url
        self.video_player.state = 'play'

    # --- DOWNLOADING LOGIC ---
    def start_video_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            return
        self.update_status("Queuing download...")
        self.update_progress(0)
        opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'progress_hooks': [self.ytdl_progress_hook]
        }
        threading.Thread(target=self._async_download, args=(url, opts), daemon=True).start()

    def start_audio_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            return
        self.update_status("Queuing audio download...")
        self.update_progress(0)
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'progress_hooks': [self.ytdl_progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        threading.Thread(target=self._async_download, args=(url, opts), daemon=True).start()

    def _async_download(self, url, opts):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.update_status("Download Complete!")
            Clock.schedule_once(lambda dt: self.refresh_offline_library())
        except Exception as e:
            self.update_status(f"Download failed: {str(e)[:40]}")

if __name__ == '__main__':
    MediaDownloaderApp().run()
