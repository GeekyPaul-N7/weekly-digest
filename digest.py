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
    log.info("Raw response for %s (first 500 chars): %s", subject["id"], raw[:500])
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
            stories = fetch_items(subj, api_key)
            log.info("Fetched %d stories for %s", len(stories), subj["id"])
        except Exception as exc:
            log.error("Failed to fetch %s: %s", subj["id"], exc)
            stories = []
        sections.append({"id": subj["id"], "label": subj["label"], "stories": stories})

    html = render_html(sections, label, generated_at)

    with open("digest_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    log.info("Preview written to digest_preview.html")

    send_email(html, f"Weekly Digest: {label}", gmail_user, recipient, gmail_password)
    log.info("Email sent to %s", recipient)


if __name__ == "__main__":
    main()
