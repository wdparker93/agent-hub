# Agent Hub — To-Do List

## 1. Knowledge Content

Provide enough structured detail that agents can give thorough, accurate answers.

- [ ] Expand `public/resume.html` in portfolio-page with richer project descriptions (tech stack, role, impact, dates)
- [ ] Write a `knowledge/projects/groovevision.md` — architecture, features, monetization, target user
- [ ] Write a `knowledge/projects/improv-helper.md` — architecture, features, use case
- [ ] Write a `knowledge/about-will.md` — background, skills taxonomy, career goals, availability
- [ ] Write a `knowledge/faq.md` — anticipated questions and canonical answers (e.g. "are you available for freelance?")
- [ ] Update `repos.yml` to point each repo entry at its knowledge file(s) so the agent fetches them as context

## 2. Portfolio Page — "Ask Me Anything" Feature

Let visitors know they can email a question and get an AI-powered answer.

- [ ] Add an "Ask Me Anything" section to `portfolio-page/src/components/` (below Projects, above Contact)
- [ ] Explain the `[AGENT]` email format with a one-liner and example subject line
- [ ] Add a mailto button that pre-fills `Subject: [AGENT] ` so the user just types their question
- [ ] Optionally show a disclaimer: "Replies are AI-generated based on Will's resume and project docs"

## 2a. "Living" Portfolio & Resume Branding

Once the AI pipeline is operational, surface that fact on the site and resume — this is itself a demonstration of the work.

- [ ] Add a subtle "AI-maintained" or "Living document" badge/label to the portfolio site header or About section
- [ ] Add a small callout on the Projects page explaining that project descriptions are automatically updated by an AI pipeline when the underlying repos ship new features
- [ ] Update `public/resume.html` to include a note (e.g. in the header or footer) that it is kept current by an automated AI agent
- [ ] Consider adding a "Last updated" timestamp to both the site and resume that the pipeline stamps on each auto-commit — makes the "living" quality concrete and visible
- [ ] Update the portfolio project entry for **Portfolio Page** itself to mention the AI-powered auto-update pipeline as a feature of the project

## 3. Agents & Skills

Move from a single flat handler to a skill-routed agent system.

- [ ] Define a skills registry (`knowledge/skills.yml`) — list of answerable topic areas, each with a system prompt and knowledge file list
- [ ] Refactor `email_agent.py` routing to load skill config from `skills.yml` instead of inline repos
- [ ] Add a **multi-turn** handler: if the reply chain already has prior `[AGENT]` turns, include them as conversation history
- [ ] Add a **fallback / out-of-scope** handler that politely declines questions Claude can't answer from the knowledge base
- [ ] Add a **confidence gate**: if Claude's answer relies on assumptions (nothing found in docs), append a caveat
- [ ] (Stretch) Explore Claude Managed Agents for stateful per-sender sessions so a conversation can span multiple emails

## 4. Knowledge Base & RAG

Build a tagged, retrievable knowledge base so the agent answers precisely instead of dumping the full document into context.

- [ ] Establish a `knowledge/` directory structure with consistent frontmatter tags:
  ```
  ---
  tags: [skills, python, backend]
  topic: technical-skills
  ---
  ```
- [ ] Write a `retriever.py` module: given a question, score knowledge chunks by tag/keyword overlap and return the top-N most relevant passages
- [ ] Integrate `retriever.py` into `email_agent.py` so only relevant chunks are passed to Claude (reduces token cost, improves focus)
- [ ] (Stretch) Replace keyword retrieval with embedding-based semantic search using the Anthropic embeddings API or a lightweight local model
- [ ] Add a `knowledge/index.md` that lists all knowledge files, their topics, and their tags — used by the retriever as a manifest

## 5. AI-Operated Repo Management (Beads + Gastownhall)

Goal: repos are agent-operated; you manage agents as their owner/reviewer rather than doing the work yourself.

