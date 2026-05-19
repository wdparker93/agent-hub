# Agent Hub

A lightweight email-driven agent that polls Gmail for questions and answers them using Claude.

## How it works

1. The ADO pipeline fires every 15 minutes (`always: true` so it runs even with no new commits).
2. `email_agent.py` connects to Gmail via IMAP and searches for **unread emails where the subject contains `[AGENT]`**.
3. Each matching email is routed to the best-matching repo handler by keyword matching against `repos.yml`.
4. Claude (`claude-opus-4-7`, adaptive thinking) answers the question using the relevant document (e.g. `resume.html` fetched from GitHub).
5. The answer is sent as a reply and the email is marked read so it isn't processed again.

## Setup

### 1. Gmail app password

In your Google account → Security → 2-Step Verification → App passwords, create a password for "Mail". Use the 16-character result as `GMAIL_APP_PASSWORD`.

### 2. ADO pipeline variables

In Azure DevOps → Pipelines → (this pipeline) → Edit → Variables, add and mark secret:

| Variable | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `GMAIL_ADDRESS` | `wdparker93@gmail.com` |
| `GMAIL_APP_PASSWORD` | The 16-char app password |

### 3. Create the ADO pipeline

Point the pipeline at this repo and select `azure-pipelines.yml` as the configuration file.

## Sending a question

Email `wdparker93@gmail.com` with:
- Subject: `[AGENT] <your question here>`
- Body: the question (plain text)

The reply arrives within 15 minutes (next pipeline run).

## Routing

Routing is keyword-based — see `repos.yml`. Any email that doesn't match a specific repo falls through to the **portfolio** handler (the default). Keywords are matched case-insensitively against the combined subject + body text.

Example routings:
- "Tell me about Will's work experience" → portfolio
- "How does the Spotify connector detect the current song?" → groovevision
- "What is Improv Helper?" → improvhelper

## Adding new repos

Add an entry to `repos.yml` with:
- `id` — short identifier
- `display_name` — human-readable name
- `keywords` — list of strings that route emails here
- `resume_url` or `readme_url` — optional URL to fetch as context (cached across requests)
- `system_prompt` — persona and constraints for Claude

## Architecture notes

- **Prompt caching**: the system prompt and fetched document are marked `cache_control: {type: "ephemeral"}`. This cuts token costs significantly when multiple emails arrive in the same pipeline run (the resume HTML is ~10K tokens and is re-used across requests).
- **No database**: read state is tracked by Gmail's `\Seen` flag. No external storage needed.
- **Idempotent**: re-running the pipeline when no new `[AGENT]` emails exist is a no-op.
