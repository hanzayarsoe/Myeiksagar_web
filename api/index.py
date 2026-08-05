import os
import pycrfsuite
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

try:
    from quiz_data import QUESTIONS_PER_ROUND, assert_quiz_integrity, pick_questions
except ImportError:  # when imported as api.index from project root
    from api.quiz_data import QUESTIONS_PER_ROUND, assert_quiz_integrity, pick_questions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
MODEL_PATH = os.path.join(BASE_DIR, "mm-word-segmentation-300.crfsuite")
MAX_SEGMENT_CHARS = 2000


def _load_dotenv():
    """Load KEY=VALUE pairs from .env / .env.local files (not a .env/ directory)."""
    for name in (".env", ".env.local"):
        env_path = os.path.join(ROOT_DIR, name)
        if not os.path.isfile(env_path):
            continue
        with open(env_path, encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key:
                    os.environ.setdefault(key, value)


_load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    # Local Flask serves from public/static; on Vercel the CDN serves public/**
    static_folder=os.path.join(ROOT_DIR, "public", "static"),
    static_url_path="/static",
)

_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "SECRET_KEY is required on Vercel. "
            "Set it in Project Settings → Environment Variables."
        )
    _secret_key = "dev-only-insecure-secret-key"

app.secret_key = _secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Secure cookies on Vercel (HTTPS); keep off for local http://
    SESSION_COOKIE_SECURE=bool(os.environ.get("VERCEL")),
)

_tagger = None


def get_tagger():
    """Lazy-load the CRF model so cold starts fail clearly and only when needed."""
    global _tagger
    if _tagger is None:
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(f"CRF model not found at {MODEL_PATH}")
        tagger = pycrfsuite.Tagger()
        tagger.open(MODEL_PATH)
        _tagger = tagger
    return _tagger


def create_char_features(sentence, i):
    # set initial feature set char as first char in prepared_sentence
    features = [
        'bias',
        'char=' + sentence[i][0]
    ]
    # if i >=1 then go to previous character else append 'BOS' in features list
    if i >= 1:
        features.extend([
            'char-1=' + sentence[i-1][0],
            'char-1:0=' + sentence[i-1][0] + sentence[i][0],
        ])
    else:
        features.append("BOS")

    if i >= 2:
        features.extend([
            'char-2=' + sentence[i-2][0],
            'char-2:0=' + sentence[i-2][0] + sentence[i-1][0] + sentence[i][0],
            'char-2:-1=' + sentence[i-2][0] + sentence[i-1][0],
        ])

    if i >= 3:
        features.extend([
            'char-3:0=' + sentence[i-3][0] + sentence[i -
                                                      2][0] + sentence[i-1][0] + sentence[i][0],
            'char-3:-1=' + sentence[i-3][0] +
            sentence[i-2][0] + sentence[i-1][0],
        ])
    # if i+1 < len(sentence) then go to next character and set it to next character and set char to next two characters else append 'EOS' to features list
    if i + 1 < len(sentence):
        features.extend([
            'char+1=' + sentence[i+1][0],
            'char:+1=' + sentence[i][0] + sentence[i+1][0],
        ])
    else:
        features.append("EOS")
    # if first if condition satisfy then go to second and third if condition and do the same work for next characters
    if i + 2 < len(sentence):
        features.extend([
            'char+2=' + sentence[i+2][0],
            'char:+2=' + sentence[i][0] + sentence[i+1][0] + sentence[i+2][0],
            'char+1:+2=' + sentence[i+1][0] + sentence[i+2][0],
        ])

    if i + 3 < len(sentence):
        features.extend([
            'char:+3=' + sentence[i][0] + sentence[i +
                                                   1][0] + sentence[i+2][0] + sentence[i+3][0],
            'char+1:+3=' + sentence[i+1][0] +
            sentence[i+2][0] + sentence[i+3][0],
        ])
    return features


def create_word_features(prepared_sentence):
    return [create_char_features(prepared_sentence, i) for i in range(len(prepared_sentence))]

