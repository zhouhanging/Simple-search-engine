from index import Indexer
import jieba
import operator
import math

"""
搜索
返回结果：(相关问题,相似度)列表
搜索步骤：
    1.分词
    2.计算tf-idf,找出候选doc
    3.排序
"""


class Searcher:
    def __init__(self, index):
        self.index = index
    #根据关键词query搜索
    def search(self, query):
        term_list = []
        query = query.split()
        for entry in query:
            # 分词
            term_list.extend(jieba.cut_for_search(entry))
        print(term_list)

        # 计算tf-idf,找出候选doc
        # TF−IDF=tf∗idf
        tf_idf = {}
        for term in term_list:
            if term in self.index.inverted:
                for doc_id, fre in self.index.inverted[term].items():
                    if doc_id in tf_idf:
                        tf_idf[doc_id] += (1 + math.log10(fre)) * self.index.idf[term]
                    else:
                        tf_idf[doc_id] = (1 + math.log10(fre)) * self.index.idf[term]
        # 排序
        sorted_doc = sorted(tf_idf.items(), key=operator.itemgetter(1), reverse=True)
        print(sorted_doc)
        res = [self.index.id_doc[doc_id] for doc_id, score in sorted_doc]
        print("res:")
        print(res)
        print("---")
        return res


# 生成摘要类
class CreateAbstract:
    def __init__(self, data, kv):  # 文本段和滑动窗口大小
        self.data = data[0]  # 只处理一段文本数据
        self.tfidf = MyTfIdf(data)  # 得到tfidf对象
        self.kv = kv  # 初始化设置窗口大小

    # 暴力查找法（可以优化，比如用kmp,或者python的s.index()）
    def s_match(self, s, s1):
        loc = list()
        l_s = len(s)
        l_s1 = len(s1)
        # 蛮力法字符串匹配
        for i in range(l_s - l_s1 + 1):
            index = i
            for j in range(l_s1):
                if s[index] == s1[j]:
                    index += 1
                else:
                    break
            if index - i == l_s1:
                loc.append(i)  # 将每个结果都装起来，而不是直接返回，保证查找到全部位置
        return loc

    # 找到每个词的位置
    def getLoc(self, keywords):
        locList = list()
        for kw in keywords:  # 对于每个词
            # print(kw)
            ll = self.s_match(self.data, kw)  # 找到每个词的位置
            locList.extend(ll)  # 将每个词的位置扩充装起来
        locList.sort()  # 排序一下
        # print('关键词的位置', locList)
        return locList

    # 拆分得到滑动窗口信息
    def getShingle(self, locList):  # 窗口大小
        txtLine = list()  # 切片文本
        for l in locList:
            txtLine.append(self.data[l:l + self.kv])  # 切片操作s[i:i+k]
        # print('得到的窗口信息', txtLine)
        return txtLine

    # 给生成的每段窗口打分
    def getScore(self, tfidfV, shingles, keywords):  # tfidf的值，生成的窗口信息,关键词列表
        score = dict()  # 每一窗口的分数字典
        for i, v in enumerate(shingles):
            if not score.get(i):
                score[i] = 0  # 每一段初始化是0
            for keyw in keywords:  # 对于每个关键词
                if keyw in v:
                    try:
                        score[i] += v.count(keyw) * tfidfV[keyw]  # count是计数，看keyworld在这里窗口出现了几次
                    except:
                        continue
        # 将字典排序
        sortedDic = sorted(score.items(), key=lambda t: t[1], reverse=True)  # 排序方法
        # print('窗口得分', sortedDic)
        return sortedDic

    # 返回摘要的结果
    def getResult(self, keywords):
        cut_words = ""
        seg_list = jieba.cut(keywords, cut_all=False)
        cut_words += (" ".join(seg_list))
        all_words = cut_words.split()
        tfidfV = self.tfidf.getTfIdfValues() 
         # 先算tfidf的分数
        locList = self.getLoc(all_words) 
         # 得到每个查询词的位置
        if len(locList) != 0:
            txtLine = self.getShingle(locList) 
             # 根据位置对文档进行窗口滑动切分
        else:
            txtLine = self.getShingle([50]) 
             # 根据位置对文档进行窗口滑动切分
        scores = self.getScore(tfidfV, txtLine, all_words)  
        # 得到每个窗口的分数
        try:
            maxShinge = txtLine[scores[0][0]]  # 返回得分最大的窗口
        except:
            return txtLine
        return maxShinge

