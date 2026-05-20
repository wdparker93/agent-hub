"""
Agent Hub — Email Q&A Agent

Polls a Gmail inbox for emails with [AGENT] in the subject line,
routes each to the appropriate handler based on keyword matching,
calls Claude for an answer, and replies to the sender.

Required environment variables:
  GMAIL_ADDRESS            — your Gmail address (e.g. you@gmail.com)
  GMAIL_APP_PASSWORD       — 16-char Google app password (not your login password)
  CLAUDE_CODE_OAUTH_TOKEN  — OAuth token from `claude setup-token` (Claude Pro/Max)

Optional:
  REPOS_YML_PATH      — path to repos.yml (defaults to ./repos.yml)
"""

import email
import imaplib
import os
import smtplib
import textwrap
import yaml
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
IMAP_HOST = "imap.gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

REPOS_YML_PATH = os.environ.get("REPOS_YML_PATH", os.path.join(os.path.dirname(__file__), "repos.yml"))

MODEL = "claude-opus-4-7"

# ── Routing ────────────────────────────────────────────────────────────────────

def load_repos() -> list[dict]:
    with open(REPOS_YML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["repos"]


def route_email(subject: str, body: str, repos: list[dict]) -> dict | None:
    """
    Return the best-matching repo config for this email, or None if no match.
    Scores by counting how many of the repo's keywords appear in subject+body.
    """
    text = f"{subject} {body}".lower()
    best_score = 0
    best_repo = None
    for repo in repos:
        score = sum(1 for kw in repo["keywords"] if kw.lower() in text)
        if score > best_score:
            best_score = score
            best_repo = repo
    return best_repo if best_score > 0 else repos[0]  # default to first (portfolio)


# ── Content fetching ───────────────────────────────────────────────────────────

_content_cache: dict[str, str] = {}

def fetch_content(url: str) -> str:
    if url in _content_cache:
        return _content_cache[url]
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    content = resp.text
    _content_cache[url] = content
    return content


# ── Claude call ────────────────────────────────────────────────────────────────

client = anthropic.Anthropic(auth_token=os.environ["CLAUDE_CODE_OAUTH_TOKEN"])

def ask_claude(repo: dict, question: str) -> str:
    """
    Call Claude with the repo's system prompt and (optionally) fetched content.
    Uses prompt caching on the system prompt and any fetched content block.
    """
    system_blocks: list[dict] = [
        {
            "type": "text",
            "text": repo["system_prompt"],
            "cache_control": {"type": "ephemeral"},
        }
    ]

    user_content: list[dict] = []

    # For repos with a fetchable document (e.g. resume HTML), include it with caching
    context_url = repo.get("resume_url") or repo.get("readme_url")
    if context_url:
        try:
            doc = fetch_content(context_url)
            user_content.append(
                {
                    "type": "text",
                    "text": f"<document>\n{doc}\n</document>",
                    "cache_control": {"type": "ephemeral"},
                }
            )
        except Exception as exc:
            user_content.append(
                {
                    "type": "text",
                    "text": f"(Could not fetch document: {exc})",
                }
            )

    user_content.append({"type": "text", "text": question})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=system_blocks,
        messages=[{"role": "user", "content": user_content}],
    )

    # Extract text blocks from the response (skip thinking blocks)
    return "\n\n".join(
        block.text for block in response.content if block.type == "text"
    )


# ── Email I/O ──────────────────────────────────────────────────────────────────

def fetch_unread_agent_emails(mail: imaplib.IMAP4_SSL) -> list[dict]:
    """Return unread emails whose subject contains [AGENT]."""
    mail.select("INBOX")
    _, data = mail.search(None, '(UNSEEN SUBJECT "[AGENT]")')
    ids = data[0].split()
    results = []
    for uid in ids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        body = extract_plain_body(msg)
        results.append(
            {
                "uid": uid,
                "from": msg.get("From", ""),
                "subject": msg.get("Subject", ""),
                "message_id": msg.get("Message-ID", ""),
                "body": body,
                "raw_msg": msg,
            }
        )
    return results


def extract_plain_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="replace")
    return msg.get_payload(decode=True).decode(errors="replace")


def mark_seen(mail: imaplib.IMAP4_SSL, uid: bytes) -> None:
    mail.store(uid, "+FLAGS", "\\Seen")


def send_reply(to_address: str, original_subject: str, in_reply_to: str, answer: str) -> None:
    subject = original_subject if original_subject.startswith("Re:") else f"Re: {original_subject}"

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to

    plain = textwrap.fill(answer, width=80)
    html = f"<html><body><p>{answer.replace(chr(10), '<br>')}</p><hr><p><em>Answered by Agent Hub</em></p></body></html>"

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())


# ── Main loop ──────────────────────────────────────────────────────────────────

def run() -> None:
    repos = load_repos()

    with imaplib.IMAP4_SSL(IMAP_HOST) as mail:
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        emails = fetch_unread_agent_emails(mail)

        if not emails:
            print("No unread [AGENT] emails found.")
            return

        for item in emails:
            print(f"Processing: {item['subject']} from {item['from']}")
            try:
                repo = route_email(item["subject"], item["body"], repos)
                print(f"  → Routed to: {repo['display_name']}")

                answer = ask_claude(repo, item["body"])

                sender = email.utils.parseaddr(item["from"])[1]
                send_reply(sender, item["subject"], item["message_id"], answer)

                mark_seen(mail, item["uid"])
                print(f"  ✓ Replied to {sender}")
            except Exception as exc:
                print(f"  ✗ Error processing email: {exc}")


if __name__ == "__main__":
    run()
