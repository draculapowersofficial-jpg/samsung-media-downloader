import flet as ft
import os
import threading
import yt_dlp

def main(page: ft.Page):
    page.title = "Universal Media Player & Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    
    # Configure download location
    if os.name == 'posix' and 'ANDROID_ARGUMENT' in os.environ:
        download_path = "/storage/emulated/0/Download/MediaDownloader"
    else:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")
        
    if not os.path.exists(download_path):
        try: os.makedirs(download_path)
        except: pass

    # UI Element Widgets
    status_label = ft.Text("Paste a link from YouTube/TikTok below", size=16)
    url_input = ft.TextField(hint_text="Enter video or audio URL link here...", expand=True)
    progress_bar = ft.ProgressBar(value=0, visible=False)
    video_player = ft.Video(expand=True, aspect_ratio=16/9, visible=False)
    
    file_list = ft.ListView(expand=True, spacing=5, height=200)

    # --- REFRESH DOWNLOADED LIBRARY ---
    def refresh_library():
        file_list.controls.clear()
        if os.path.exists(download_path):
            files = [f for f in os.listdir(download_path) if f.endswith(('.mp4', '.mp3', '.mkv', '.webm'))]
            if not files:
                file_list.controls.append(ft.Text("No files downloaded yet.", italic=True))
            for f in files:
                full_path = os.path.join(download_path, f)
                file_list.controls.append(
                    ft.ElevatedButton(
                        text=f"📁 {f}",
                        on_click=lambda e, path=full_path, name=f: play_file(path, name),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                    )
                )
        page.update()

    def play_file(path, name):
        status_label.value = f"Playing Offline: {name}"
        video_player.visible = True
        video_player.playlist = [ft.VideoMedia(path)]
        page.update()

    # --- YT-DLP HOOKS FOR THE PROGRESS BAR ---
    def ytdl_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total
                progress_bar.value = percent
                status_label.value = f"Downloading... {int(percent * 100)}%"
                page.update()
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_label.value = "Processing and converting media..."
            page.update()

    # --- CORE WORKER FUNCTIONS ---
    def run_stream(url):
        opts = {'format': 'best[ext=mp4]/best', 'nocheckcertificate': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
                title = info.get('title', 'Live Stream')
                status_label.value = f"Streaming: {title[:40]}..."
                progress_bar.visible = False
                video_player.visible = True
                video_player.playlist = [ft.VideoMedia(stream_url)]
        except Exception as e:
            status_label.value = f"Stream failed: {str(e)[:50]}"
            progress_bar.visible = False
        page.update()

    def run_download(url, is_audio):
        opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'progress_hooks': [ytdl_hook]
        }
        if is_audio:
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            })
        else:
            opts['format'] = 'best[ext=mp4]/best'
            
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            status_label.value = "Download Complete!"
            refresh_library()
        except Exception as e:
            status_label.value = f"Download failed: {str(e)[:50]}"
        progress_bar.visible = False
        page.update()

    # --- BUTTON TRIGGER EVENTS ---
    def start_stream(e):
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Extracting link data..."
        progress_bar.visible = True
        progress_bar.value = None
        page.update()
        threading.Thread(target=run_stream, args=(url,), daemon=True).start()

    def start_download_video(e):
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Queuing video download..."
        progress_bar.visible = True
        progress_bar.value = 0
        page.update()
        threading.Thread(target=run_download, args=(url, False), daemon=True).start()

    def start_download_audio(e):
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Queuing audio download..."
        progress_bar.visible = True
        progress_bar.value = 0
        page.update()
        threading.Thread(target=run_download, args=(url, True), daemon=True).start()

    # Layout Assembly
    page.add(
        status_label,
        ft.Row([url_input]),
        progress_bar,
        ft.Row([
            ft.ElevatedButton("Stream", on_click=start_stream, bgcolor=ft.Colors.BLUE_800),
            ft.ElevatedButton("Get Video", on_click=start_download_video, bgcolor=ft.Colors.GREEN_800),
            ft.ElevatedButton("Get MP3", on_click=start_download_audio, bgcolor=ft.Colors.PURPLE_800),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(),
        video_player,
        ft.Text("📁 Offline File Library (Tap to play):", weight=ft.FontWeight.BOLD),
        file_list
    )
    
    refresh_library()

ft.app(target=main)
