# ShopImpact (demo)

A small Streamlit demo that estimates CO₂ for purchases, offers greener alternatives, and shows playful badges.

This repository contains a minimal, local-friendly version of the app with a small `shopimpact` helper package and a mock API for development.

---

## What I added / changed

- `ShopImpact.py` — main Streamlit app (entrypoint). I added:
  - Safe import handling for the local `shopimpact` package.
  - A small CSS injection to give the app an earthy/green background.
  - A resilient `get_secret()` helper that avoids crashes when no `secrets.toml` is present.
  - A safe `api_get()` + `check_api_and_notify()` helper to call `API_BASE` without crashing on connection errors.
- `shopimpact/core.py` + `shopimpact/__init__.py` — minimal local package exposing `DEFAULT_MULTIPLIERS`, `get_multiplier_for_category`, `record_to_entry`, and `suggest_alternatives` used by the app.
- `mock_api.py` — tiny local HTTP server that responds to `GET /api/status` with `{ "status": "ok" }` so you can test the app without an external backend.
- `C:\Users\ASUS\.streamlit\secrets.toml` — a non-sensitive default file created for local dev (contains `api_base` default).

---

## Requirements

- Python 3.10+ (you appear to already have this installed).
- Packages:
  - streamlit
  - pandas
  - matplotlib

Install with PowerShell:

```powershell
pip install streamlit pandas matplotlib
```

(Or use your environment manager of choice.)

---

## How to run (local dev)

1) Start the local mock API (optional — only needed if you want the app to see a backend):

```powershell
python "C:\Users\ASUS\Desktop\ShopImpact\mock_api.py"
# Should print: Mock API server listening on http://localhost:8000
```

2) Start the Streamlit app (use the same Python environment you installed dependencies into):

```powershell
python -m streamlit run "C:\Users\ASUS\Desktop\ShopImpact\ShopImpact.py"
```

Open the `Local URL` printed by Streamlit (e.g. http://localhost:8501 or http://192.168.29.29:8501 ) in your browser.

If you started the mock API, the app's status check will show the backend as reachable.

---

## Secrets and configuration

- The app reads `API_BASE` from a secrets provider. For local development I added a helper `get_secret(key, default)` that falls back to a default if no secrets file exists.
- I created a local development `secrets.toml` at:

```
C:\Users\ASUS\.streamlit\secrets.toml
```

Example contents (already created for you):

```toml
api_base = "http://localhost:8000/api"
# api_key = "your-key-here"
```

If you'd rather use environment variables, switch to `os.environ.get("API_BASE", "http://localhost:8000/api")` in the code.

**Security note:** Do not commit real secrets to the repository. Keep secrets local (user `.streamlit` folder) or use a secure vault in production.

---

## Troubleshooting

- ModuleNotFoundError: No module named 'shopimpact'
  - The project includes a local `shopimpact` package in `shopimpact/`. The `ShopImpact.py` script inserts the project directory into `sys.path` automatically so `from shopimpact import core` works regardless of your working directory.

- streamlit.errors.StreamlitSecretNotFoundError
  - Fixed by adding `get_secret()` in `ShopImpact.py`. Also created a default `secrets.toml` in your user `.streamlit` folder to avoid the error for other scripts.

- Connection refused to `localhost:8000` (HTTPConnectionPool / WinError 10061)
  - This means the backend wasn't running. Either start your real backend, or run the included mock API server:

```powershell
python "C:\Users\ASUS\Desktop\ShopImpact\mock_api.py"
```

Then reload the Streamlit app.

---

## Files of interest

- `ShopImpact.py` — main Streamlit app.
- `shopimpact/core.py` — helper functions used by the app.
- `shopimpact/__init__.py` — package init.
- `mock_api.py` — local mock backend for testing `/api/status`.
- `C:\Users\ASUS\.streamlit\secrets.toml` — local secrets (non-sensitive defaults).
- `data.json` — local data file created by the app to persist purchases (in project root).

---
