from flask import Flask, render_template, send_from_directory, jsonify
from generate_video_portable import generate_video
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        generate_video()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/download")
def download():
    return send_from_directory("static", "final_video.mp4", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
