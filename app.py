from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def home():
    video_data = None
    file_path = None

    if request.method == "POST":
        url = request.form.get("url").strip()
        if not url:
            return render_template("index.html", error="Please enter a valid YouTube URL.")

        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()

            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}.mp4"
            file_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=unique_filename)

            video_data = {
                "title": yt.title,
                "thumbnail": yt.thumbnail_url,
                "author": yt.author,
                "views": f"{yt.views:,}",
                "length": f"{yt.length // 60} min {yt.length % 60} sec",
                "filename": unique_filename,
            }

        except Exception as e:
            return render_template("index.html", error=f"Error: {e}")

    return render_template("index.html", video_data=video_data, file_path=file_path)


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found!", 404


if __name__ == "__main__":
    app.run(debug=True)
