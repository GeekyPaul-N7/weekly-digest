# Weekly Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a weekly HTML email digest that fetches news via Perplexity API and sends it via Gmail SMTP, triggered by GitHub Actions on a Monday morning cron.

**Architecture:** A single `digest.py` runner loads topic definitions from YAML, fans out one Perplexity `sonar-pro` request per topic with per-subject error isolation, renders an inline-styled Jinja2 HTML template, writes a local preview file, and sends via Gmail SMTP SSL. GitHub Actions injects all secrets as environment variables.

**Tech Stack:** Python 3.12, requests, PyYAML, Jinja2, smtplib (stdlib), GitHub Actions

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `.gitignore` | Create | Ignore build artifacts, venv, preview HTML |
| `requirements.txt` | Create | Pinned runtime deps |
| `config/subjects.yml` | Create | Topic definitions (id, label, query) |
| `templates/digest.html.j2` | Create | Inline-styled table-based HTML email |
| `digest.py` | Create | Main runner: load → fetch → render → send |
| `.github/workflows/weekly-digest.yml` | Create | Monday 07:00 UTC cron + manual dispatch |
| `README.md` | Create | Purpose, setup, secrets table, local test instructions |

---

### Task 1: Git init + .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialise git repo**

```bash
cd /c/Projects/weekly-digest
git init
```
Expected: `Initialized empty Git repository in .../weekly-digest/.git/`

- [ ] **Step 2: Write .gitignore**

```
__pycache__/
*.pyc
.env
.venv/
venv/
digest_preview.html
*.log
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

---

### Task 2: requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write requirements.txt**

```
requests==2.32.3
PyYAML==6.0.2
Jinja2==3.1.4
```

- [ ] **Step 2: Verify pip can resolve the file (dry-run)**

```bash
pip install -r requirements.txt --dry-run 2>&1 | tail -5
```
Expected: no error, lists packages to install.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt"
```

---

### Task 3: config/subjects.yml

**Files:**
- Create: `config/subjects.yml`

- [ ] **Step 1: Write subjects.yml**

```yaml
subjects:
  - id: salesforce
    label: "Salesforce & CRM"
    query: "Salesforce platform news, releases, and updates this week"

  - id: ai_tools
    label: "AI Tools & Agents"
    query: "AI agent frameworks, LLM releases, and developer tools this week"

  - id: uk_tech
    label: "UK Tech & Startups"
    query: "UK technology industry news and startup ecosystem this week"

  - id: home_automation
    label: "Home Automation"
    query: "Home Assistant, smart home, and home automation news this week"

  - id: gaming
    label: "Gaming"
    query: "PC and console gaming news, releases, and updates this week"
```

- [ ] **Step 2: Spot-check with Python**

```bash
python -c "import yaml; d=yaml.safe_load(open('config/subjects.yml')); print(len(d['subjects']), 'subjects')"
```
Expected: `5 subjects`

- [ ] **Step 3: Commit**

```bash
git add config/subjects.yml
git commit -m "feat: add subject definitions"
```

---

### Task 4: templates/digest.html.j2

**Files:**
- Create: `templates/digest.html.j2`

- [ ] **Step 1: Write the Jinja2 template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Digest</title>
</head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0f4f8;">
  <tr>
    <td align="center" style="padding:24px 0;">
      <table width="620" cellpadding="0" cellspacing="0" border="0" style="max-width:620px;width:100%;">

        <!-- HEADER -->
        <tr>
          <td style="background:#1A5FA8;padding:32px 40px 28px;border-radius:8px 8px 0 0;">
            <p style="margin:0 0 6px;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-variant:small-caps;color:#a8c8e8;">Weekly Intelligence</p>
            <h1 style="margin:0 0 8px;font-size:28px;font-weight:700;color:#ffffff;line-height:1.2;">Weekly Digest</h1>
            <p style="margin:0;font-size:14px;color:#c8ddf0;">{{ week_label }}</p>
          </td>
        </tr>

        <!-- BODY -->
        <tr>
          <td style="background:#ffffff;padding:32px 40px;">
            {% for section in sections %}
            <!-- SECTION: {{ section.label }} -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:32px;">
              <tr>
                <td style="border-bottom:2px solid #0099D6;padding-bottom:8px;margin-bottom:16px;">
                  <h2 style="margin:0;font-size:13px;letter-spacing:2px;text-transform:uppercase;font-variant:small-caps;color:#0099D6;font-weight:700;">{{ section.label }}</h2>
                </td>
              </tr>
              {% if section.items %}
                {% for item in section.items %}
                <tr>
                  <td style="padding:16px 0 0;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td width="36" valign="top" style="padding-right:12px;">
                          <div style="width:28px;height:28px;background:#1A5FA8;border-radius:50%;text-align:center;line-height:28px;color:#ffffff;font-size:12px;font-weight:700;">{{ loop.index }}</div>
                        </td>
                        <td valign="top">
                          <p style="margin:0 0 6px;">
                            <a href="{{ item.url }}" style="color:#1A5FA8;font-weight:700;font-size:15px;text-decoration:none;">{{ item.title }}</a>
                          </p>
                          <p style="margin:0 0 10px;font-size:14px;color:#4D4D4D;line-height:1.6;">{{ item.summary }}</p>
                          <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                              <td style="border-left:3px solid #0099D6;padding:8px 12px;background:#f0f4f8;">
                                <p style="margin:0;font-size:12px;color:#4D4D4D;line-height:1.5;"><strong style="color:#0099D6;">Why it matters:</strong> {{ item.significance }}</p>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                {% endfor %}
              {% else %}
              <tr>
                <td style="padding:16px 0;">
                  <p style="margin:0;font-size:14px;color:#aaaaaa;font-style:italic;">No items retrieved.</p>
                </td>
              </tr>
              {% endif %}
            </table>
            {% endfor %}
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#1A5FA8;padding:20px 40px;border-radius:0 0 8px 8px;text-align:center;">
            <p style="margin:0;font-size:11px;color:#a8c8e8;">Generated {{ generated_at }} &middot; Powered by Perplexity sonar-pro</p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>
