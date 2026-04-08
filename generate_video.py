import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

import requests
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
)
import moviepy.config as mpy_conf

# Fix ImageMagick path
mpy_conf.change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
})

# Paths
BACKGROUND_VIDEO_PATH = "assets/background_video.mp4"
BACKGROUND_MUSIC_PATH = "assets/background_music.mp3"
OUTPUT_PATH = "static/final_video.mp4"

MEME_API_URL = "https://meme-api.com/gimme"
VIDEO_DURATION_SECONDS = 6

def fetch_memes(count=2):
    print("📥 Fetching memes...")
    memes = []
    for _ in range(count):
        try:
            res = requests.get(MEME_API_URL).json()
            memes.append({"url": res["url"], "title": res["title"]})
        except Exception as e:
            print("❌ Failed to fetch meme:", e)
            memes.append({"url": None, "title": "Funny Meme!"})
    return memes

def download_image(url, filename):
    try:
        print(f"⬇️ Downloading meme image from {url}")
        img_data = requests.get(url).content
        with open(filename, "wb") as f:
            f.write(img_data)
        return filename
    except Exception as e:
        print("❌ Error downloading image:", e)
        return None

def generate_video():
    memes = fetch_memes(2)
    print("🧠 Meme Texts:", [m["title"] for m in memes])

    video = VideoFileClip(BACKGROUND_VIDEO_PATH).subclip(0, VIDEO_DURATION_SECONDS)
    audio = AudioFileClip(BACKGROUND_MUSIC_PATH).subclip(0, VIDEO_DURATION_SECONDS)

    meme_width = video.w * 0.8
    meme_height = video.h * 0.50
    padding_y = 50  # Space from top and bottom

    top_img = download_image(memes[0]["url"], "temp_meme1.jpg")
    bottom_img = download_image(memes[1]["url"], "temp_meme2.jpg")

        # Adjusted Y positions to center better visually (not too close to edges)
    top_y = int(video.h * 0.12)     # 12% from the top
    bottom_y = int(video.h * 0.65)  # 65% from the top

    top_clip = (
        ImageClip(top_img)
        .resize(width=meme_width)
        .set_duration(video.duration)
        .set_position(("center", top_y))
    )

    bottom_clip = (
        ImageClip(bottom_img)
        .resize(width=meme_width)
        .set_duration(video.duration)
        .set_position(("center", bottom_y))
    )


    final = CompositeVideoClip([video, top_clip, bottom_clip]).set_audio(audio)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print("💾 Exporting final video to:", OUTPUT_PATH)
    final.write_videofile(OUTPUT_PATH, fps=24)

if __name__ == "__main__":
    generate_video()
