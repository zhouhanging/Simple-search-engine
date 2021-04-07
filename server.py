# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for
from index import Indexer
from search import Searcher
from search import Result
import jieba
from urllib import parse
import json

app = Flask(__name__, static_url_path='')


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search', query=query))
    return render_template('index.html')


@app.route("/search/<query>", methods=['POST', 'GET'])
def search(query):
    result = Result(query)
    doc_list = result.getResult()
    terms = list(jieba.cut_for_search(query))
    doc_list = highlight(doc_list,terms)
    print(doc_list)
    return render_template('search.html', doc_list=doc_list, value=query, length=len(doc_list))


def highlight(docs, terms):
    for doc in docs:
        for term in terms:
            title = doc[1]
            content = doc[2]
            doc[1] = title.replace(term, '<em><font color="red">{}</font></em>'.format(term))
            doc[2] = content.replace(term, '<em><font color="red">{}</font></em>'.format(term))
            # content = content.replace(term, '<em><font color="red">{}</font></em>'.format(term))
    return docs


index = Indexer("docs.txt")
searcher = Searcher(index)

if __name__ == "__main__":
    app.run(host='localhost', port=8888, debug=True)
