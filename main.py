import flet as ft
import os
import threading

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def main(page: ft.Page):
    page.title = "Universal Media Player & Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    
    # Configure public download location path
    if os.name == 'posix' and 'ANDROID_ARGUMENT' in os.environ:
        download_path = "/storage/emulated/0/Download/MediaDownloader"
    else:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")
        
    if not os.path.exists(download_path):
        try: os.makedirs(download_path)
        except: pass

    # UI Element Layout Controls
    status_label = ft.Text("Paste a link from YouTube/TikTok below", size=16)
    url_input = ft.TextField(hint_text="Enter video or audio URL link here...", expand=True)
    progress_bar = ft.ProgressBar(value=0, visible=False)
    
    file_list = ft.ListView(expand=True, spacing=5, height=300)

    if yt_dlp is None:
        status_label.value = "🚨 Error: Downloading engine module missing!"
        status_label.color = ft.Colors.RED_400

    # --- REFRESH DOWNLOADED STORAGE LIBRARY ---
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
                        text=f"📁 Play Offline: {f}",
                        on_click=lambda e, path=full_path, name=f: play_file(path, name),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                    )
                )
        page.update()

    def play_file(path, name):
        status_label.value = f"Opening system player for: {name}"
        # Launches the video directly into your Samsung system media app launcher
        page.launch_url(f"file://{path}")
        page.update()

    # --- YT-DLP PROGRESS TRACKING PANEL ---
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

    # --- CORE WORKER THREAD EXTRACTION ENGINE ---
    def run_stream(url):
        if yt_dlp is None: return
        opts = {'format': 'best[ext=mp4]/best', 'nocheckcertificate': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
                title = info.get('title', 'Live Stream')
                status_label.value = f"Streaming: {title[:40]}..."
                progress_bar.visible = False
                # Launches your raw URL stream source directly to view online cleanly
                page.launch_url(stream_url)
        except Exception as e:
            status_label.value = f"Stream failed: {str(e)[:50]}"
            progress_bar.visible = False
        page.update()

    def run_download(url, is_audio):
        if yt_dlp is None: return
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

    # --- ACTION BUTTON EVENT HANDLERS ---
    def start_stream(e):
        if yt_dlp is None: return
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Extracting streaming data..."
        progress_bar.visible = True
        progress_bar.value = None
        page.update()
        threading.Thread(target=run_stream, args=(url,), daemon=True).start()

    def start_download_video(e):
        if yt_dlp is None: return
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Queuing video download..."
        progress_bar.visible = True
        progress_bar.value = 0
        page.update()
        threading.Thread(target=run_download, args=(url, False), daemon=True).start()

    def start_download_audio(e):
        if yt_dlp is None: return
        url = url_input.value.strip()
        if not url: return
        status_label.value = "Queuing audio download..."
        progress_bar.visible = True
        progress_bar.value = 0
        page.update()
        threading.Thread(target=run_download, args=(url, True), daemon=True).start()

    # Layout Assembly Viewports
    page.add(
        status_label,
        ft.Row([url_input]),
        progress_bar,
        ft.Row([
            ft.ElevatedButton("Stream Link", on_click=start_stream, bgcolor=ft.Colors.BLUE_800),
            ft.ElevatedButton("Get Video", on_click=start_download_video, bgcolor=ft.Colors.GREEN_800),
            ft.ElevatedButton("Get MP3", on_click=start_download_audio, bgcolor=ft.Colors.PURPLE_800),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(),
        ft.Text("📁 Saved Offline Files (Tap to play):", weight=ft.FontWeight.BOLD),
        file_list
    )
    
    refresh_library()

ft.app(target=main)
