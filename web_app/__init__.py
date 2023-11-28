from flask import Flask, request, render_template, jsonify
import copy
from datetime import datetime
import json
from .analyzer import Analyzer

app = Flask(__name__)

a = Analyzer()


def copy_request_args():
    """
    Copy the reauest arguments from request.args to a
    normal modifiable dictionary. Return the dictionary.
    """
    query = {}
    if request.args is None or len(request.args) <= 0:
        return query
    for field, value in request.args.items():
        query[field] = copy.deepcopy(value)
    return query


@app.route('/')
def index():
    return render_template('index.html', languages=a.langs)


@app.route('/<lang>')
def index_lang(lang):
    if lang in a.langs:
        return render_template('index.html', lang=lang, languages=a.langs)
    return render_template('index.html', languages=a.langs)


@app.route('/<lang>/analyze')
def add_lemma(lang):
    if lang not in a.langs:
        return jsonify({'message': 'Wrong language.'})
    query = copy_request_args()
    if 'sentence' not in query or query['sentence'] in (None, ''):
        return jsonify({'message': 'Empty sentence sent.'})
    with open('query_log.txt', 'a', encoding='utf-8') as fLog:
        fLog.write(datetime.now().isoformat(timespec='seconds') + '\t' + lang + '\n')
        fLog.write(json.dumps(query, ensure_ascii=False, indent=2) + '\n\n')
    analysis = a.analyze(lang, query['sentence'])
    analysisHTML = render_template('analysis.html', words=analysis)
    return jsonify({'message': 'OK', 'analysis': analysisHTML})


if __name__ == "__main__":
    app.run(port=5500, host='0.0.0.0', debug=True)