# 摘要tfIdf计算
class MyTfIdf:
    def __init__(self, s):  # 初始化参数，即得到待操作的文本
        self.s = s
    """分词操作"""
    def fenci(self, s):
        seg_list = jieba.cut(s)
        result = []
        for seg in seg_list:
            seg = ''.join(seg.split())
            if (seg != '，' and seg != '？' and seg != '。' and seg != "\n" and seg != "\n\n"):
                result.append(seg)
        return result

    # 计算每个词在每段文本中的次数
    def getCount(self, data):
        docCount = list()
        for i, word in enumerate(data):
            vec = dict()
            for w in word:
                if not vec.get(w):
                    vec[w] = 1
                else:
                    vec[w] += 1
            docCount.append(vec)
        return docCount

    # 计算tf的值
    def tf(self, data):
        tf_word = []
        for i, doc in enumerate(data):
            docLen = len(doc)
            tf = dict()
            for w in doc:
                tf[w] = doc[w] / docLen
            tf_word.append(tf)
        return tf_word

    # 统计每个词在哪些文本中出现过
    def countWinDoc(self, data):
        countDic = dict()
        for i, v in enumerate(data):
            for w in v:
                if not countDic.get(w):
                    countDic[w] = set()  # 用set是为了去重
                countDic[w].add(i)
        return countDic

    # 计算idf的值
    def idf(self, data, docLen):
        idfDic = dict()
        for d in data:
            idfDic[d] = math.log(docLen / len(data[d]) + 1)  # data[d]+1，加1是为了防止分母为0
        return idfDic

    # 计算每个文本中每个词的tfidf的值
    def tfIdf(self, tf, idf):
        tfidf = list()
        for t in tf:
            _tfidf = dict()
            for w in t:
                _tfidf[w] = 1.0 * t[w] * idf[w]
            tfidf.append(_tfidf)
        return tfidf

    def getTfIdfValues(self):
        # 为每段文本实现分词
        if self.s:  # 如果没有传东西进来，我们就不进行tfidf计算
            cut_s = list()
            for v in self.s:
                cut_s.append(self.fenci(v))
            tfCount = self.getCount(cut_s)  # 统计每个文本中每个词出现的次数
            tf_result = self.tf(tfCount)  # 计算tf
            idfCount = self.countWinDoc(cut_s)  # 统计每个词在哪些文档中出现过
            idf_result = self.idf(idfCount, len(self.s))  # 计算idf的值
            tfIdfValue = self.tfIdf(tf_result, idf_result)  # 计算tf-idf
            return tfIdfValue[0]

#根据关键词得到 结果
class Result:
    def __init__(self,keyword):
        self.kView = 100  # 滑动窗口大小
        self.cut_words = ""
        self.keywords = keyword
        self.index = Indexer("article")
        self.searcher = Searcher(self.index)
        self.doc_list = self.searcher.search(self.keywords)

    def getResult(self):
        result = []
        try:
            for doc in self.doc_list:
                data = []
                data.append(doc.get('key'))
                data.append(doc.get('title'))
                str = doc.get('context')
                a = list()
                a.append(str)
                abstr = CreateAbstract(a, self.kView)
                txt = abstr.getResult(self.keywords)
                data.append(txt)
                result.append(data)
        except:
            print("")
        return result;

    def getUrl(self):
        url_list = []
        for doc in self.doc_list:
            url_list.append(doc.get('key'))
        return url_list

    def getTitle(self):
        title_list = []
        for doc in self.doc_list:
            title_list.append(doc.get('title'))
        return title_list

    def getText(self):
        try:
            text_list = []
            for doc in self.doc_list:
                str = doc.get('context')
                a = list()
                a.append(str)
                abstr = CreateAbstract(a, self.kView)
                txt = abstr.getResult(self.keywords)
                text_list.append(txt)
            return text_list
        except:
            return []

if __name__ == '__main__':
    # kView = 50  # 滑动窗口大小
    # cut_words = ""
    # keywords = "重庆巴南区"
    # index = Indexer("article")
    # searcher = Searcher(index)
    # doc_list = searcher.search(keywords)
    # for doc in doc_list:
    #     str = doc.get('context')
    #     a = list()
    #     a.append(str)
    #     abstr = CreateAbstract(a, kView)
    #     txt = abstr.getResult(keywords)
    #     print(doc.get('key'), doc.get('title'), txt)
    result = Result("阿里巴巴")
    doc_list = result.getResult()
    # print(type(doc_list))
    res={'url': '', 'titel': '', 'detail': ''}
    dics=[]
    for doc in doc_list:
        res['url']=doc[0]
        res['titel']=doc[1]
        res['detail']=doc[2]
        dics.append(res)
    print(dics)
        # print("doc:\n")
        # print(doc[0])
        # # print("\n")
        # print(doc[1])
        # # print("\n")
        # print(doc[2])

