# Myeiksagar (ဘိတ်စကား)

Burmese ↔ Myeik dialect web app from UCS-MYEIK: dictionary translation (exact phrase, then word-level compose), CRF word segmentation, and a Myeik culture quiz. Missing words link out to the collect app for corpus growth.

## Stack

- **Backend:** Flask 3 + `python-crfsuite`
- **Frontend:** Jinja templates + `public/static/css/myeiksagar.css` (+ Alpine for mobile nav)
- **Data:** Firebase Firestore (client-side dictionary)
- **Deploy:** Vercel Python function + CDN static from `public/`

## Project layout

```
api/
  index.py                 # Vercel / local entrypoint (exposes `app`)
  factory.py               # create_app()
  config.py                # paths, env, session settings
  quiz_data.py             # culture quiz bank + helpers
  routes/
    pages.py               # /, /about, /contact
    quiz.py                # quiz session flow
    translate.py           # POST /translate
  services/
    segmentation.py        # CRF word segmentation
  templates/               # Jinja pages
  mm-word-segmentation-300.crfsuite
public/
  static/                  # css, js, images, fonts, sounds
firestore.rules
firebase.json
requirements.txt
vercel.json
```

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set SECRET_KEY (see .env.example)

python api/index.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

> Prefer a virtualenv named `.venv/`. An older folder named `.env/` may exist in this clone and can collide with a `.env` secrets file.

## Deploy on Vercel

1. Push this repo and import the project in Vercel (or `vercel` CLI).
2. **Set `SECRET_KEY`** in Project Settings → Environment Variables for Production, Preview, and Development:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Deploy. `vercel.json` routes non-static traffic to `api/index.py` and serves `/static/**` from `public/static` on the CDN.

Without a fixed `SECRET_KEY`, quiz sessions break on every serverless cold start (the app refuses to boot on Vercel if it is missing).

## Main routes

| Path | Purpose |
|------|---------|
| `/` | Translator home (phrase → segment → dictionary compose) |
| `/translate` | CRF word segmentation API |
| `/quiz_start_page` … `/quiz` | Culture quiz |
| `/about`, `/contact` | Info pages |

Dictionary inserts: [myeiksagar-collect](https://myeiksagar-collect.vercel.app/).

## Firestore rules

Collection `data`: `{myanmarWord}` → `{ value: myeikWord }`.

`firestore.rules` allows public **read**, schema-checked **create/update**, and **denies delete**. Deploy:

```bash
npx firebase-tools login
npx firebase-tools use myeiksagar-c1009
npx firebase-tools deploy --only firestore:rules
```
