# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for,make_response,jsonify
from index import Indexer
from search import Searcher
from search import Result
import jieba
from flask_cors import *  # 导入模块
import requests
from urllib import parse
import json

app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] =False

#
# @app.route("/", methods=['POST', 'GET'])
# def main():
#     if request.method == 'POST' and request.form.get('query'):
#         query = request.form['query']
#         return redirect(url_for('search', query=query))
#     # return render_template('index.html')
#     return 'hello'

@app.route('/', methods=["GET", "POST"])  # GET 和 POST 都可以
def get_data():
    # 假设有如下 URL
    # http://10.8.54.48:5000/index?name=john&age=20
    # 可以通过 request 的 args 属性来获取参数
    name = request.args.get("name")
    # 经过处理之后得到要传回的数据
    # 将数据再次打包为 JSON 并传回
    res = 'name'+'age'
    return res

@app.route("/api/search/", methods=['POST', 'GET'])
# @cross_origin()
def search():
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    state= request.args['state']
    print(state)
    result = Result(state)
    doc_list = result.getResult()
    terms = list(jieba.cut_for_search(state))
    doc_list = highlight(doc_list,terms)
    # print
    res = {'url': '', 'titel': '', 'detail': ''}
    dics = []
    for doc in doc_list:
        res['url'] = doc[0]
        res['titel'] = doc[1]
        res['detail'] = doc[2]
        dics.append(res)
    print(dics)
    # dics.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    # jsons=json.dumps(dics)
    # return dics.json()

    method = request.method
    res = make_response(jsonify(token=123456, gender=0, method=method,data=dics))  # 设置响应体
    res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res
    # return jsons

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
    CORS(app, supports_credentials=True)  # 设置跨域
    app.run(host='localhost', port=8888, debug=True)
