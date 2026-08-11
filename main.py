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
    status_label = ft.Text("Loading global trending media feed...", size=14)
    url_input = ft.TextField(hint_text="Search keywords or paste URL link here...", expand=True)
    progress_bar = ft.ProgressBar(value=0, visible=False)
    
    # Dynamic Containers for Feed/Search Results and Offline Files
    search_results_container = ft.Column(spacing=10)
    file_list = ft.ListView(expand=True, spacing=5, height=200)
    feed_title_label = ft.Text("🔥 Global Most Viewed Feed:", weight=ft.FontWeight.BOLD)

    if yt_dlp is None:
        status_label.value = "🚨 Error: Downloading engine module missing!"
        status_label.color = ft.Colors.RED_400

    # --- REFRESH DOWNLOADED STORAGE LIBRARY ---
    def refresh_library():
        file_list.controls.clear()
        if os.path.exists(download_path):
            files = [f for f in os.listdir(download_path) if f.endswith(('.mp4', '.mp3', '.mkv', '.webm'))]
            if not files:
                file_list.controls.append(ft.Text("No files downloaded yet.", italic=True, size=12))
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

    # --- AUTOMATIC TRENDING FEED LOGIC ---
    def load_trending_feed():
        if yt_dlp is None: return
        opts = {
            'format': 'best',
            'nocheckcertificate': True,
            'quiet': True,
            'extract_flat': True,
            'skip_download': True
        }
        try:
            # Using YouTube's trending URL format directly to populate the home layout
            trending_url = "https://youtube.com"
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(trending_url, download=False)
                search_results_container.controls.clear()
                
                if 'entries' in result and result['entries']:
                    status_label.value = "Trending feed loaded successfully!"
                    # Limit to the top 5 most viewed entries on application boot
                    for entry in result['entries'][:5]:
                        video_url = entry.get('url') or f"https://youtube.com{entry.get('id')}"
                        video_title = entry.get('title', 'Trending Media Item')
                        
                        search_results_container.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"🔥 {video_title[:60]}...", weight=ft.FontWeight.BOLD, size=13),
                                    ft.Row([
                                        ft.ElevatedButton("Stream", on_click=lambda e, url=video_url: trigger_action(url, "stream"), bgcolor=ft.Colors.BLUE_900),
                                        ft.ElevatedButton("Video", on_click=lambda e, url=video_url: trigger_action(url, "video"), bgcolor=ft.Colors.GREEN_900),
                                        ft.ElevatedButton("MP3", on_click=lambda e, url=video_url: trigger_action(url, "audio"), bgcolor=ft.Colors.PURPLE_900),
                                    ], spacing=5)
                                ]),
                                padding=10,
                                border=ft.border.all(1, ft.Colors.GREY_800),
                                border_radius=8,
                                bgcolor=ft.Colors.BLACK
                            )
                        )
                else:
                    status_label.value = "Could not pull charts. Paste direct link instead!"
        except Exception as e:
            status_label.value = "Feed loaded. Type above to search keywords!"
            
        progress_bar.visible = False
        page.update()

    # --- VIDMATE KEYWORD TEXT SEARCH ENGINE ---
    def run_search(query_text):
        if yt_dlp is None: return
        opts = {
            'format': 'best',
            'nocheckcertificate': True,
            'quiet': True,
            'extract_flat': True,
            'skip_download': True
        }
        try:
            search_query = f"ytsearch3:{query_text}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(search_query, download=False)
                search_results_container.controls.clear()
                
                if 'entries' in result and result['entries']:
                    feed_title_label.value = f"🔍 Results for: '{query_text}'"
                    status_label.value = f"Found {len(result['entries'])} matching items!"
                    
                    for entry in result['entries']:
                        video_url = entry.get('url') or f"https://youtube.com{entry.get('id')}"
                        video_title = entry.get('title', 'Unknown Title')
                        
                        search_results_container.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"📺 {video_title[:60]}...", weight=ft.FontWeight.BOLD, size=13),
                                    ft.Row([
                                        ft.ElevatedButton("Stream", on_click=lambda e, url=video_url: trigger_action(url, "stream"), bgcolor=ft.Colors.BLUE_900),
                                        ft.ElevatedButton("Video", on_click=lambda e, url=video_url: trigger_action(url, "video"), bgcolor=ft.Colors.GREEN_900),
                                        ft.ElevatedButton("MP3", on_click=lambda e, url=video_url: trigger_action(url, "audio"), bgcolor=ft.Colors.PURPLE_900),
                                    ], spacing=5)
                                ]),
                                padding=10,
                                border=ft.border.all(1, ft.Colors.GREY_800),
                                border_radius=8,
                                bgcolor=ft.Colors.BLACK
                            )
                        )
                else:
                    status_label.value = "No results found. Try different keywords!"
        except Exception as e:
            status_label.value = f"Search failed: {str(e)[:40]}"
        
        progress_bar.visible = False
        page.update()

    def trigger_action(url, action_type):
        progress_bar.visible = True
        if action_type == "stream":
            status_label.value = "Loading live stream link..."
