# coding=utf-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import time
import random
import urllib3
import pickle
import opencc
from ebooklib import epub
from zhconv import convert
from threading import Thread
from requests_html import HTML
from requests_html import HTMLSession
import threading
urllib3.disable_warnings()

root_url = "https://mickey1124.pixnet.net/"
ret_dict = {}

def opencc_t2s(s):
    cc = opencc.OpenCC('t2s')
    return cc.convert(s)

def add_epub_item(page_dict):
    style = '''BODY { text-align: justify;}'''
    default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)

    item_list = []
    for page_title in page_dict:
            item = epub.EpubHtml(title=page_title, file_name=page_title + '.xhtml')
            page = "<br />".join(page_dict[page_title].split("\n"))
            item.content = '<h1>' + page_title + '</h1><p>' + page + '</p>'
            item.set_language('zh')
            item.properties.append('rendition:layout-pre-paginated rendition:orientation-landscape rendition:spread-none')
            item.add_item(default_css)
            item_list.append(item)
    return item_list

def create_pub2(category_dict):
    book = epub.EpubBook()

    # add metadata
    book.set_identifier(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    book.set_title('基督教小小羊園地')
    book.set_language('zh')
    book.add_author('小小羊')

    # define intro chapter
    c1 = epub.EpubHtml(title='简介', file_name='intro.xhtml', lang='zh')
    c1.content = u'<html><head></head><body><h1>約翰福音8：32</h1><p>你們必曉得真理，真理必叫你們得以自由</p></body></html>'

    # add chapters to the book
    book.add_item(c1)
    #book.add_item(c2)

    # create table of contents
    # - add manual link
    # - add section
    # - add auto created links to chapters

    book.toc = (epub.Link('intro.xhtml', '简介', 'intro'), )
    pa_list = []
    for category in category_dict:  # 分类字典，分类 + 页面字典
        items = add_epub_item(category_dict[category])
        for cx in items:
            book.add_item(cx)
            pa_list.append(cx)

        book.toc = book.toc + ((epub.Section(category), tuple(items)), )

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif; white-space: pre-line;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spine
    book.spine = ['nav', c1]
    book.spine = book.spine + pa_list

    epub.write_epub('all.epub', book, {})

    return

def create_pub(category_dict):
    book = epub.EpubBook()

    # add metadata
    book.set_identifier(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    book.set_title('基督教小小羊園地')
    book.set_language('zh')
    book.add_author('小小羊')

    # define intro chapter
    c1 = epub.EpubHtml(title='简介', file_name='intro.xhtml', lang='zh')
    c1.content = u'<html><head></head><body><h1>約翰福音8：32</h1><p>你們必曉得真理，真理必叫你們得以自由</p></body></html>'

    # add chapters to the book
    book.add_item(c1)
    #book.add_item(c2)

    # create table of contents
    # - add manual link
    # - add section
    # - add auto created links to chapters

    book.toc = (epub.Link('intro.xhtml', '简介', 'intro'), )
    pa_list = []
    for category in category_dict:  # 分类字典，分类 + 页面字典
        items = add_epub_item(category_dict[category])
        for cx in items:
            book.add_item(cx)
            pa_list.append(cx)

        book.toc = book.toc + ((epub.Section(category), tuple(items)), )

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif; white-space: pre-line;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spine
    book.spine = ['nav', c1]
    book.spine = book.spine + pa_list

    epub.write_epub(category + '.epub', book, {})

    return

lock = threading.Lock()
def  single_down_category(links, category, pthread_num ):
    i = 0
    category_dict = {}
    page_dicts = {} # dicts that page content
    for link in links:
        file_str = "\n@@@@@@ " + category + "@@@@@@\n"
        wait_time = random.randint(0, 6)
        time.sleep(wait_time)
        i += 1
        print("(" + str(wait_time) + ")即将下载链接(" + category + ")[" + str(i) + "]线程号[" + str(pthread_num) + ")]：" + link)
        page_dict = get_page(link)
        for title in page_dict:
            file_str += "\n&&&&&& " + title + " &&&&&&\n"
            file_str += "\n" + page_dict[title] + "\n"
            page_dicts.update(page_dict)

        lock.acquire()
        write_file(file_str)
        lock.release()

    category_dict[category] = page_dicts
    global ret_dict
    ret_dict.update(category_dict)

    create_pub(category_dict)
    return

def get_host_content():
    host_str = ""
    file_str = ""
    absolute_dict = {}
    if os.path.exists("data.txt"):
        f = open("data.txt", 'rb')
        absolute_dict = pickle.load(f)
    else:
        absolute_dict = get_indexs()
        f = open('data.txt', 'wb')
        pickle.dump(absolute_dict, f)

    i = 0
    for category in absolute_dict:
        for link in absolute_dict[category]:
            i += 1
    print("即将下载链接总数[" + str(i) + "]")

    i = 0
    process_list = []
    for category in absolute_dict:
        # index -> category
        # absolute_dict[index] -> link
        i += 1
        file_str = "\n@@@@@@ " + category + "@@@@@@\n"
        t = Thread(target=single_down_category, args=(absolute_dict[category], category, i))
        process_list.append(t)
        t.start()
        print("即将下载第[" + str(i) + "]线程：" + category)

    for t in process_list:
        t.join()

    #print(file_str)
    create_pub2(ret_dict)
    return

def get_common_content(common_str):
    html = HTML(html=common_str)
    xpath_str = "//*[contains(@class,'single-post')]"
    common_list = []
    for item in html.xpath(xpath_str):
        xpath_str = "//*[contains(@class,'post-text')]"
        common_text = str(item.xpath(xpath_str, first=True).text)

        common_time = ""
        xpath_str = "//*[contains(@class,'post-time')]"
        ret_time = item.xpath(xpath_str, first=True)
        if ret_time is None:
            print("注释时间为空")
        else:
            common_time = str(item.xpath(xpath_str, first=True).text)

        common_author = ""
        xpath_str = "//*[contains(@class,'user-name')]"
        ret_author = item.xpath(xpath_str, first=True)
        if ret_author is None:
            print("注释作者为空")
        else:
            common_author = str(item.xpath(xpath_str, first=True).text)
        common_info = "作者：" + common_author + "\n时间：" + common_time + "\n" + common_text
        common_list.append(common_info)
        #print("时间：\n" + common_time)
        #print("作者：\n" + common_author)
        #print("内容：\n" + common_text)

    return common_list

def write_file(s):
    fo = open("1.txt", "a", encoding="utf-8")
    fo.write(s)
    fo.close()
    return

def write_error(s):
    fo = open("err.txt", "a", encoding="utf-8")
    fo.write(s)
    fo.close()
    return

def get_indexs():
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get('https://mickey1124.pixnet.net/blog', proxies=proxies, verify=False)
    absolute_dict = {}

    for i in range(1, 24):  # 1 ~ 24
        xpath_str = "//*[@id=\"category\"]/div/ul/li[" + str(i) + "]"
        text_title = (r.html.xpath(xpath_str, first=True).text)
        print("分类名称：" + text_title)
        text_links = (r.html.xpath(xpath_str, first=True).absolute_links)
        tmp_list = []
        for link in text_links:
            print("当前序号：" + str(i) + " - 23")
            i = i + 1
            print("分类链接：" + link)
            page_number = get_catagory_pages(link)
            print("分类页码：" + str(page_number))
            for i in range(1, page_number + 1):
                url = link + "/" + str(i)
                ret_list = get_category_links(url)
                tmp_list.extend(ret_list)

        absolute_dict[text_title] = tmp_list

    return absolute_dict

def get_last_number(url):
    end = "/"
    return url[url.rfind(end) + 1:]

def get_catagory_pages(url):
    proxies = {"https": "http://127.0.0.1:1082"}
    post_link = "https://mickey1124.pixnet.net/blog/post/"

    page_list = []
    self_number = get_last_number(url)

    session = HTMLSession()
    r = session.get(url, proxies=proxies, verify=False)

    for link in r.html.absolute_links:
        ret = link.find("comments")
        if ret != -1:
            continue

        ret = link.find(url)
        if ret != -1:
            page = get_last_number(link)
            if page != self_number:
                page_list.append(int(page))

    if len(page_list):
        page_total = max(page_list)
    else:
        page_total = 1
    return page_total

def get_category_links(url):
    proxies = {"https": "http://127.0.0.1:1082"}
    post_link = "https://mickey1124.pixnet.net/blog/post/"
    link_list = []

    session = HTMLSession()
    r = session.get(url, proxies=proxies, verify=False)

    for link in r.html.absolute_links:
        ret = link.find("comments")
        if ret != -1:
            continue

        ret = link.find(post_link)
        if ret != -1:
            link_list.append(link)

    return link_list

def get_link_exceptions(url):
    try:
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
        proxies = {"https": "http://127.0.0.1:1082"}
        session = HTMLSession()
        r = session.get(url, proxies=proxies, headers={'user-agent': ua}, verify=False, timeout=12)
        r.raise_for_status()

    except HTMLSession.exceptions.HTTPError as errh:
        print("Http Error[" + url + "]:", errh)
        write_error(url)
    except HTMLSession.exceptions.ConnectionError as errc:
        print("Error Connecting" + url + "]:", errc)
        write_error(url)
    except HTMLSession.exceptions.Timeout as errt:
        print("Timeout Error" + url + "]:", errt)
        write_error(url)
    except HTMLSession.exceptions.RequestException as err:
        print("OOps[" + url + "]: Something Else", err)
        write_error(url)
    except:
        write_error(url)

    return r

def get_common(url):
    url = url + "/comments"
    i = 0
    r = get_link_exceptions(url)
    while i < 3:
        if r.strip() == "":
            i = i + 1
            time.sleep(3)
            r = get_link_exceptions(url)
        else:
            break

    '''
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get(url, proxies=proxies, verify=False)
    '''
    r_dict = r.json()

    common_list = get_common_content(r_dict['list'])
    return common_list

def get_page(url):
    page_dict = {}
    r = get_link_exceptions(url)
    '''
    proxies = {"https": "http://127.0.0.1:1082"}
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
    session = HTMLSession()
    r = session.get(url, proxies=proxies, headers={'user-agent': ua}, verify=False, timeout=12)
    #r.html.render(scrolldown=5,sleep=3)
    '''
    self_number = get_last_number(url)
    xpath_str = "//*[@id=\"article-box\"]/div/ul/li[1]"
    page_time = r.html.xpath(xpath_str, first=True).text
    #print("时间：" + page_time)

    xpath_str = "//*[@id=\"article-" + self_number + "\"]"
    title = r.html.xpath(xpath_str, first=True).text
    #title = convert(title, 'zh-hans')
    title = opencc_t2s(title)
    #print("标题：" + title)

    xpath_str = "//*[@id=\"article-content-inner\"]"
    content = r.html.xpath(xpath_str, first=True).text

    format_text = "\n标题：" + title + "\n时间：" + page_time + '\n' + content

    common_list = get_common(url)
    format_text += "\n****** 注释 ******\n"
    for common in common_list:
        format_text += common

    #format_text = convert(format_text, 'zh-hans')
    format_text = opencc_t2s(format_text)
    page_dict[title] = format_text
    # print(page_dict)
    #write_file(format_text)
    return page_dict

def get_page_text():
    text = ""
    return text;
def get_page_bible():
    bible = ""
    return bible

get_host_content()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
