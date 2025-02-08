from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get("url")
    format = data.get("format", "mp4")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            "format": "bestaudio" if format == "mp3" else "best",
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }] if format == "mp3" else [],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == "mp3":
                filename = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")

        download_url = f"http://127.0.0.1:5000/download/{os.path.basename(filename)}"
        return jsonify({"downloadUrl": download_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
