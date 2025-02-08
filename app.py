from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
import os
import yt_dlp

app = Flask(__name__)

CORS(app)

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url or not format:
        return jsonify({"error": "URL and format are required"}), 400

    output_file = f"downloads/output.{format}"
    
    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else 'best',
        'outtmpl': output_file,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}] if format == 'mp3' else []
    }

    os.makedirs("downloads", exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return jsonify({"downloadUrl": f"/download/{format}"})


@app.route('/download/<format>', methods=['GET'])
def download_file(format):
    return send_file(f"downloads/output.{format}", as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