```

- [ ] **Step 2: Smoke-check Jinja2 can parse it**

```bash
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
tpl = env.get_template('digest.html.j2')
html = tpl.render(week_label='w/c 14 April 2026', generated_at='2026-04-17 07:00 UTC', sections=[])
print('OK, len:', len(html))
"
```
Expected: `OK, len: <number>`

- [ ] **Step 3: Commit**

```bash
git add templates/digest.html.j2
git commit -m "feat: add HTML email template"
```

---

### Task 5: digest.py

**Files:**
- Create: `digest.py`

- [ ] **Step 1: Write digest.py**

```python
import json
import logging
import os
import re
import smtplib
import ssl
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
SYSTEM_PROMPT = (
    "Return ONLY a JSON array. No markdown fences, no preamble. "
    "Each element must have exactly these keys: title, summary, url, significance. "
    "summary is 2-3 sentences. significance is one sentence. "
    "Rank items by significance, most significant first. Maximum 5 items."
)


def load_subjects(path: str = "config/subjects.yml") -> list[dict]:
    with open(path) as f:
        return yaml.safe_load(f)["subjects"]


def week_label_for(d: date) -> str:
    monday = d - timedelta(days=d.weekday())
    return monday.strftime("w/c %-d %B %Y")


def fetch_items(subject: dict, api_key: str) -> list[dict]:
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": subject["query"]},
        ],
        "search_recency_filter": "week",
        "temperature": 0.2,
        "max_tokens": 1500,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(PERPLEXITY_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def render_html(sections: list[dict], week_label: str, generated_at: str) -> str:
    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    tpl = env.get_template("digest.html.j2")
    return tpl.render(sections=sections, week_label=week_label, generated_at=generated_at)


def send_email(html: str, subject_line: str, sender: str, recipient: str, app_password: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject_line
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())


def main() -> None:
    api_key = os.environ["PERPLEXITY_API_KEY"]
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["DIGEST_RECIPIENT"]

    today = date.today()
    label = week_label_for(today)
    generated_at = today.strftime("%Y-%m-%d 07:00 UTC")

    subjects = load_subjects()
    sections = []
    for subj in subjects:
        try:
            items = fetch_items(subj, api_key)
            log.info("Fetched %d items for %s", len(items), subj["id"])
        except Exception as exc:
            log.error("Failed to fetch %s: %s", subj["id"], exc)
            items = []
        sections.append({"id": subj["id"], "label": subj["label"], "items": items})

    html = render_html(sections, label, generated_at)

    with open("digest_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    log.info("Preview written to digest_preview.html")

    send_email(html, f"Weekly Digest: {label}", gmail_user, recipient, gmail_password)
    log.info("Email sent to %s", recipient)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check**

```bash
python -m py_compile digest.py && echo "OK"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add digest.py
git commit -m "feat: add main digest runner"
```

---

### Task 6: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/weekly-digest.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Weekly Digest

on:
  schedule:
    - cron: "0 7 * * 1"
  workflow_dispatch:

jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run digest
        env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          GMAIL_USER: ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          DIGEST_RECIPIENT: ${{ secrets.DIGEST_RECIPIENT }}
        run: python digest.py

      - name: Upload preview on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: digest_preview
          path: digest_preview.html
          retention-days: 7
```

- [ ] **Step 2: YAML lint check**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/weekly-digest.yml')); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/weekly-digest.yml
git commit -m "ci: add weekly digest workflow"
```

---

### Task 7: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

### Task 8: Initial scaffold commit

- [ ] **Step 1: Verify clean working tree**

```bash
git status
```
Expected: `nothing to commit, working tree clean`

- [ ] **Step 2: Amend the last commit message to match the requested initial scaffold message, OR make a final consolidation commit if anything is un-staged**

If everything is already committed in prior tasks, create one final empty-tree summary commit:

```bash
git log --oneline
```
Review. If the requested initial commit message (`Initial scaffold`) is desired as the single commit, squash all prior commits:

```bash
git rebase -i --root
# In the editor, change all but the first "pick" to "squash"
# Set the combined message to: Initial scaffold
```

Expected: single commit `Initial scaffold` covering all files.
