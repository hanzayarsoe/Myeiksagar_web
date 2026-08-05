# Myeiksagar (ဘိတ်စကား)

Burmese ↔ Myeik dialect web app from UCS-MYEIK: Firestore dictionary lookup, CRF word segmentation, and a Myeik culture quiz.

## Stack

- **Backend:** Flask 3 + `python-crfsuite` (`api/index.py`)
- **Frontend:** Jinja templates + Tailwind/Alpine CDN
- **Data:** Firebase Firestore (client-side dictionary)
- **Deploy:** Vercel Python function + CDN static from `public/`

## Project layout

```
api/
  index.py                         # Flask app (Vercel entrypoint)
  quiz_data.py                     # Culture quiz question bank
  mm-word-segmentation-300.crfsuite
  templates/
public/
  static/                          # CSS, JS, images, fonts, sounds
firestore.rules                    # Firestore security rules
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

export SECRET_KEY="$(grep SECRET_KEY .env | cut -d= -f2-)"
python api/index.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

> Note: An older virtualenv folder named `.env/` may exist in this clone. Prefer `.venv/` for new setups so it does not collide with a `.env` secrets file.

## Deploy on Vercel

1. Push this repo and import the project in Vercel (or `vercel` CLI).
2. **Set `SECRET_KEY`** in Project Settings → Environment Variables for Production, Preview, and Development. Generate one with:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Deploy. `vercel.json` routes non-static traffic to `api/index.py` and serves `/static/**` from `public/static` on the CDN.

Without a fixed `SECRET_KEY`, quiz sessions break on every serverless cold start (the app refuses to boot on Vercel if it is missing).

## Main routes

| Path | Purpose |
|------|---------|
| `/` | Translator home |
| `/translate` | CRF word segmentation API |
| `/quiz_start_page` … `/quiz` | Culture quiz |
| `/about`, `/contact` | Info pages |

Dictionary inserts are handled by the companion app: [myeiksagar-collect](https://myeiksagar-collect.vercel.app/).

## Firestore rules

The translator reads from Firestore collection `data` (`{myanmarWord}` → `{ value: myeikWord }`).

`firestore.rules` allows public **read**, schema-checked **create/update** (string `value` only, max 200 chars), and **denies delete**. Deploy rules to project `myeiksagar-c1009`:

```bash
npm i -g firebase-tools   # once
firebase login
firebase use myeiksagar-c1009
firebase deploy --only firestore:rules
```

If the collect app later adds Firebase Auth, tighten writes to `request.auth != null` (or a specific UID allowlist).
