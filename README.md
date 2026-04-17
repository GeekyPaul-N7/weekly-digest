# weekly-digest

A scheduled weekly email digest that fetches news via the Perplexity API and delivers it as a styled HTML email via Gmail SMTP.

## How it works

1. GitHub Actions triggers every Monday at 07:00 UTC (or manually via `workflow_dispatch`)
2. `digest.py` loads topic definitions from `config/subjects.yml`
3. For each topic, one request is sent to the Perplexity `sonar-pro` model with `search_recency_filter: week`, returning a ranked JSON array of up to 5 news items
4. Results are rendered into an inline-styled HTML email via Jinja2 (`templates/digest.html.j2`)
5. The email is sent via Gmail SMTP SSL to the configured recipient

## Folder structure

```
weekly-digest/
├── .github/workflows/weekly-digest.yml   # Actions cron workflow
├── config/subjects.yml                   # Topic definitions
├── templates/digest.html.j2              # HTML email template
├── digest.py                             # Main runner
├── requirements.txt                      # Pinned deps
└── README.md
```

## Setup

### GitHub Secrets

Add these four secrets to your repository (**Settings → Secrets and variables → Actions**):

| Secret | Description |
|--------|-------------|
| `PERPLEXITY_API_KEY` | API key from [perplexity.ai](https://www.perplexity.ai/) |
| `GMAIL_USER` | Full Gmail address used as sender, e.g. `you@gmail.com` |
| `GMAIL_APP_PASSWORD` | 16-character Gmail App Password (see below) |
| `DIGEST_RECIPIENT` | Email address to receive the digest |

### Gmail App Password

1. Enable 2-Step Verification on your Google account
2. Go to **Google Account → Security → 2-Step Verification → App passwords**
3. Create a new app password (any name), copy the 16-character code
4. Use this as the `GMAIL_APP_PASSWORD` secret — never your real Gmail password

## Local testing

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables and run:

```bash
export PERPLEXITY_API_KEY=your_key
export GMAIL_USER=you@gmail.com
export GMAIL_APP_PASSWORD=your_app_password
export DIGEST_RECIPIENT=recipient@example.com
python digest.py
```

After running, `digest_preview.html` is written to the working directory. Open it in a browser to inspect the rendered email before it is sent.
