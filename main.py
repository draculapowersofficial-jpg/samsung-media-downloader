import os
import re
import datetime
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import yt_dlp

# --- Optimized for Android Pydroid 3 (Stable) ---
DOWNLOAD_DIR = "/sdcard/Download/MyDownloader"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

class MobileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Downloader Pro")
        self.root.geometry("450x670")
        
        # --- Stable Dark Mode Colors ---
        self.bg_dark = "#121212"       
        self.bg_card = "#1E1E1E"       
        self.accent_purple = "#6200EE" 
        self.text_white = "#FFFFFF"    
        self.text_dim = "#A0A0A0"      
        
        self.root.configure(bg=self.bg_dark)
        self.create_widgets()
        
    def create_widgets(self):
        # UI Setup using basic Tkinter to prevent native graphic crashes
        tk.Label(self.root, text="Media Downloader Pro", font=("Helvetica", 18, "bold"), bg=self.bg_dark, fg=self.text_white).pack(pady=20)
        
        # Tab bar (Simulated with Frame)
        self.tab_bar = tk.Frame(self.root, bg=self.bg_card)
        self.tab_bar.pack(fill="x", padx=15, pady=5)
        
        # Action Buttons
        self.btn_single = tk.Button(self.tab_bar, text="Single Link", bg=self.accent_purple, fg=self.text_white, bd=0, command=self.show_single_view)
        self.btn_single.pack(side="left", fill="x", expand=True)
        
        self.btn_batch = tk.Button(self.tab_bar, text="Batch Mode", bg=self.bg_card, fg=self.text_dim, bd=0, command=self.show_batch_view)
        self.btn_batch.pack(side="right", fill="x", expand=True)

        self.view_container = tk.Frame(self.root, bg=self.bg_dark)
        self.view_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Panes
        self.single_view = tk.Frame(self.view_container, bg=self.bg_dark)
        self.batch_view = tk.Frame(self.view_container, bg=self.bg_dark)
        text="View Downloads Folder"
        self.build_single_layout()
        self.build_batch_layout()
        self.show_single_view()

        # Status Footer
        progress_frame = tk.LabelFrame(self.root, text=" Download Status ", bg=self.bg_dark, fg=self.text_white)
        progress_frame.pack(fill="x", padx=15, pady=15)
        
        self.status_lbl = tk.Label(progress_frame, text="Ready...", bg=self.bg_dark, fg=self.text_dim)
        self.status_lbl.pack(pady=10)
        
        # Storage Location
        tk.Button(self.root, text="📁 View Downloads", bg=self.accent_purple, fg=self.text_white, bd=0, command=self.show_file_location).pack(pady=10, padx=15, fill="x")

    def build_single_layout(self):
        tk.Label(self.single_view, text="URL:", bg=self.bg_dark, fg=self.text_white).pack(anchor="w")
        self.url_entry = tk.Entry(self.single_view, bg=self.bg_card, fg=self.text_white, insertbackground="white")
        self.url_entry.pack(fill="x", pady=5)
        
        self.type_var = tk.StringVar(value="Video")
        tk.OptionMenu(self.single_view, self.type_var, "Video", "Audio").pack(fill="x", pady=5)
        
        tk.Button(self.single_view, text="Download", bg=self.accent_purple, fg=self.text_white, command=self.start_single_download).pack(pady=20, fill="x")

    def build_batch_layout(self):
        tk.Label(self.batch_view, text="Create 'links.txt' in Downloads", bg=self.bg_dark, fg=self.text_dim).pack()
        tk.Button(self.batch_view, text="Run Batch", bg=self.accent_purple, fg=self.text_white, command=self.start_batch_download).pack(pady=20, fill="x")

    def show_single_view(self):
        self.batch_view.pack_forget()
        self.single_view.pack(fill="both", expand=True)

    def show_batch_view(self):
        self.single_view.pack_forget()
        self.batch_view.pack(fill="both", expand=True)

    # --- Core Logic & Threading ---
    def generate_filename(self, url, ext=".mp4"):
        return f"Download_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

    def show_file_location(self):
        messagebox.showinfo("Path", f"Files saved to: {DOWNLOAD_DIR}")

    def start_single_download(self):
        url = self.url_entry.get().strip()
        if url:
            threading.Thread(target=self.download_with_ytdl, args=(url, self.type_var.get()), daemon=True).start()

    def start_batch_download(self):
        file_path = os.path.join(DOWNLOAD_DIR, "links.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                threading.Thread(target=self.process_batch, args=(urls,), daemon=True).start()
        else:
            messagebox.showwarning("Error", "links.txt not found")

    def download_with_ytdl(self, url, media_type):
        self.update_status("Starting...")
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if media_type == "Audio" else 'bestvideo+bestaudio/best',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.update_status("Finished!")
        except Exception as e:
            self.update_status(f"Error: {e}")

    def process_batch(self, urls):
        for url in urls:
            self.download_with_ytdl(url, "Video")
        messagebox.showinfo("Done", "Batch finished")

    def update_status(self, text):
        self.root.after(0, lambda: self.status_lbl.config(text=text))

if __name__ == "__main__":
    window = tk.Tk()
    app = MobileDownloaderApp(window)
    window.mainloop()
