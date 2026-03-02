# Daily Paper Alert to KakaoTalk

This project sends paper recommendations to your KakaoTalk "Me" chat.

## What it does

- Collects papers from `arXiv` and `Crossref`
- Ranks by keywords (webtoon, animation, text mining, NLP, etc.)
- Boosts Korean papers (`ko` / Hangul detection)
- Sends up to `MAX_SEND_COUNT` items (default: 5)
- Runs automatically with Windows Task Scheduler

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill `.env`:

- `KAKAO_REST_API_KEY`
- `KAKAO_CLIENT_SECRET` (if enabled in Kakao app)
- `KAKAO_REDIRECT_URI`

## OAuth token

```powershell
python kakao_oauth_helper.py
```

Copy `access_token` and `refresh_token` to `.env`.

## Run once

```powershell
python paper_alert.py
```

## Scheduler (already used in this project)

- Morning task: `DailyPaperAlertKakao` at `09:00`
- Afternoon task: `DailyPaperAlertKakao_15` at `15:00`

Script used by tasks:

- `run_daily_paper_alert.cmd`

## Notes

- Kakao text template requires a `link` field, so the "details" area cannot be fully removed by API.
- Use DOI links in the message body directly.
