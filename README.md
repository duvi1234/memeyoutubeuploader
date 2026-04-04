# Meme Shorts Generator 🎥😂

This is a fully automated web app that generates funny meme videos using trending memes, a background video, and music. You can generate and download a ready-to-upload meme short (MP4) in a single click!

## 🚀 Features

- Auto-fetches trending memes via API
- Overlays memes on a background video with music
- Responsive web interface
- Download button appears after generation
- Replaces old video automatically
- Mobile-friendly UI
- Ready for deployment on Render

## 🛠 Tech Stack

- Python 🐍 (Flask, MoviePy)
- HTML5 + CSS3 + JavaScript
- Meme API (`https://meme-api.com/gimme`)
- Responsive Design

## 📁 Folder Structure

project/
│
├── assets/
│ ├── background_video.mp4
│ └── background_music.mp3
│
├── web/
│ ├── index.html
│ └── script.js
│
├── app.py
├── generate_video.py
├── requirements.txt
├── README.md
└── web/final_video.mp4 # Generated output

bash
Copy
Edit

## 🖥️ Local Setup

1. **Clone the Repo**
   ```bash
   git clone https://github.com/your-username/meme-shorts-generator.git
   cd meme-shorts-generator
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the App

bash
Copy
Edit
python app.py
Access in Browser
Open http://127.0.0.1:5000 in your browser.

🌐 Deploy on Render
Create a new Web Service on Render

Connect your GitHub repo

Set the start command: gunicorn app:app

Use Python 3.10+ environment

Add requirements.txt and render.yaml if needed

📦 Requirements
Python 3.8+

moviepy, requests, flask

📜 License
MIT License

🎬 Created for fun, reels, and rapid meme delivery!

yaml
Copy
Edit

---

Let me know if you want a `render.yaml` or deployment screenshot too.

## YouTube Automation

This project now includes [`auto_upload.py`](/d:/meme_shorts_project/auto_upload.py), which:

- generates a new meme short
- copies the rendered file into an `uploads/` archive
- uploads it to YouTube
- repeats every 2 hours by default

### One-time setup

1. Create a Google Cloud project.
2. Enable the YouTube Data API v3.
3. Create an OAuth Desktop App client.
4. Download the OAuth JSON file and save it in the project root as `client_secrets.json`.
5. Copy `.env.example` to `.env` and update the values you want.

### Run one upload now

```bash
python auto_upload.py --run-once
```

The first run will open a browser window so you can sign in to the YouTube channel and grant upload access. After that, the OAuth token is stored in `token.pickle`.

### Run continuously every 2 hours

```bash
python auto_upload.py
```

You can change the interval with either:

- `UPLOAD_INTERVAL_HOURS=2` in `.env`
- `python auto_upload.py --interval-hours 2`

### Windows recommendation

If you want this to keep running automatically even after reboots, the most reliable setup on Windows is Task Scheduler running:

```bash
python auto_upload.py --run-once
```

every 2 hours.

## GitHub Actions Setup

This repo now includes the workflow [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml), which runs:

- manually from the GitHub Actions tab
- automatically every 2 hours at `0 */2 * * *` UTC

### What changed for GitHub Actions

- [`auto_upload.py`](/d:/meme_shorts_project/auto_upload.py) can now read YouTube OAuth data from GitHub Secrets.
- [`generate_video_portable.py`](/d:/meme_shorts_project/generate_video_portable.py) removes the Windows-only dependency path so the upload job can run on Ubuntu.
- [`app.py`](/d:/meme_shorts_project/app.py) now uses the portable generator too.

### Step-by-step launch instructions

1. Put this project in a GitHub repository.
2. On your local machine, keep `client_secrets.json` in the project root.
3. Run one local auth flow so Google creates a valid `token.pickle`:

```bash
python auto_upload.py --run-once
```

4. In GitHub, open your repository and go to `Settings` -> `Secrets and variables` -> `Actions`.
5. Create this secret:

- `YOUTUBE_CLIENT_SECRETS_JSON`
  Paste the full contents of your local `client_secrets.json`.

6. Create this secret too:

- `YOUTUBE_TOKEN_PICKLE_B64`
  Paste the base64 version of your local `token.pickle`.

On Windows PowerShell, generate that value with:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle"))
```

7. Optional: add repository variables in the same GitHub settings page:

- `YOUTUBE_PRIVACY_STATUS`
- `YOUTUBE_CATEGORY_ID`
- `YOUTUBE_TITLE_PREFIX`
- `YOUTUBE_DESCRIPTION`
- `YOUTUBE_TAGS`

If you skip them, the script uses defaults.

8. Commit and push these files to GitHub:

- [`auto_upload.py`](/d:/meme_shorts_project/auto_upload.py)
- [`generate_video_portable.py`](/d:/meme_shorts_project/generate_video_portable.py)
- [`app.py`](/d:/meme_shorts_project/app.py)
- [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml)

9. In GitHub, open the `Actions` tab.
10. Open the `YouTube Upload` workflow.
11. Click `Run workflow` to test one upload immediately.
12. If the test succeeds, leave the workflow enabled and GitHub Actions will run it every 2 hours automatically.

### Important notes

- GitHub Actions schedules use UTC, not your local timezone.
- Scheduled workflows can start a little later than the exact minute.
- If you revoke Google access or the refresh token stops working, create a fresh `token.pickle` locally and update the `YOUTUBE_TOKEN_PICKLE_B64` secret.
