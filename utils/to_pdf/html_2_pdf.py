# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/7/28 10:01
@Auth ： AJay13
@File ：html_2_pdf.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

'''
windows 需配置环境变量
linux 需下载 pdfkit
'''
import os
import re
import time

import pdfkit
import requests

from config import base_config

options = {
    'page-size': 'A4',  # 默认是A4 Letter  etc
    # 'margin-top':'0.05in',   #顶部间隔
    # 'margin-right':'2in',   #右侧间隔
    # 'margin-bottom':'0.05in',   #底部间隔
    # 'margin-left':'2in',   #左侧间隔
    'encoding': "UTF-8",  # 文本个数
    'dpi': '180',
    # 'image-dpi': '600',
    # 'image-quality': '94',
    # 'footer-font-size': '80',  # 字体大小
    'no-outline': None,
    "zoom": 1.0,  # 网页放大/缩小倍数
}
# 爬虫数据配置
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}


def extra_footmark():
    '''
    pdf中添加额外的脚标内容，属于额外的备注部分
    :return:
    '''
    html = '<br>'
    html += "<a href='http://wechat.doonsec.com'>声明：pdf仅供学习使用，一切版权归原创公众号所有；<br>" \
            "建议持续关注原创公众号获取最新文章，学习愉快--洞见网安！</a>"
    return html


def get_wechat_html(url):
    try:
        req = requests.get(url=url, headers=HEADERS)
        content = req.text.replace('data-src="https', 'src="https')
        content += extra_footmark()
        if base_config.is_save_html:
            html_name = '{}_{}_{}.html'.format(publish_time, account, title)
            html_name = validateTitle(html_name)  # 格式化html_name名称 替换为_
            with open(os.path.join(base_config.HTML_PATH, html_name), 'w', encoding='utf-8')as f:
                f.write(content)
        return content

    except Exception as e:
        return False


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def html2pdf(publish_time, account, title, url):
    '''
    保存html到固定的文件夹中（static/pdf or static/html）2020_02_02_12:12:12_account_title.pdf
    :param publish_time:
    :param account:
    :param title:
    :param url:
    :return:
    '''
    start_time = time.time()
    pdf_name = '{}_{}_{}.pdf'.format(publish_time, account, title)
    pdf_name = validateTitle(pdf_name)  # 格式化pdf名称 替换为_
    if os.path.exists(os.path.join(base_config.PDF_PATH, pdf_name)):
        return False
    wechat_html = get_wechat_html(url)
    if isinstance(wechat_html, str):
        try:
            pdfkit.configuration(wkhtmltopdf='')
            pdfkit.from_string(wechat_html, os.path.join(base_config.PDF_PATH, pdf_name), options=options)
        except Exception as e:
            print('', e)

    use_time = time.time() - start_time
    print('', use_time)
    return True


if __name__ == '__main__':
    account = 'asda'
    title = '渣打阿萨打'
    url = 'https://mp.weixin.qq.com/s?__biz=MzIwMDcyNzM0Mw==&mid=2247484330&idx=1&sn=fa5f3c3de8737f3ddbc5622917b2c852&chksm=96f98deaa18e04fcb69450e54bad2449548037c6720a3a5193aeb9e13204c4e60f2124489212&scene=27&key=0e6b2ba44e52e4c43cd4361dab44242d119a890b51f0a09c6dcc'

    publish_time = '2020_2020_12:12'

    import csv

    with open('阿里云.csv', 'r')as f:
        for row in csv.reader(f):
            print(row)
            account = row[0]
            title = row[1]
            url = row[2]
            publish_time = row[3]
            html2pdf(account=account, title=title, publish_time=publish_time, url=url)
