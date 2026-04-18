# AI Debugger

A small hackathon MVP Django app for turning pasted Python/Django tracebacks into a focused debugging brief.

The app gives you:

- Issue summary
- Likely root cause
- Suspected file/function/class
- Suggested minimal fix
- Optional patch diff
- Confidence score
- One regression test suggestion

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set an OpenAI API key for live analysis:

```bash
export OPENAI_API_KEY="your-api-key"
```

Optional model override:

```bash
export AI_DEBUGGER_MODEL="gpt-4o-mini"
```

## Run

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Demo

Click **Load Demo Example**, then **Analyze Bug**. If `OPENAI_API_KEY` is not set, the built-in demo still returns a deterministic structured analysis so the UI can be shown reliably.

## Notes

- No auth, no background jobs, and no database-backed features.
- The LLM call lives in `debugger/services/debugger.py`.
- Bad model output is handled with a friendly fallback and the raw response is shown instead of crashing the page.
- API keys are read from environment variables only.
