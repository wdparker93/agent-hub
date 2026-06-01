"""
Agent Hub — Weekly App Idea Generator

Runs every Sunday. Uses Claude to research market gaps and generate
monetizable app ideas tailored to a solo developer's interests and skills.
Results are emailed to GMAIL_ADDRESS.

Required environment variables (shared with email agent):
  ANTHROPIC_API_KEY   — Anthropic API key
  GMAIL_ADDRESS       — Gmail address to send the report to
  GMAIL_APP_PASSWORD  — 16-char Google app password
"""

import os
import smtplib
import textwrap
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────

GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
SMTP_HOST          = "smtp.gmail.com"
SMTP_PORT          = 465

MODEL = "claude-sonnet-4-6"

DEVELOPER_PROFILE = """
- Solo developer — no co-founder, no investors, no team to hire
- Comfortable with: Python, React, JavaScript, REST APIs, CLIs, desktop apps
- Can ship to: App Store, Google Play, Steam, web (SaaS), direct download, browser extension
- Budget: bootstrap / ramen profitable — must monetize without VC
- Time: side-project pace, so scope needs to fit one person
- Interests and domain knowledge: music production & instruments, video games
  (especially indie and retro), sci-fi (books/film/games), cats & pet care,
  firearms & shooting sports, developer tooling & automation
"""

PROMPT = f"""Today is {date.today().strftime("%B %d, %Y")}.

You are a sharp indie product strategist. Your job is to surface 5 specific,
monetizable software ideas that match the developer profile below — ideas with
real paying customers, a clear solo-dev path to v1, and a reason to exist
beyond "it would be cool."

Developer profile:
{DEVELOPER_PROFILE}

For each idea produce exactly this structure (use the bold headers verbatim):

**Idea N: [Product Name]**
**Problem:** The specific, concrete pain point. Who feels it, when, and why
existing tools fail them.
**Target buyer:** Exactly who pays — be specific (e.g. "bedroom producers who
release on Bandcamp" not just "musicians").
**Monetization:** Model + realistic price point. One-time, subscription,
marketplace cut, etc. Rough revenue estimate if the math is simple.
**MVP scope:** What the smallest shippable version looks like. What it does
NOT do yet.
**Distribution:** Where and how the first 100 customers would find it.
**Why a solo dev wins here:** Why this isn't already done well by a big
company, and why small scale is actually an advantage.
**Biggest risk:** The one thing most likely to kill it.

Ground rules:
- No generic ideas ("a habit tracker", "a recipe app"). Every idea must feel
  specific enough that you could write a landing page headline for it today.
- Prioritize niches where enthusiasts have money and strong opinions.
- Cross-category ideas (e.g. firearms + developer tooling, music + sci-fi
  worldbuilding) are especially welcome if the intersection makes sense.
- Avoid anything requiring a large content library, hardware, or a team to
  reach v1.
- At least two ideas should be outside the obvious "app for [interest]" framing
  — think tooling, automation, data, or workflow angles.

Generate 5 ideas now.
"""


# ── Claude call ────────────────────────────────────────────────────────────────

def generate_ideas() -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": PROMPT}],
    )
    return "\n\n".join(
        block.text for block in response.content if block.type == "text"
    )


# ── Email ──────────────────────────────────────────────────────────────────────

def ideas_to_html(ideas: str) -> str:
    lines = ideas.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**Idea"):
            html_lines.append(f'<h2 style="margin-top:2em;color:#1a73e8;">{stripped.strip("**")}</h2>')
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_lines.append(f'<p><strong>{stripped.strip("**")}</strong></p>')
        elif ":**" in stripped:
            label, _, rest = stripped.partition(":**")
            html_lines.append(
                f'<p><strong>{label.strip("*")}:</strong> {rest.strip()}</p>'
            )
        elif stripped:
            html_lines.append(f'<p>{stripped}</p>')
    return "\n".join(html_lines)


def send_email(ideas: str) -> None:
    subject = f"💡 Weekly App Ideas — {date.today().strftime('%b %d, %Y')}"

    plain = textwrap.fill(ideas, width=90)
    html = f"""
<html><body style="font-family:sans-serif;max-width:700px;margin:auto;color:#222;">
<h1 style="color:#1a73e8;">Weekly App Idea Report</h1>
<p style="color:#666;">{date.today().strftime("%A, %B %d, %Y")} &nbsp;·&nbsp; Generated by Agent Hub</p>
<hr>
{ideas_to_html(ideas)}
<hr>
<p style="color:#999;font-size:0.85em;">
  Generated by Agent Hub using Claude {MODEL}.<br>
  Ideas are starting points — do your own market validation before building.
</p>
</body></html>
"""

    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = GMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, GMAIL_ADDRESS, msg.as_string())
    print(f"Sent idea report to {GMAIL_ADDRESS}")


# ── Entry point ────────────────────────────────────────────────────────────────

def run() -> None:
    print("Generating app ideas via Claude…")
    ideas = generate_ideas()
    print(ideas)
    send_email(ideas)


if __name__ == "__main__":
    run()
