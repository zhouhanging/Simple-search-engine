import os
import jieba
import math
from doc import Doc

#计算文档排序

class Indexer:
    inverted = {}  # 记录词所在文档及词频
    idf = {}  # 词的逆文档频率
    id_doc = {}  # 文档与词的对应关系

    def __init__(self, file_path):
        self.doc_list = [] #文档列表
        self.index_writer(file_path) #文档路径

    def index_writer(self, file_path):
        for dirpath, dirnames, filenames in os.walk(file_path):
            for i in filenames:
                with open(file_path+"\\"+i, 'r', encoding='utf-8') as f:
                    key, title, context = f.read().split('\t\t')
                    #读取文件 并根据关键词存入 关键词和网页题目，以及内容。
                    doc = Doc()
                    doc.add('key', key)
                    doc.add('title', title)
                    doc.add('context', context)
                    self.doc_list.append(doc)
        self.index()

    def index(self):
        doc_num = len(self.doc_list)  # 文档总数
        for doc in self.doc_list:
            key = doc.get('key')
            # 正排
            self.id_doc[key] = doc
            # 倒排
            term_list = list(jieba.cut_for_search(doc.get('title')))  # 分词 列表
            for t in term_list:
                if t in self.inverted:  # 如果分词在序列中
                    if key not in self.inverted[t]: #但关键词步骤序列帧
                        self.inverted[t][key] = 1
                    else:
                        self.inverted[t][key] += 1
                else:
                    self.inverted[t] = {key: 1}
        for t in self.inverted:
            self.idf[t] = math.log10(doc_num / len(self.inverted[t]))
            #倒排索引建立
        print("inverted terms:%d" % len(self.inverted)) #
        print("index done")


if __name__ == '__main__':
    print("index")
    Indexer("article")