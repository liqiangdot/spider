# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#import requests
#proxies = {"https": "http://127.0.0.1:1082"}
#response = requests.get("https://mickey1124.pixnet.net/blog", proxies=proxies)
#requests.encoding = "utf-8"
#html = response.text.encode('iso-8859-1').decode('utf-8')
#print(html)

#TODO:
# 1，按照分类获取信息。
# 2，提取其中圣经经文并出处。

import json
from zhconv import convert
from requests_html import HTMLSession
from requests_html import HTML


def get_common_content(common_str):
    html = HTML(html=common_str)
    xpath_str = "//*[contains(@class,'single-post')]"
    common_list = []
    for item in html.xpath(xpath_str):
        xpath_str = "//*[contains(@class,'post-text')]"
        common_text = str(item.xpath(xpath_str, first=True).text)
        xpath_str = "//*[contains(@class,'post-time')]"
        common_time = str(item.xpath(xpath_str, first=True).text)
        xpath_str = "//*[contains(@class,'user-name')]"
        common_author = str(item.xpath(xpath_str, first=True).text)
        common_info = "作者：\n" + common_author + "\n时间：" + common_time + "\n" + common_text
        common_list.append(common_info)
        #print("时间：\n" + common_time)
        #print("作者：\n" + common_author)
        #print("内容：\n" + common_text)

    return common_list

def get_indexs():
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get('https://mickey1124.pixnet.net/blog', proxies=proxies)
    text_link_dict = {}

    for i in range(1, 23):
        xpath_str = "//*[@id=\"category\"]/div/ul/li[" + str(i) + "]"
        text = (r.html.xpath(xpath_str, first=True).text)
        text_link = (r.html.xpath(xpath_str, first=True).absolute_links)
        text_link_dict[text] = text_link
    return text_link_dict

def get_common(url):
    common_url = url + "/comments"
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get(common_url, proxies=proxies)
    r_dict = r.json()
    common_list = get_common_content(r_dict['list'])
    return common_list
    #print(common_list)
    #html = HTML(html=r_dict['list'])
    #xpath_str = "//*[contains(@class,'post-text')]"
    #text = str(html.xpath(xpath_str, first=True).text)
    #print("时间" + text)
    #print("作者" + author)
    #print("内容" + common_str)
    #print(html.html)
    #print(html.attrs)
    #xpath_str = "//*[@class=\"comment-text\"]"
    #comment = html.find("post-text")
    #comment = html.xpath(xpath_str, first=True)
    #print(r_dict['list'])
    #print(r_dict['total'])
    #r = r_dict['list']
    #print(comment)

def get_page(url):
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get(url, proxies=proxies)
    #r.html.render()
    #links = r.html.absolute_links
    #for link in links:
    #    print(link)
    #print(r.html.text)
    xpath_str = "//*[@id=\"article-box\"]/div/ul/li[1]"
    page_time = r.html.xpath(xpath_str, first=True).text
    print("时间：" + page_time)

    xpath_str = "//*[@id=\"article-329364895\"]"
    title =r.html.xpath(xpath_str, first=True).text
    print("标题：" + title)
    xpath_str = "//*[@id=\"article-content-inner\"]"
    content = r.html.xpath(xpath_str, first=True).text

    content = convert(content, 'zh-hans')
    print("内容：" + content)
    common_list = get_common(url)
    print(common_list)
    return

def get_page_text():
    text = ""
    return text;
def get_page_bible():
    bible = ""
    return bible

page = get_page('https://mickey1124.pixnet.net/blog/post/329364895')
#print(page)

#with open("a.txt",'w',encoding='utf-8') as f:
#    f.write(response.text)


#import requests
#import random

#proxies = [
#    {'http':'socks5://127.0.0.1:1081'},
#    {'https':'socks5://127.0.0.1:1081'}
#]
#proxies = random.choice(proxies)
#print(proxies)
#url = 'https://mickey1124.pixnet.net/blog'
#try:
#    response = requests.get(url,proxies=proxies) #使用代理
#    print(response.status_code)
#    if response.status_code == 200:
#        print(response.text)
#except requests.ConnectionError as e:
#    print(e.args)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
