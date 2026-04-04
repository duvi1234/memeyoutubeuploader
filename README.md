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

This repo now includes the workflow [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml), which can:

- run manually from the GitHub Actions tab
- run automatically every 2 hours at `0 */2 * * *` UTC
- generate a meme video
- optionally upload it to YouTube
- email the MP4 if it is small enough
- email a GitHub Actions run link if the MP4 is too large to attach

### Files used by the automation

- [`auto_upload.py`](/d:/meme_shorts_project/auto_upload.py): main automation script
- [`generate_video_portable.py`](/d:/meme_shorts_project/generate_video_portable.py): Linux-friendly video generator for GitHub Actions
- [`app.py`](/d:/meme_shorts_project/app.py): Flask app, now using the portable generator
- [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml): scheduled GitHub Actions workflow
- [`.env.example`](/d:/meme_shorts_project/.env.example): example config values

## Full Step-By-Step Implementation

### 1. Prepare the project locally

1. Make sure these files exist in your project:
   - [`assets/background_video.mp4`](/d:/meme_shorts_project/assets/background_video.mp4)
   - [`assets/background_music.mp3`](/d:/meme_shorts_project/assets/background_music.mp3)
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. If you want local testing, start the app or run the automation once:

```bash
python app.py
```

or:

```bash
python auto_upload.py --run-once
```

### 2. Create a GitHub repository

1. Create a new repository on GitHub.
2. Push this project to that repository.
3. Make sure these files are committed:
   - [`auto_upload.py`](/d:/meme_shorts_project/auto_upload.py)
   - [`generate_video_portable.py`](/d:/meme_shorts_project/generate_video_portable.py)
   - [`app.py`](/d:/meme_shorts_project/app.py)
   - [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml)
   - [`.env.example`](/d:/meme_shorts_project/.env.example)

### 3. Set up email delivery

This is the easiest way to use the project because YouTube credentials are optional.

1. Open your GitHub repository.
2. Go to `Settings` -> `Secrets and variables` -> `Actions`.
3. Under `Secrets`, add:
   - `SMTP_HOST`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
4. Under `Variables`, add:
   - `EMAIL_TO`
   - `EMAIL_FROM`
   - `EMAIL_SUBJECT_PREFIX`
   - `EMAIL_ATTACHMENT_MAX_MB`
   - `SMTP_PORT`
   - `SMTP_USE_TLS`

Recommended values:

- `EMAIL_TO`: your email address
- `EMAIL_FROM`: usually the same as your SMTP username
- `EMAIL_SUBJECT_PREFIX`: `Meme Short Ready`
- `EMAIL_ATTACHMENT_MAX_MB`: `20`
- `SMTP_PORT`: `587`
- `SMTP_USE_TLS`: `true`

Example for Gmail SMTP:

- `SMTP_HOST`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SMTP_USERNAME`: your Gmail address
- `SMTP_PASSWORD`: a Gmail App Password, not your normal Gmail password

### 4. Optional: set up YouTube upload

If you only want the email feature, skip this section.

If you also want YouTube uploads, you still need Google OAuth credentials.

1. Put `client_secrets.json` in the project root on your local machine.
2. Run this locally one time:

```bash
python auto_upload.py --run-once
```

3. Sign in with your Google account in the browser window.
4. After that, a local `token.pickle` file will be created.
5. In GitHub `Settings` -> `Secrets and variables` -> `Actions`, add this secret:
   - `YOUTUBE_CLIENT_SECRETS_JSON`
6. Paste the full contents of `client_secrets.json` into that secret.
7. Convert `token.pickle` to base64 in PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle"))
```

8. Create another GitHub secret:
   - `YOUTUBE_TOKEN_PICKLE_B64`
9. Paste the base64 output into that secret.
10. Optional GitHub variables for YouTube:
   - `YOUTUBE_PRIVACY_STATUS`
   - `YOUTUBE_CATEGORY_ID`
   - `YOUTUBE_TITLE_PREFIX`
   - `YOUTUBE_DESCRIPTION`
   - `YOUTUBE_TAGS`

Recommended values:

- `YOUTUBE_PRIVACY_STATUS`: `private`
- `YOUTUBE_CATEGORY_ID`: `24`
- `YOUTUBE_TITLE_PREFIX`: `Meme Short`
- `YOUTUBE_DESCRIPTION`: `Auto-generated meme short. #shorts #meme #funny`
- `YOUTUBE_TAGS`: `shorts,meme,funny,viral`

### 5. Run the workflow manually the first time

1. Open the `Actions` tab in GitHub.
2. Click the `YouTube Upload` workflow.
3. Click `Run workflow`.
4. Wait for the job to finish.
5. Check your email.
6. If the video was small enough, it will be attached.
7. If the video was too large, the email will include the GitHub Actions run link.
8. If YouTube credentials were added, also check your YouTube account for the uploaded video.

### 6. Let it run automatically every 2 hours

You do not need to do anything else after the first successful run.

The workflow in [`youtube-upload.yml`](/d:/meme_shorts_project/.github/workflows/youtube-upload.yml#L1) is already scheduled for:

```yaml
0 */2 * * *
```

That means every 2 hours in UTC.

### 7. How the email fallback works

1. The workflow generates `static/final_video.mp4`.
2. The script checks the file size.
3. If the size is less than or equal to `EMAIL_ATTACHMENT_MAX_MB`, it sends the video as an email attachment.
4. If the size is bigger, it sends an email with the GitHub Actions run link.
5. The workflow also uploads the MP4 as a GitHub Actions artifact and keeps it for 7 days.

### 8. Troubleshooting

- If you do not receive email, check `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_TO`, and `SMTP_PORT`.
- If you use Gmail, make sure you use an App Password.
- If the GitHub workflow fails, open the failed run in the `Actions` tab and read the logs.
- If YouTube upload stops working later, create a fresh `token.pickle` locally and update `YOUTUBE_TOKEN_PICKLE_B64`.
- GitHub Actions schedules are in UTC and can be delayed slightly.
- If the file is too large for email, the script will send the run link instead of failing.
