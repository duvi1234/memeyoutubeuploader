import requests
import os
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip
)

# Paths
ASSETS_DIR = "assets"
OUTPUT_DIR = "static"
BACKGROUND_VIDEO = os.path.join(ASSETS_DIR, "background_video.mp4")
MUSIC_FILE = os.path.join(ASSETS_DIR, "music.mp3")
FONT_FILE = os.path.join(ASSETS_DIR, "IMPACT.TTF")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "final_video.mp4")
VIDEO_DURATION_SECONDS = 6

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Fetch meme text
def get_meme_text():
    try:
        response = requests.get("https://meme-api.com/gimme")
        data = response.json()
        return data.get("title", "Funny meme")  # fallback
    except Exception as e:
        print("Error fetching meme:", e)
        return "When memes automate themselves."

# Step 2: Create meme short video
def create_meme_short(meme_text):
    print("Generating meme short...")
    
    # Load background video
    video = VideoFileClip(BACKGROUND_VIDEO).subclip(0, VIDEO_DURATION_SECONDS)

    # Load music (optional)
    music = AudioFileClip(MUSIC_FILE).subclip(0, video.duration)
    video = video.set_audio(music)

    # Create text overlay
    text_clip = TextClip(
        txt=meme_text,
        fontsize=70,
        font=FONT_FILE,
        color='white',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(video.w - 100, None)
    ).set_duration(video.duration).set_position(("center", "bottom"))

    # Combine video + text
    final = CompositeVideoClip([video, text_clip])
    
    # Export
    final.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac')
    print("Video created:", OUTPUT_VIDEO)

if __name__ == "__main__":
    meme_text = get_meme_text()
    create_meme_short(meme_text)
