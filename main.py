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
from requests_html import HTMLSession
from requests_html import HTML


def get_test():
    #import requests_html

    #session = requests_html.HTMLSession()
    #r = session.get('https://www.meleenumerique.com/scientist_comite')
    #r.html.render(sleep=5, timeout=8)
    #for item in r.html.xpath("//*[contains(@class,'speaker-name')]"):
    #    print(item.text)

    html_str = "\n<ul class=\"single-post\">\n        <li class=\"post-info\">\n        <a name=\"comment-2745274\"> </a>\n        <span class=\"floor\">#1</span>\n        <span class=\"user-name\"><img class=\"identity-provider comment-icon lazy\" data-original=\"//front.pixfs.net/comment/images/openid-pixnet-icon.gif\" width=\"16\" height=\"16\"> Brandweer</span>                                <span class=\"post-time\">於 2020/12/15 05:31</span>\n            </li>\n    <li class=\"post-photo\">\n        <img src=\"//s.pixfs.net/blog/images/choc/avatar-neutral.png\" alt=\"Brandweer\" height=\"90\" width=\"90\">    </li>\n        <li class=\"post-text\">\n     dddd       <p id=\"comment-2745274\"></p>\n                    <br />\r\n\r\n        </li>\n              </ul>\n"
    html = HTML(html=html_str)
    print(html.html)

    xpath_str = "//*[contains(@class,'post-text')]"
    text = str(html.xpath(xpath_str, first=True).text)
    print("C" + text)

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
    print(r.json())
    r_dict = r.json()
    html = HTML(html=r_dict['list'])
    #print(html.html)
    #print(html.attrs)
    xpath_str = "//*[@class=\"comment-text\"]"
    comment = html.find("post-text")
    #comment = html.xpath(xpath_str, first=True)
    #print(r_dict['list'])
    #print(r_dict['total'])
    #r = r_dict['list']
    #print(comment)

def get_page(url):
    get_common(url)
    return url
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get(url, proxies=proxies)
    #r.html.render()
    links = r.html.absolute_links
    for link in links:
        print(link)
    print(r.html.text)
    xpath_str = "//*[@id=\"article-box\"]/div/ul"
    title =r.html.xpath(xpath_str, first=True).text
    #print("标题：" + title)
    xpath_str = "//*[@id=\"article-content-inner\"]"
    content = r.html.xpath(xpath_str, first=True).text
    #print("内容：" + content)
    xpath_str = "//*[@id=\"comment-text\"]"
    comment = r.html.xpath(xpath_str, first=True).html
    print("评论：" + comment)
    return comment

def get_page_text():
    text = ""
    return text;
def get_page_bible():
    bible = ""
    return bible

get_test()
#page = get_page('https://mickey1124.pixnet.net/blog/post/329364895')
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
