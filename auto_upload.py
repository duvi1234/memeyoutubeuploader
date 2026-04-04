import argparse
import base64
import os
import pickle
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from generate_video_portable import generate_video


BASE_DIR = Path(__file__).resolve().parent
STATIC_VIDEO_PATH = BASE_DIR / "static" / "final_video.mp4"
ARCHIVE_DIR = BASE_DIR / "uploads"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv(BASE_DIR / ".env")
TOKEN_PATH = Path(os.getenv("YOUTUBE_TOKEN_FILE", BASE_DIR / "token.pickle"))
CLIENT_SECRETS_PATH = Path(
    os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", BASE_DIR / "client_secrets.json")
)


def write_secret_file_from_env(
    env_name: str, destination: Path, *, base64_encoded: bool
) -> bool:
    value = os.getenv(env_name, "").strip()
    if not value:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    if base64_encoded:
        destination.write_bytes(base64.b64decode(value))
    else:
        destination.write_text(value, encoding="utf-8")
    return True


def get_env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


def build_title(now: datetime) -> str:
    prefix = get_env("YOUTUBE_TITLE_PREFIX", "Meme Short")
    return f"{prefix} | {now.strftime('%Y-%m-%d %H:%M')}"


def build_description(now: datetime) -> str:
    default_lines = [
        "Auto-generated meme short.",
        f"Created at {now.isoformat(timespec='minutes')}.",
        "#shorts #meme #funny",
    ]
    return get_env("YOUTUBE_DESCRIPTION", "\n".join(default_lines))


def get_tags() -> list[str]:
    raw_tags = get_env("YOUTUBE_TAGS", "shorts,meme,funny,viral")
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def get_authenticated_service():
    credentials = None

    write_secret_file_from_env(
        "YOUTUBE_CLIENT_SECRETS_JSON", CLIENT_SECRETS_PATH, base64_encoded=False
    )
    write_secret_file_from_env(
        "YOUTUBE_TOKEN_PICKLE_B64", TOKEN_PATH, base64_encoded=True
    )

    if TOKEN_PATH.exists():
        with TOKEN_PATH.open("rb") as token_file:
            credentials = pickle.load(token_file)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        if not CLIENT_SECRETS_PATH.exists():
            raise FileNotFoundError(
                f"Missing OAuth client file: {CLIENT_SECRETS_PATH}. "
                "Provide client_secrets.json locally or set YOUTUBE_CLIENT_SECRETS_JSON."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRETS_PATH), SCOPES
        )
        credentials = flow.run_local_server(port=0)

        with TOKEN_PATH.open("wb") as token_file:
            pickle.dump(credentials, token_file)

    return build("youtube", "v3", credentials=credentials)


def archive_generated_video(source_path: Path) -> Path:
    if not source_path.exists():
        raise FileNotFoundError(f"Generated video not found at {source_path}")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archived_path = ARCHIVE_DIR / f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    shutil.copy2(source_path, archived_path)
    return archived_path


def upload_video(video_path: Path, title: str, description: str) -> str:
    youtube = get_authenticated_service()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": get_tags(),
                "categoryId": get_env("YOUTUBE_CATEGORY_ID", "24"),
            },
            "status": {
                "privacyStatus": get_env("YOUTUBE_PRIVACY_STATUS", "private"),
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(str(video_path), resumable=True),
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response["id"]


def run_single_cycle() -> Optional[str]:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Generating video...")
    generate_video()
    archived_video = archive_generated_video(STATIC_VIDEO_PATH)
    title = build_title(datetime.now())
    description = build_description(datetime.now())
    video_id = upload_video(archived_video, title, description)
    print(
        f"[{datetime.now().isoformat(timespec='seconds')}] Uploaded {archived_video.name} "
        f"as https://www.youtube.com/watch?v={video_id}"
    )
    return video_id


def run_scheduler(interval_hours: int) -> None:
    interval_seconds = interval_hours * 60 * 60
    while True:
        try:
            run_single_cycle()
        except HttpError as exc:
            print(f"YouTube API error: {exc}")
        except Exception as exc:
            print(f"Automation cycle failed: {exc}")

        next_run = datetime.now().timestamp() + interval_seconds
        readable_time = datetime.fromtimestamp(next_run).isoformat(timespec="seconds")
        print(f"Next upload cycle at {readable_time}")
        time.sleep(interval_seconds)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate meme shorts and upload them to YouTube on a schedule."
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=int(get_env("UPLOAD_INTERVAL_HOURS", "2")),
        help="Hours to wait between uploads when running continuously.",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Generate and upload a single video, then exit.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.run_once:
        run_single_cycle()
    else:
        run_scheduler(args.interval_hours)
