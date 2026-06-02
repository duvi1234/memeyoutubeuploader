import os
from contextlib import suppress
from pathlib import Path


def normalize_imagemagick_binary() -> None:
    imagemagick_binary = os.getenv("IMAGEMAGICK_BINARY", "").strip()
    if not imagemagick_binary:
        return

    path = Path(imagemagick_binary)
    if path.is_dir():
        magick_exe = path / "magick.exe"
        if magick_exe.is_file():
            os.environ["IMAGEMAGICK_BINARY"] = str(magick_exe)


normalize_imagemagick_binary()

import moviepy.config as mpy_conf
import requests
from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, VideoFileClip


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_VIDEO_PATH = BASE_DIR / "assets" / "background_video.mp4"
BACKGROUND_MUSIC_PATH = BASE_DIR / "assets" / "background_music.mp3"
OUTPUT_PATH = BASE_DIR / "static" / "final_video.mp4"
TEMP_DIR = BASE_DIR / "temp"
MEME_API_URL = "https://meme-api.com/gimme"
VIDEO_DURATION_SECONDS = 6


def get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


def get_requests_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = get_env_bool("MEME_API_TRUST_ENV", False)
    return session


def configure_imagemagick() -> None:
    imagemagick_binary = os.getenv("IMAGEMAGICK_BINARY", "").strip()
    if imagemagick_binary:
        os.environ["IMAGEMAGICK_BINARY"] = imagemagick_binary
        mpy_conf.change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary})


def safe_console_text(value) -> str:
    return str(value).encode("ascii", "backslashreplace").decode("ascii")


def fetch_memes(count=2):
    print("Fetching memes...")
    memes = []
    session = get_requests_session()
    for _ in range(count):
        try:
            response = session.get(MEME_API_URL, timeout=20)
            response.raise_for_status()
            payload = response.json()
            memes.append({"url": payload["url"], "title": payload["title"]})
        except Exception as exc:
            print("Failed to fetch meme:", exc)
    if len(memes) < count:
        raise RuntimeError(
            f"Could not fetch {count} meme(s) from {MEME_API_URL}. "
            "If your network requires a proxy, set MEME_API_TRUST_ENV=true."
        )
    return memes


def download_image(url, filename, session):
    try:
        print(f"Downloading meme image from {url}")
        response = session.get(url, timeout=30)
        response.raise_for_status()
        with open(filename, "wb") as file_handle:
            file_handle.write(response.content)
        return filename
    except Exception as exc:
        print("Error downloading image:", exc)
        return None


def generate_video():
    configure_imagemagick()

    memes = fetch_memes(2)
    print("Meme Texts:", [safe_console_text(m["title"]) for m in memes])

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    session = get_requests_session()
    top_img = download_image(memes[0]["url"], TEMP_DIR / "temp_meme1.jpg", session)
    bottom_img = download_image(memes[1]["url"], TEMP_DIR / "temp_meme2.jpg", session)
    if not top_img or not bottom_img:
        raise RuntimeError("Could not download meme images.")

    video = VideoFileClip(str(BACKGROUND_VIDEO_PATH)).subclip(0, VIDEO_DURATION_SECONDS)
    audio = AudioFileClip(str(BACKGROUND_MUSIC_PATH)).subclip(0, VIDEO_DURATION_SECONDS)

    top_y = int(video.h * 0.12)
    bottom_y = int(video.h * 0.65)
    meme_width = video.w * 0.8

    top_clip = (
        ImageClip(str(top_img))
        .resize(width=meme_width)
        .set_duration(video.duration)
        .set_position(("center", top_y))
    )
    bottom_clip = (
        ImageClip(str(bottom_img))
        .resize(width=meme_width)
        .set_duration(video.duration)
        .set_position(("center", bottom_y))
    )

    final = CompositeVideoClip([video, top_clip, bottom_clip]).set_audio(audio)
    temp_audio_path = TEMP_DIR / f"final_video_audio_{os.getpid()}.mp3"

    print("Exporting final video to:", OUTPUT_PATH)
    try:
        final.write_videofile(
            str(OUTPUT_PATH),
            fps=24,
            temp_audiofile=str(temp_audio_path),
            remove_temp=False,
        )
    finally:
        final.close()
        top_clip.close()
        bottom_clip.close()
        audio.close()
        video.close()
        with suppress(OSError):
            temp_audio_path.unlink()


if __name__ == "__main__":
    generate_video()
