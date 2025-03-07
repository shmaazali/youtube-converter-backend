from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os

cookies_content = os.getenv("YOUTUBE_COOKIES")
with open("youtube_cookies.txt", "w") as f:
    f.write(cookies_content)
    
    
app = Flask(__name__)
CORS(app, origins=["https://trustwavetrade.com"])

# Directory to save downloaded files
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Global variable to store download progress
download_progress = {"status": "idle", "percentage": 0}

# Progress hook for yt-dlp
def progress_hook(d):
    if d['status'] == 'downloading':
        percent_str = d['_percent_str'].strip()
        percentage = int(float(percent_str.replace('%', '')))
        download_progress["status"] = "downloading"
        download_progress["percentage"] = percentage
    elif d['status'] == 'finished':
        download_progress["status"] = "finished"
        download_progress["percentage"] = 100

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data['url']
    format = data['format']

    # Reset progress
    download_progress["status"] = "starting"
    download_progress["percentage"] = 0

    output_file = f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s"

    # yt-dlp options
"""    ydl_opts = {
        "format": "bestaudio/best" if format == "mp3" else "bestvideo+bestaudio/best",
        "outtmpl": output_file,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ] if format == "mp3" else [],
        "cookies": "cookies.txt",  # Uses cookies for restricted videos
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "progress_hooks": [progress_hook],
    }"""
    ydl_opts = {
    "format": "bestaudio/best" if format == "mp3" else "bestvideo+bestaudio/best",
    "outtmpl": output_file,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ] if format == "mp3" else [],
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "cookies": "youtube_cookies.txt",

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Get the name of the downloaded file
        downloaded_files = os.listdir(DOWNLOAD_FOLDER)
        if not downloaded_files:
            return jsonify({"error": "No file was downloaded."})

        downloaded_file = max([f"{DOWNLOAD_FOLDER}/{f}" for f in downloaded_files], key=os.path.getctime)
        filename = os.path.basename(downloaded_file)

        return jsonify({"downloadUrl": f"/download/{filename}", "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify(download_progress)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