- [ ] Research **beads (`bd`)** issue tracker — understand how it stores issues (Dolt-backed?), the `bd prime` / `bd ready` / `bd close` workflow, and whether it supports cross-repo issue linking
- [ ] Research **gastownhall** — understand how it enables a shared agent coordination layer across repos (global context, cross-repo task assignment)
- [ ] Prototype a `gastownhall` config in this repo that links to `spotify-youtube-connector`, `improvisation-helper`, and `portfolio-page`
- [ ] Define the agent workflow for feature-request intake:
  - Email with `[AGENT] [FEATURE]` prefix (or similar) triggers the pipeline
  - Agent triages the request: is it feasible, which repo does it belong to, estimated scope?
  - Agent creates a beads issue and opens a feature branch in the target repo
  - Agent scaffolds the branch with a stub implementation and opens a PR for Will to review
- [ ] Define escalation rules — what the agent does autonomously vs. what it flags for Will's approval before acting (e.g. auto-branch OK, auto-push to main NOT OK)
- [ ] Explore whether Claude Managed Agents (persistent agent configs + sessions) are a better fit than the current ADO-scheduled script for long-running or stateful agent tasks
- [ ] Document the target operating model: agent roles, what each one owns, how they hand off work to each other

## 7. Agent Honesty & Knowledge Gap Feedback Loop

Agents must never fabricate answers. When they don't know, they say so — and log the gap so it can be filled.

- [ ] Add explicit instructions to every agent system prompt: "If the answer is not clearly supported by the provided documents, do not guess. State that you don't have enough information to answer reliably and ask Will to provide more detail."
- [ ] Implement a **gap logger** in `email_agent.py`: when Claude's response contains uncertainty signals (e.g. "I don't have information about", "I'm not sure", "not mentioned in"), append the original question + date to `knowledge/gaps.md` and commit it
- [ ] Set up `knowledge/gaps.md` as a running log Will reviews periodically — each entry is a prompt to write new knowledge content or expand an existing file
- [ ] Add a **confidence check** step before sending a reply: have Claude rate its own confidence (high / medium / low) in a structured way, and if low, prepend a disclaimer to the reply and always log the gap regardless of wording
- [ ] Define a hard list of things agents must never do even if asked:
  - Never state Will is available/unavailable for work without an explicit knowledge file saying so
  - Never quote specific salary expectations or rates
  - Never commit to timelines or deliverables on Will's behalf
  - Never answer questions about people other than Will
  - Document this list in a `knowledge/agent-constraints.md` file that is injected into every agent's system prompt

## 6. Weekly App Idea Brainstorm Agent

A scheduled agent that generates new app/product ideas suited to Catnip Labs — things Will can build and sell.

- [ ] Create `brainstorm_agent.py` — calls Claude with a prompt focused on:
  - Solo-buildable tools (Chrome extensions, desktop companions, small SaaS)
  - Monetizable via Lemon Squeezy or similar (one-time purchase or subscription)
  - Underserved niches that match existing skills (JS/TS, Python, Chrome extensions, Windows native)
  - Brief for each idea: problem it solves, target user, rough build effort, monetization angle
- [ ] Add a weekly schedule entry to `azure-pipelines.yml` (e.g. Monday 9am) that runs `brainstorm_agent.py`
- [ ] Output options (pick one or both):
  - [ ] Email digest to `wdparker93@gmail.com` with 3–5 ideas, formatted as a short brief per idea
  - [ ] Append ideas to a `knowledge/idea-log.md` file with date stamps and commit them — builds a running archive Will can review
- [ ] Give the agent context so ideas stay relevant:
  - Current Catnip Labs products (GrooveVision, Improv Helper) — what's working, what niches are adjacent
  - Will's skill set (from `knowledge/about-will.md` once written)
  - Optionally: recent trending tools/topics fetched from a public source (HN, Product Hunt RSS)
