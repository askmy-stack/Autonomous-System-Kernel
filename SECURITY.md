# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

- Preferred: use GitHub's private vulnerability reporting for this repository
  (Security tab → **Report a vulnerability**).
- Alternative: email **kamineniabhinaysai@gmail.com** with a description of
  the issue, steps to reproduce, and its potential impact.

We aim to acknowledge reports within 7 days and to keep you updated as we
investigate and fix confirmed issues.

## Supported Versions

A.S.K. does not yet have tagged releases; security fixes are applied to the
`main` branch. Run the latest `main` to get fixes as soon as they land.

## Authentication

- `ASK_API_KEY` is optional Bearer auth enforced by `ApiKeyMiddleware`
  (`backend/middleware.py`) on every route except `/health`,
  `/health/providers`, `/docs`, `/openapi.json`, and `/redoc`. **Leaving it
  unset runs the API in open mode with no auth** — fine for local/dev use,
  but set it before exposing the service on a network.
- `/voice/stt/stream` (WebSocket) validates the same key independently
  (`authorize_websocket`), since `BaseHTTPMiddleware` never sees WebSocket
  handshakes. Browsers can't set custom WebSocket headers, so it also
  accepts the key via a `?token=` query param — avoid logging URLs that
  include this parameter.
- `/ops/backup` and `/ops/restore` always require `ASK_API_KEY` — they fail
  closed (`503`) if it isn't configured at all, rather than falling back to
  open access like the rest of the API. `/ops/restore` also only accepts
  `target_path` values from a fixed allowlist and `backup_path` values
  inside `BACKUP_DIR`.
- The Next.js frontend proxies API calls through server-side Route Handlers
  (`frontend/app/api/[...path]/route.ts`), which inject `ASK_API_KEY` from a
  server-only env var. Never rename `ASK_API_KEY` (or `ASK_API_URL`) to a
  `NEXT_PUBLIC_*` variable — that would inline it into the browser bundle.

## Data Handled

A.S.K. is a personal assistant that processes chat conversations, voice
transcripts/audio, and (on macOS) calendar reads/writes via AppleScript;
calendar mutations require an approval token from `POST /calendar/approve`.
Conversation turns are embedded into a local ChromaDB store
(`./chroma_db`) and a memory graph (`./memory_graph.db`); backups of both
are written to `BACKUP_DIR`. When `REDACT_PII=true` (the default),
`backend/ops.py::redact_text` strips emails and phone-like numbers before
text is persisted to the vector store — this is regex-based and does not
catch every PII type.

Depending on configuration, prompts and search queries may leave the
machine: to a configured LLM provider (OpenAI/OpenRouter; local Ollama by
default sends nothing externally), to LangSmith if tracing is enabled
(`LANGCHAIN_TRACING_V2`), and to DuckDuckGo for web search. `PRIVACY_MODE`
reflects deployment intent (surfaced in `/health`) but is not itself an
enforced technical control — review the provider/tracing settings you
actually configure.

---

This covers the security-relevant portion of the broader OSS-readiness
checklist tracked in #7; `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are
left for a follow-up PR.
