# coding=utf-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import time
import random
import pickle
import opencc
import urllib3
import requests
import threading
from ebooklib import epub
from random import randint
from threading import Thread
from requests_html import HTML
from requests_html import HTMLSession

urllib3.disable_warnings()

ROOT_URL = "https://mickey1124.pixnet.net/"
PROXIES = {"https": "http://127.0.0.1:1082"}
TOTAL_PAGE_NUMBER = 0
TOTAL_PAGE_NUMBER_ERROR = 0
GLOBAL_DICT = {}

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

def create_txt():
    if os.path.exists("all.object"):
        f = open("all.object", 'rb')
        category_dict = pickle.load(f)
    else:
        global  GLOBAL_DICT
        category_dict = GLOBAL_DICT

    str_file = ""
    for category in category_dict:
        str_file += "\n@@@@@@ " + category + " @@@@@@\n"
        for title in category_dict[category]:
            str_file += "\n&&&&&& " + title + " &&&&&&\n"
            str_file += category_dict[category][title]

        #str_file2 = "<br />".join(str_file2.split("\n"))
        #file_n = opencc_t2s(category)
        #write_file3(file_n + ".txt", str_file2)

    # file_name = "all.html"
    # #os.remove(file_name)
    # str_file = "<br />".join(str_file.split("\n"))
    # fo = open(file_name, "w", encoding="utf-8")
    # fo.write(str_file)
    # fo.close()

    file_name = "all.txt"
    write_file3(file_name, str_file)

    get_bible_list(str_file)

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
        print("(" + str(wait_time) + ")即将下载链接(" + category + ")[" + str(i) + "]线程号[" + str(pthread_num) + "]：" + link)
        page_dict = get_page(link)
        for title in page_dict:
            file_str += "\n&&&&&& " + title + " &&&&&&\n"
            file_str += "\n" + page_dict[title] + "\n"
            page_dicts.update(page_dict)

        lock.acquire()
        write_file(file_str)
        lock.release()

        write_file2(category, file_str)

    category_dict[category] = page_dicts
    global GLOBAL_DICT
    GLOBAL_DICT.update(category_dict)

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

    # save all object
    global GLOBAL_DICT
    f = open('all.object', 'wb')
    pickle.dump(GLOBAL_DICT, f)

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
        common_info = "\n作者：" + common_author + "\n时间：" + common_time + "\n" + common_text + "\n"
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

def write_file2(f, s):
    fo = open(f + ".txt", "a", encoding="utf-8")
    fo.write(s)
    fo.close()
    return

def write_file3(f, s):
    fo = open(f, "a", encoding="utf-8")
    fo.write(s)
    fo.close()
    return

def write_error(s):
    fo = open("err.txt", "a", encoding="utf-8")
    fo.write(s + "\n")
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
    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]

    random_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
    headers = {
        'User-Agent': random_agent,
    }

    while True:
        try:
            session = HTMLSession()
            global PROXIES
            r = session.get(url, proxies=PROXIES, headers=headers, verify=False, timeout=12)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            print(e)
            r = None
            break

        finally:
            break

    return r

def get_link_exceptions_try(url):
    i = 1
    r = get_link_exceptions(url)

    while (i < 4) and (r is None):
        i = i + 1
        time.sleep(3)
        r = get_link_exceptions(url)

    if r is None:
        write_error(url)
        global TOTAL_PAGE_NUMBER_ERROR
        TOTAL_PAGE_NUMBER_ERROR = TOTAL_PAGE_NUMBER_ERROR + 1
        print("失败下载页面个数:" + str(TOTAL_PAGE_NUMBER_ERROR))
        return None
    else:
        global TOTAL_PAGE_NUMBER
        TOTAL_PAGE_NUMBER = TOTAL_PAGE_NUMBER + 1
        print("成功下载页面个数：[" + str(TOTAL_PAGE_NUMBER) + "]失败下载页面个数:[" + str(TOTAL_PAGE_NUMBER_ERROR) + "]")
        return r

def get_common(url):
    url = url + "/comments"
    common_list = []
    r = get_link_exceptions_try(url)

    if r is None:
        return common_list

    '''
    while (i < 4) and (r is None):
        if r.text.strip() == "":
            i = i + 1
            time.sleep(3)
            r = get_link_exceptions(url)
        else:
            break    
    proxies = {"https": "http://127.0.0.1:1082"}
    session = HTMLSession()
    r = session.get(url, proxies=proxies, verify=False)
    '''
    r_dict = r.json()

    common_list = get_common_content(r_dict['list'])
    return common_list

def get_page(url):
    page_dict = {}
    r = get_link_exceptions_try(url)

    if r is None:
        return page_dict
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
    format_text += "\n\n****** 注释 ******\n\n"
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


def get_bibles():
    str = '''讲出『洁净的』、的动物了。『耶母』（创7：1-2）没错出『耶母111』『耶母2222』（创7：1-2）『洁净的』'''


    r = get_bible_list(str)
    #while r != -1:
    #    = get_one(str[r:], 0)

def get_paper_list():
    paper_list = ["创","出", "利", "民","申", "书", "士", "得", "撒上","撒下","王上","王下", "代上", "代下", "拉", "尼",
"斯",
"伯",
"诗",
"箴",
"传",
"歌",
"赛",
"耶",
"哀",
"结",
"但",
"何",
"珥",
"摩",
"俄",
"拿",
"弥",
"鸿",
"哈",
"番",
"该",
"亚",
"玛",
"太",
"可",
"路",
"约",
"徒",
"罗",
"林前",
"林后",
"加",
"弗",
"腓",
"西",
"帖前",
"帖后",
"提前",
"提后",
"多",
"门",
"来",
"雅",
"彼前",
"彼后",
"约壹",
"约贰",
"约叁",
"犹",
"启"]
    return paper_list

def get_bible_list(str):
    out = ""
    ret = 0
    start = 0
    l = len(str)
    bible_list = []
    paper_list = get_paper_list()

    while start < l:
        out = ""
        point1 = str.find("『", start)
        ret = point1
        if (point1 != -1):
            start = point1
            point2 = str.find("』", point1)
            ret = point2
            if point2 != -1:
                start = point2
                # find 『 and 』
                point3 = str.find("（", point2, point2 + 8)
                ret = point3
                if point3 != -1:
                    start = point3
                    point4 = str.find("）", point3, point3 + 8)
                    ret = point4
                    if point4 != -1:
                        start = point3
                        # find （ and ）
                        out = str[point1: point4 + 1]
                        out = out.replace("\n", "")
                        bible = str[point3:point4]
                        find = 0
                        for p in paper_list:
                            op = bible.find(p)
                            if op != -1:
                                find = 1
                                break
                        fl = bible.find("：")
                        if fl == -1:
                            find = 0
                        if find == 1:
                            out = out.replace("（", "\t（")
                            bible_list.append(out)
                            print(out)

        else:
            start = l

    l2 = []
    for i in bible_list:
        if not i in l2:
            l2.append(i)

    file_name = "bible.txt"
    f = ""
    for s in l2:
        f += s + "\n"

    write_file3(file_name, f)
    return ret

#get_host_content()
create_txt()
#get_bibles()
#get_test()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
