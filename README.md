# Myeiksagar (ဘိတ်စကား)

Burmese ↔ Myeik dialect web app from UCS-MYEIK. Provides dictionary translation (exact phrase, then word-level compose), CRF word segmentation, and a Myeik culture quiz. Missing words can be contributed via a linked collect app.

## Features

- Myanmar ↔ Myeik phrase and word-level translation using a Firestore dictionary
- CRF-based Myanmar word segmentation (`python-crfsuite`)
- Myeik culture quiz with session-based progression
- About and contact pages
- Deployable as a Vercel Python serverless app with static assets from `public/`

## Tech Stack

- **Backend:** Flask 3, `python-crfsuite`
- **Frontend:** Jinja templates, static CSS/JS (Alpine for mobile nav)
- **Data:** Firebase Firestore (client-side dictionary reads)
- **Deploy:** Vercel Python function + CDN static files

## Project Structure

```text
api/
  index.py                 # Vercel / local entrypoint (exposes `app`)
  factory.py               # create_app()
  config.py                # paths, env, session settings
  quiz_data.py             # culture quiz bank
  routes/                  # pages, quiz, translate
  services/                # CRF segmentation
  templates/               # Jinja pages
  mm-word-segmentation-300.crfsuite
public/static/             # css, js, images, fonts, sounds
firestore.rules
firebase.json
requirements.txt
vercel.json
```

## Getting Started

### Prerequisites

- Python 3 (see `.python-version` if present)
- Node.js optional (for Firebase CLI / Vercel tooling)

### Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set SECRET_KEY

python api/index.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

> Prefer a virtualenv named `.venv/`. An older folder named `.env/` may exist in some clones and can collide with a `.env` secrets file.

## Configuration

Copy `.env.example` to `.env`:

```env
SECRET_KEY=replace-with-a-long-random-string
```

Generate a key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

On Vercel, set `SECRET_KEY` for Production, Preview, and Development. Without a fixed key, quiz sessions break on serverless cold starts.

### Main routes

| Path | Purpose |
|------|---------|
| `/` | Translator home |
| `/translate` | CRF word segmentation API |
| `/quiz_start_page` … `/quiz` | Culture quiz |
| `/about`, `/contact` | Info pages |

Dictionary inserts: [myeiksagar-collect](https://myeiksagar-collect.vercel.app/).

### Firestore

Collection `data`: `{myanmarWord}` → `{ value: myeikWord }`. Rules allow public read, schema-checked create/update, and deny delete. See `firestore.rules`.
