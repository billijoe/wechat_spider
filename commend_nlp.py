#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'AJay'
__mtime__ = '2020/1/10 0010'

"""
import matplotlib.pyplot as plt
import jieba.analyse
import jieba
from snownlp import SnowNLP
import collections # 词频统计库
def get_nlp_num():
    with open('comment.txt','r+',encoding='utf-8')as f:
        for comment in  f.read().split('\n'):
            if comment is '':
                continue
            print(comment)
            s1 = SnowNLP(comment)
            nlp_num =s1.sentiments
            with open('nul_num.txt','a+',encoding='utf-8')as f:
                f.write(str(nlp_num)+'\n')

def get_wc():
    with open('comment.txt','r+',encoding='utf-8')as f:
        object_list = f.read().split('\n')
    text = '。'.join([i for i in object_list])
    # result = jieba.analyse.textrank(text, topK=int(100), withWeight=True)
    result=[('没有', 1.0), ('公司', 0.5503626525792503), ('知道', 0.49172628880757363), ('时候', 0.4746258188049866), ('学习', 0.4736603169546652), ('技术', 0.4688954933069456), ('问题', 0.4667594274502087), ('希望', 0.4377599252502788), ('觉得', 0.4238676517251337), ('感觉', 0.4214092007838836), ('应该', 0.4090917594155355), ('火绒', 0.40567253813593657), ('看到', 0.4015396335883029), ('需要', 0.3808954029477508), ('微笑', 0.37468052547884334), ('还有', 0.3556881089246677), ('文章', 0.35334692395655687), ('工作', 0.35135269991458884), ('奸笑', 0.3457844009842432), ('可能', 0.34526624613322876), ('不能', 0.33827624590917743), ('不会', 0.32964918100536156), ('喜欢', 0.28679902960740744), ('中国', 0.28512903986253496), ('大家', 0.2812643531584526), ('时间', 0.2773995895840229), ('用户', 0.27657997565459164), ('手机', 0.27402521268642016), ('支持', 0.27394097910071813), ('软件', 0.26882800591329786), ('东西', 0.2674566002239858), ('数据', 0.2671529072895853), ('开始', 0.2657054815505495), ('广告', 0.26445519825327335), ('出来', 0.24236221049939505), ('程序员', 0.2412324381040155), ('产品', 0.2295163808919571), ('感谢', 0.21598929402552353), ('发现', 0.21148914474406022), ('使用', 0.2078499672085337), ('有点', 0.2072172145512025), ('电脑', 0.20660860307338635), ('微信', 0.2041287944364051), ('系统', 0.19966592764730365), ('信息', 0.19572327311671206), ('关注', 0.19142128461965588), ('代码', 0.19125249516882073), ('作为', 0.19037563281042333), ('只能', 0.18186734254560835), ('老师', 0.17999949365841855), ('分享', 0.1774365705444045), ('公众', 0.17552871619926183), ('企业', 0.17479425232413456), ('知识', 0.16930857880493147), ('偷笑', 0.16860389434249487), ('加油', 0.1674621109887531), ('推荐', 0.1633116250939277), ('能力', 0.1613289551684993), ('个人', 0.15677495421894797), ('开发', 0.15496441355175827), ('百度', 0.1530944834999498), ('行业', 0.15145947411479363), ('功能', 0.15144192946323357), ('发展', 0.15076003546641187), ('朋友', 0.14875810784402202), ('互联网', 0.1483145426169239), ('看看', 0.14830178909751543), ('作者', 0.1482324609941199), ('生活', 0.1479088135042584), ('苹果', 0.14607203941166394), ('世界', 0.1454938012594488), ('起来', 0.14536158516539469), ('结果', 0.14323138813312508), ('网络', 0.13958655386193414), ('流泪', 0.13910687737622376), ('内容', 0.13896969954598226), ('甲哥', 0.13848633596065402), ('想要', 0.1354108405435915), ('期待', 0.13385751336377813), ('平台', 0.13235581531863488), ('才能', 0.13186726691961306), ('选择', 0.13135172472634135), ('有没有', 0.12932673554872898), ('比如', 0.1284918729897384), ('社会', 0.12827719928615136), ('游戏', 0.1274075355763478), ('视频', 0.12718486231888254), ('国家', 0.12476090951757655), ('程序', 0.1245773451884257), ('了解', 0.12290461406383421), ('不用', 0.12188151628079134), ('肯定', 0.12186077775702364), ('继续', 0.12096636717368692), ('漏洞', 0.11930098055171653), ('专业', 0.11891508082589326), ('事情', 0.11826404857033418), ('好像', 0.117683293784512), ('不了', 0.116640826901119), ('项目', 0.11531512670866714), ('网站', 0.11492084220391834)]
    keywords = dict()
    for i in result:
        keywords[i[0]] = i[1]
    print(result)
    # print(text)
    # seg_list_exact = jieba.cut(text, cut_all=True)  # 精确模式分词
    # word_counts = collections.Counter(seg_list_exact)  # 对分词做词频统计
    # word_counts_top10 = word_counts.most_common(100)  # 获取前10最高频的词
    # print(word_counts_top10)

    import numpy as np  # numpy数据处理库

    from wordcloud import WordCloud# 词云展示库
    from PIL import Image  # 图像处理库
    # 词频展示
    mask = np.array(Image.open('./static/favicon.ico')) # 定义词频背景
    wc = WordCloud(font_path='./utils/captcha/simhei.ttf',max_words=int(100), width=805, height=304)
    wc.generate_from_frequencies(keywords)
    plt.imshow(wc)
    plt.axis("off")
    wc.to_file('./static/front/img/comment.png')
    print('词云图生成完成')

if __name__ == '__main__':
    get_wc()