# segment word by trained model


def segment_word(sentence):
    # remove white spaces from sentence
    sent = sentence.replace(" ", "")
    # tag sentence by trained model or create sentence features
    prediction = get_tagger().tag(create_word_features(sent))
    # assign 'complete' to empty string
    complete = ""
    # apply for loop on taged sentence
    for i, p in enumerate(prediction):
        # if label of character in sentence is 1 then brack that word from that place and add into complete
        if p == "1":
            complete += "   " + sent[i]
        # if label of character in sentence is 0 then add that word as it is into complete
        else:
            complete += sent[i]
    # print(type(sent))
    return complete

assert_quiz_integrity()


def _normalize_answer(value):
    return (value or "").strip()


@app.route('/quiz_start_page')
def quiz_start_page():
    return render_template('quiz_start_page.html')


@app.route('/quiz_start')
def quiz_start():
    session.clear()
    session['level'] = 'easy'
    session['score'] = 0
    session['question_number'] = 0
    session['completed_levels'] = 0
    session['questions'] = pick_questions(session['level'], QUESTIONS_PER_ROUND)
    session['total_questions'] = QUESTIONS_PER_ROUND
    return redirect(url_for('quiz'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'level' not in session:
        return redirect(url_for('quiz_start_page'))

    if request.method == 'POST':
        user_answer = _normalize_answer(request.form.get('answer'))
        correct_answer = _normalize_answer(
            session['questions'][session['question_number']]['answer']
        )

        if user_answer == correct_answer:
            session['score'] += 1

        session['question_number'] += 1

        if session['question_number'] >= session['total_questions']:
            if session['score'] == session['total_questions']:
                session['completed_levels'] += 1
                if session['level'] == 'hard':
                    return redirect(url_for('congratulations'))
                return redirect(url_for('next_level'))
            return redirect(url_for('result'))

    if session['question_number'] < session['total_questions']:
        question_data = session['questions'][session['question_number']]
        return render_template(
            'quiz.html',
            question=question_data['question'],
            options=question_data['options'],
            level=session['level'],
            question_number=session['question_number'] + 1,
            total_questions=session['total_questions'],
        )
    return redirect(url_for('result'))


@app.route('/next_level')
def next_level():
    if 'completed_levels' not in session or session['completed_levels'] < 1:
        return redirect(url_for('quiz_start_page'))
    upcoming = 'medium' if session['level'] == 'easy' else 'hard'
    return render_template('next_level.html', next_level=upcoming)


@app.route('/start_next_level')
def start_next_level():
    if 'completed_levels' not in session or session['completed_levels'] < 1:
        return redirect(url_for('quiz_start_page'))
    if session['level'] == 'easy':
        session['level'] = 'medium'
    elif session['level'] == 'medium':
        session['level'] = 'hard'

    session['score'] = 0
    session['question_number'] = 0
    session['questions'] = pick_questions(session['level'], QUESTIONS_PER_ROUND)
    session['total_questions'] = QUESTIONS_PER_ROUND
    return redirect(url_for('quiz'))


@app.route('/congratulations')
def congratulations():
    if 'completed_levels' not in session or session['completed_levels'] < 3:
        return redirect(url_for('quiz_start_page'))
    session['completed_levels'] = 0
    return render_template('congratulations.html')


@app.route('/result')
def result():
    if 'level' not in session:
        return redirect(url_for('quiz_start_page'))
    return render_template('result.html', score=session['score'], level=session['level'])


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/translate', methods=['POST'])
def wordTranslation():
    data = request.get_json(silent=True) or {}
    text = data.get('text')
    if not isinstance(text, str) or not text.strip():
        return jsonify({'error': 'text is required'}), 400
    text = text.strip()
    if len(text) > MAX_SEGMENT_CHARS:
        return jsonify({
            'error': f'text must be at most {MAX_SEGMENT_CHARS} characters',
        }), 400
    return jsonify({'translated_text': segment_word(text)})


if __name__ == '__main__':
    app.run(debug=True)
