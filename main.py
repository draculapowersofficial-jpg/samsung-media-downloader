import os
import re
import datetime
import threading
from flask import Flask, render_template_string, request, jsonify
import requests
import yt_dlp

DOWNLOAD_DIR = "/sdcard/Download/MyDownloader"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

app = Flask(__name__)
status_message = "Ready to download..."

# Clean Premium Dark Mode HTML/CSS Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Downloader Pro</title>
    <style>
        body { background-color: #121212; color: #FFFFFF; font-family: Helvetica, Arial, sans-serif; padding: 20px; text-align: center; }
        .container { max-width: 450px; margin: 0 auto; background: #1E1E1E; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { font-size: 24px; margin-bottom: 20px; color: #FFFFFF; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 4px; border: none; font-size: 16px; box-sizing: border-box; }
        input, select { background-color: #2D2D2D; color: #FFFFFF; }
        button { background-color: #6200EE; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #3700B3; }
        .status { margin-top: 20px; color: #A0A0A0; font-style: italic; }
        .tab-btn { width: 48%; display: inline-block; background-color: #2D2D2D; margin: 5px 1%; }
        .active-tab { background-color: #6200EE; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Media Downloader Pro</h1>
        <div style="margin-bottom: 20px;">
            <button class="tab-btn active-tab" id="btn-single" onclick="showTab('single')">Single Link</button>
            <button class="tab-btn" id="btn-batch" onclick="showTab('batch')">Batch Mode</button>
        </div>

        <div id="single-view">
            <input type="text" id="url" placeholder="Paste your media link here...">
            <select id="type">
                <option value="Video">Video</option>
                <option value="Audio">Audio</option>
            </select>
            <button onclick="startDownload()">DOWNLOAD NOW</button>
        </div>

        <div id="batch-view" style="display:none;">
            <p style="color: #A0A0A0; font-size: 14px;">Place a file named 'links.txt' in your Download folder with one link per line.</p>
            <button onclick="startBatch()">RUN BATCH FILE</button>
        </div>

        <div class="status" id="status-box">Status: Ready.</div>
    </div>

    <script>
        function showTab(type) {
            if(type === 'single') {
                document.getElementById('single-view').style.display = 'block';
                document.getElementById('batch-view').style.display = 'none';
                document.getElementById('btn-single').classList.add('active-tab');
                document.getElementById('btn-batch').classList.remove('active-tab');
            } else {
                document.getElementById('single-view').style.display = 'none';
                document.getElementById('batch-view').style.display = 'block';
                document.getElementById('btn-single').classList.remove('active-tab');
                document.getElementById('btn-batch').classList.add('active-tab');
            }
        }
        function startDownload() {
            let url = document.getElementById('url').value;
            let type = document.getElementById('type').value;
            document.getElementById('status-box').innerText = "Status: Initializing connection...";
            fetch('/download?url=' + encodeURIComponent(url) + '&type=' + type)
                .then(res => res.json())
                .then(data => alert(data.message));
        }
        function startBatch() {
            document.getElementById('status-box').innerText = "Status: Starting batch processing...";
            fetch('/batch')
                .then(res => res.json())
                .then(data => alert(data.message));
        }
        setInterval(() => {
            fetch('/status').then(res => res.json()).then(data => {
                document.getElementById('status-box').innerText = "Status: " + data.status;
            });
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status')
def get_status():
    global status_message
    return jsonify({"status": status_message})

@app.route('/download')
def download():
    url = request.args.get('url')
    media_type = request.args.get('type')
    threading.Thread(target=process_ytdl, args=(url, media_type), daemon=True).start()
    return jsonify({"message": "Download thread started in background!"})

@app.route('/batch')
def batch():
    batch_file = os.path.join(DOWNLOAD_DIR, "links.txt")
    if os.path.exists(batch_file):
        with open(batch_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        threading.Thread(target=process_batch, args=(urls,), daemon=True).start()
        return jsonify({"message": "Batch sequence initiated!"})
    return jsonify({"message": "Error: links.txt file not found."})

def process_ytdl(url, media_type):
    global status_message
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    status_message = "Downloading..."
    ydl_opts = {'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_{timestamp}.%(ext)s', 'quiet': True}
    if media_type == "Audio":
        ydl_opts.update({'format': 'bestaudio/best'})
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        status_message = "✅ Download complete!"
    except Exception:
        status_message = "❌ Extraction failed."

def process_batch(urls):
    global status_message
    for url in urls:
        process_ytdl(url, "Video")
    status_message = "✅ Batch layout tasks complete!"

if __name__ == '__main__':
    # Starts an internal web app on boot that hooks into standard Android ports
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(host='127.0.0.1', port=5000)
