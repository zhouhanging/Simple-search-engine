import requests
from bs4 import BeautifulSoup
import re
import os
import logging
import time

def crawl_content(url):
    """"提取网页内容"""
    requests.DEFAULT_RETRIES = 5
    logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1', }
    resq = requests.get(url, headers=header, verify=False)  # 去掉https 的验证
    print(resq.status_code)
    if resq.status_code!=200:
        return 0
    # if resq=='Response [200]'
    # resq = requests.get(url)#通过get请求得到url链接网页的返回对象
    resq.encoding = 'utf-8'#将该网页的编码设置为utf-8
    content = resq.text #content代表网页的文本信息，即源代码
    return content

def extract_title(content):
    """"得到网页标题"""
    soup = BeautifulSoup(content, "html.parser")
    t = soup.find('title')
    t=remove_any_tag(str(t))
    # with codecs.open("title.txt", 'a+', encoding='utf-8') as file_out:
    #     file_out.write(remove_any_tag(str(t)))
    return t

def remove_empty_line(content):
    """移除content中的空行"""
    r = re.compile(r"^\s+$", re.M | re.S)  # 代表匹配全是空白字符的行
    s = r.sub('', content)
    r = re.compile(r"\n+", re.M | re.S)  # 代表匹配至少一个空行
    s = r.sub('\n', s)
    return s

def remove_js_css(content):
    """移除content中的script、style、meta、注释等脚本"""
    r = re.compile(r'''<script.*?</script>''', re.I | re.M | re.S)
    s = r.sub('', content)
    r = re. compile(r'''<style.*?</style>''', re.I | re.M | re.S)
    s = r.sub('', s)
    r = re.compile(r'''<!--.*?-->''',re.I | re.M | re.S)
    s = r.sub('', s)
    r = re.compile(r'''<meta.*?>''', re.I | re.M | re.S)
    s = r.sub('', s)
    r = re.compile(r'''<ins.*?</ins>''', re.I | re.M | re.S)
    s = r.sub('', s)
    r = re.compile(r'''<link.*?>''', re.I | re.M | re.S)
    s = r.sub('', s)
    return s

def remove_any_tag (s):
    """移除content中的tag"""
    s = re.sub(r'''<[^>]+>''', '', s)
    return s.strip()#strip() 方法用于移除字符串头尾指定的字符（默认为空格）

def extract_text(content):
    #remove_empty_line会移除content中的空行以及英文字母：
    s = remove_empty_line(remove_js_css(content)) #remove_js_css移除content中的script、style、meta、注释等脚本：
    s = remove_any_tag(s) #该方法会移除content中的js以及css等脚本
    s = remove_empty_line(s) #remove_empty_line会移除content中的空行以及英文字母：
    # print("1:",s)
    # with codecs.open("content.txt", 'w', encoding='utf-8') as file_out:
    #     file_out.write(s)
    return s

def extract_a_label(content):
    soup = BeautifulSoup(content,'html.parser')
    alink = soup.find_all('a')
    return alink

def remove(str):
    str = str.replace('\n', '')
    str = str.replace(' ', '')
    str = str.replace('\t', '')
    str = str.replace('\r', '')
    return str

def remove_content(str):
    str = re.sub("[A-Za-z0-9\：\·\—\，\。\“ \”]", "", str)
    return str

if __name__ == '__main__':
    # url = "https://hao.360.com/"
    # url="https://www.sina.com.cn/"
    #种子站点
    url="https://www.baidu.com"
    # url="https://www.douban.com/"
    # url = "http://tieba.baidu.com/p/2460150866"
    #set() --> 不重复元素集
    re_url=set()
    center=set()
    dele=set()
    re_url.add(url)#加入种子站点
    done_url=set()
    download_txt=dict()
    count=0
    x = 0 #文件夹名字
    path = "./正文"
    # 判断路径是否存在，若不存在则创建
    if not os.path.isdir(path):
        os.makedirs(path)
    print("种子站点：",re_url)
    # for re_link in re_url:
    #     download_txt['id']=re_link
    #     content = crawl_content(re_link) #网页源码
    #     t=extract_title(content) #网页标题
    #     download_txt['title']=t
    #     s=extract_text(content) #网页正文
    #     download_txt['mainContent']=s
    #     #将网页 链接 标题 正文 存入文件
    #     f = open(path + "/" + str(x) + ".txt", "w+")
    #     # f.write(str(download_txt))
    #     f.write('id：'+download_txt['id']+'\n')
    #     f.write('title：'+download_txt['title']+'\n')
    #     f.write('mainContent：'+download_txt['mainContent'])
    #     f.close()
    #     x=x+1 #文件夹名字
    #
    #     alink = extract_a_label(content)  # 链接
    #     f_a = open('link.txt', 'w', encoding='utf-8')
    #     for link in alink:
    #         a = link.get('href')
    #         key = link.string
    #         if key != None and a != None:
    #             f_a.write(a)
    #             re_url.add(a) #往待爬取队列里添加链接
    #             f_a.write(' ')
    #             f_a.write(key)
    #             f_a.write('\n')
    # for re_link in re_url:
    #     center.add(re_link)
    print('re_url1111:', re_url)
    #while循环
    # for re_link in re_url:
    while re_url:
        for re_link in re_url:
            dele.add(re_link)
            download_txt['id']=remove(re_link)
            count+=1
            if count==2:
                time.sleep(5)
                count=0
            try:
                content = crawl_content(re_link) #网页源码
            except:
                time.sleep(5)
                continue
            try:
                t=extract_title(content) #网页标题
            except:
                continue
            download_txt['title']=remove(t)
            try:
                s=extract_text(content) #网页正文
            except:
                continue
            download_txt['mainContent']=remove_content(remove(s))
            #将网页 链接 标题 正文 存入文件
            f = open(path + "/" + str(x) + ".txt", "w+",encoding='utf-8')
            # f.write(str(download_txt))
            f.write(download_txt['id']+'\t\t')
            f.write(download_txt['title']+'\t\t')
            f.write(download_txt['mainContent'])
            f.close()
            x=x+1 #文件夹名字
            alink = extract_a_label(content)  # 链接
            f_a = open('link.txt', 'a', encoding='utf-8')
            for link in alink:
                a = link.get('href')
                key = link.string
                # if key != None and a != None:
                #丢掉无效链接
                if a!= None and a.startswith('http'):
                    f_a.write(a)
                    center.add(a) #往待爬取集合里添加链接
                    f_a.write(' ')
                    # f_a.write(key)
                    f_a.write('\n')
        for add_link in center:
            re_url.add(add_link)
        print("添加url列表：",center,"添加长度：",len(center),"总长度：",len(re_url))
        print("删除url列表：", dele, '删除长度：', len(dele), "总长度：", len(re_url))
        for delet in dele:
            re_url.remove(delet)
        center.clear()
        dele.clear()
        # print("remove",center)
        # print('re_url22222:', re_url)
        # print('center:',center)
