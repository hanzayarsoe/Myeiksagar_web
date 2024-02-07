from flask import Flask, jsonify, render_template, request
from seg import segment_word

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def wordTranslation():
    data = request.json
    text_to_translate = data.get('text')
    translated_text = segment_word(text_to_translate)

    return jsonify({'translated_text': translated_text})


if __name__ == '__main__':
    app.run(debug=True)
