# Meme Shorts YouTube Auto Uploader

This project generates short meme videos and can upload them to YouTube automatically. The current generator creates 6-second MP4 shorts from meme images, a background video, and background music.

## Features

- Generates 6-second meme shorts with MoviePy.
- Fetches meme images from `https://meme-api.com/gimme`.
- Uses `assets/background_video.mp4` and `assets/background_music.mp3`.
- Provides a Flask web page for generating, previewing, and downloading `static/final_video.mp4`.
- Includes `auto_upload.py` for scheduled YouTube uploads.
- Runs automatically once per hour through GitHub Actions.
- Can send the generated MP4 by email when SMTP settings are configured.
- Uploads the generated video as a GitHub Actions artifact for 7 days.

## Project Structure

```text
.
|-- .github/workflows/youtube-upload.yml
|-- assets/
|   |-- IMPACT.TTF
|   |-- background_music.mp3
|   `-- background_video.mp4
|-- templates/
|   `-- index.html
|-- app.py
|-- auto_upload.py
|-- generate_video_portable.py
|-- generate_video.py
|-- generate_meme_short.py
|-- meme_api.py
|-- requirements.txt
|-- render.yaml
`-- .env.example
```

Generated files are intentionally ignored by Git:

- `static/final_video.mp4`
- `uploads/`
- `temp/`
- `.env`
- `client_secrets.json`
- `token.pickle`

## Local Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure these assets exist:

```text
assets/background_video.mp4
assets/background_music.mp3
```

3. Start the Flask app:

```bash
python app.py
```

4. Open the app:

```text
http://127.0.0.1:5000
```

Use the page to generate a short, preview it, and download the MP4.

## Generate One Video

To generate a video from the command line without opening the web app:

```bash
python generate_video_portable.py
```

The output is written to:

```text
static/final_video.mp4
```

## YouTube Upload Setup

1. Create a Google Cloud project.
2. Enable the YouTube Data API v3.
3. Create an OAuth Desktop App client.
4. Download the OAuth JSON file.
5. Save it in the project root as:

```text
client_secrets.json
```

6. Copy `.env.example` to `.env` and adjust values as needed.
7. Run one upload locally:

```bash
python auto_upload.py --run-once
```

The first local run opens a browser window so you can sign in to the YouTube channel and grant upload access. After authorization, the OAuth token is saved as `token.pickle`.

GitHub Actions is headless, so it does not attempt browser sign-in. The workflow expects a valid pre-authorized `token.pickle` to be provided through `YOUTUBE_TOKEN_PICKLE_B64`.

## Local Scheduler

Run continuously with the default 60-minute interval:

```bash
python auto_upload.py
```

Change the interval with either:

```env
UPLOAD_INTERVAL_MINUTES=60
```

or:

```bash
python auto_upload.py --interval-minutes 60
```

The older `--interval-hours` flag still works, but `--interval-minutes` is preferred.

On Windows, use Task Scheduler if you want uploads to continue after reboots. Configure it to run:

```bash
python auto_upload.py --run-once
```

every 60 minutes.

## GitHub Actions Automation

The workflow at `.github/workflows/youtube-upload.yml` can be run manually and is also scheduled for:

```yaml
0 * * * *
```

That means one run at the start of every hour in UTC. GitHub schedules can be delayed slightly.

The workflow:

- checks out the repository
- installs Python and FFmpeg
- installs `requirements.txt`
- runs `python auto_upload.py --run-once`
- uploads `static/final_video.mp4` as an artifact
- sends email if SMTP settings are configured
- uploads to YouTube if YouTube credentials are configured

## GitHub Secrets And Variables

For YouTube uploads, add these GitHub Actions secrets:

- `YOUTUBE_CLIENT_SECRETS_JSON`: the full contents of `client_secrets.json`
- `YOUTUBE_TOKEN_PICKLE_B64`: base64-encoded contents of `token.pickle`

The workflow cannot recover an expired or revoked YouTube token by itself. When that happens, refresh the token locally and upload the new base64 value to `YOUTUBE_TOKEN_PICKLE_B64`.

Convert `token.pickle` to base64 in PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle"))
```

Optional YouTube variables:

- `YOUTUBE_PRIVACY_STATUS`: default `private`
- `YOUTUBE_CATEGORY_ID`: default `24`
- `YOUTUBE_TITLE_PREFIX`: default `Meme Short`
- `YOUTUBE_DESCRIPTION`: default `Auto-generated meme short. #shorts #meme #funny`
- `YOUTUBE_TAGS`: default `shorts,meme,funny,viral`
- `YOUTUBE_UPLOAD_FAILURE_FATAL`: default `true`. When `true`, the GitHub Actions job fails if YouTube upload was configured but could not complete. Email delivery and artifact upload still run after the video is generated.

For email delivery, add these GitHub Actions secrets:

- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

And these GitHub Actions variables:

- `EMAIL_TO`
- `EMAIL_FROM`
- `EMAIL_SUBJECT_PREFIX`
- `EMAIL_ATTACHMENT_MAX_MB`
- `SMTP_PORT`
- `SMTP_USE_TLS`

For Gmail SMTP, use an App Password instead of your normal Gmail password.

## Environment Variables

See `.env.example` for all supported local settings:

```env
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_TOKEN_FILE=token.pickle
YOUTUBE_ALLOW_INTERACTIVE_AUTH=true
YOUTUBE_PRIVACY_STATUS=private
YOUTUBE_CATEGORY_ID=24
YOUTUBE_TITLE_PREFIX=Meme Short
YOUTUBE_DESCRIPTION=Auto-generated meme short. #shorts #meme #funny
YOUTUBE_TAGS=shorts,meme,funny,viral
YOUTUBE_UPLOAD_FAILURE_FATAL=true
UPLOAD_INTERVAL_MINUTES=60
EMAIL_TO=
EMAIL_FROM=
EMAIL_SUBJECT_PREFIX=Meme Short Ready
EMAIL_ATTACHMENT_MAX_MB=20
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true
GITHUB_ARTIFACT_NAME=generated-video
```

## Deployment

For Render, use the included `render.yaml` or configure a Python web service with:

```bash
gunicorn app:app
```

The Flask app is useful for manual video generation. The scheduled YouTube upload flow is handled by `auto_upload.py` and GitHub Actions.

## Troubleshooting

- If YouTube upload fails, check `YOUTUBE_CLIENT_SECRETS_JSON` and `YOUTUBE_TOKEN_PICKLE_B64`.
- If the OAuth token expires or stops working, regenerate `token.pickle` locally and update the base64 secret. GitHub Actions cannot complete the browser OAuth step for you.
- If you want video generation, email, and artifact upload to keep succeeding while you fix YouTube OAuth, set the GitHub Actions variable `YOUTUBE_UPLOAD_FAILURE_FATAL=false`.
- If you want to disable local browser auth too, set `YOUTUBE_ALLOW_INTERACTIVE_AUTH=false`.
- If email does not send, check `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_TO`, and `SMTP_PORT`.
- If the generated video is missing, confirm `assets/background_video.mp4` and `assets/background_music.mp3` exist.
- If GitHub Actions fails, open the failed run and read the logs for the exact command error.
