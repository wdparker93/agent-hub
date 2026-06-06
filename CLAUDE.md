# Agent Hub

A lightweight email-driven agent that polls Gmail for questions and answers them using Claude. Also runs a weekly brainstorm agent that generates monetizable app ideas.

## Pipelines

| Pipeline file | Schedule | Purpose |
|---|---|---|
| `automatic-email-agent.yml` | Three times per day — 9am, 2pm, 8pm UTC | Poll Gmail and reply to `[AGENT]` emails |
| `brainstorm-agent.yml` | Every Monday at 9am UTC | Generate app/product ideas and email a digest |

## How the email agent works

1. The ADO pipeline fires three times per day (`always: true` so it runs even with no new commits).
2. `email_agent.py` connects to Gmail via IMAP and searches for **unread emails where the subject contains `[AGENT]`**.
3. Each matching email is routed to the best-matching repo handler by keyword matching against `repos.yml`.
4. Claude answers the question using the relevant document (e.g. `context.md` fetched from GitHub).
5. The answer is sent as a reply and the email is marked read so it isn't processed again.

## How the brainstorm agent works

1. `brainstorm_agent.py` calls Claude with a product-strategist prompt focused on monetizable, solo-buildable app ideas.
2. Ideas span broad market categories — not limited to personal interests — prioritized by revenue potential.
3. A digest (5–7 ideas with problem, target buyer, price point, and build effort) is emailed to `wdparker93@gmail.com`.
4. Ideas are appended to `knowledge/idea-log.md` with a date stamp for later review.

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

### 3. Create the ADO pipelines

In Azure DevOps, create two pipelines pointing at this repo:
- **Email agent**: select `automatic-email-agent.yml` as the configuration file.
- **Brainstorm agent**: select `brainstorm-agent.yml` as the configuration file. Link the same `agent-hub` variable group.

## Sending a question

Email `wdparker93@gmail.com` with:
- Subject: `[AGENT] <your question here>`
- Body: the question (plain text)

The reply arrives within the next pipeline run (pipeline runs at 9am, 2pm, and 8pm UTC — maximum wait ~13 hours overnight).

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
