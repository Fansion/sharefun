# -*- coding: utf-8 -*-

__author__ = 'frank'


"""爬取douban.com相关页面提取work数据
适用于beautifulsoup3
改动两点：
1. find_all 改成 findAll
2. get_text 改成 getText
"""

import os
import sys
from urllib import urlretrieve, urlopen
from BeautifulSoup import BeautifulSoup
from spider_config import *
from python_mysql import *
import datetime


class EmptyResultException(Exception):

    """raised for empty result"""
    pass


class ConnectionException(Exception):

    """raised for internet connection error"""
    pass


def downloadPic(url, path):
    urlretrieve(url, path)
    if os.path.exists(path):
        return True
    return False


def crawlMovieInfo(cate_name, title, director, author, genre, score, desc, url, cover_url, cover_path):
    """抓取电影信息"""
    search_url = SEARCH_URL_PATTERN.replace(
        '{cate_name}', CATENAME_CHIN_TO_ENG[cate_name]).replace('{work_title}', title)

    works_page = ''
    work_search_page_path = os.path.join(
        WEBPAGES_PATH,  CATENAME_CHIN_TO_ENG[cate_name] + '_' + title + '_search_page.html')
    # 缓存work search 结果web页面
    if not os.path.exists(work_search_page_path):
        try:
            works_page = urlopen(search_url).read()
            if works_page:
                work_search_page = open(work_search_page_path, 'w')
                work_search_page.write(str(works_page))
                work_search_page.close()
            # print works_page
        except Exception, e:
            raise ConnectionException('搜索' + title + +'失败: ' + search_url)
    else:
        works_page = urlopen(work_search_page_path).read()

    soup = BeautifulSoup(works_page)
    tables = soup.findAll('table')
    if len(tables) == 1:                # 系统第一个自带table与搜索结果无关
        os.remove(work_search_page_path)
        raise EmptyResultException('搜索 ' + title + ' 结果为空')
    # 检查搜索结果是否为目的影片
    # 此处检查可能有bug，因为搜索牯岭街少年杀人事件时该页面乱码，但是进一步搜索时页面正常
    # if title != tables[1].find("a", "nbg").get("title").encode('utf-8'):
    #     raise EmptyResultException('搜索列表中不包含 ' + title)

    url = tables[1].find("a", "nbg").get("href")
    if tables[1].find("span", "rating_nums"):
        score = float(tables[1].find("span", "rating_nums").getText())

    work_page = ''
    work_home_page_path = os.path.join(
        WEBPAGES_PATH, CATENAME_CHIN_TO_ENG[cate_name] + '_' + title + '_page.html')
    # 缓存work web页面
    if not os.path.exists(work_home_page_path):
        try:
            work_page = urlopen(url).read()
            if work_page:
                work_home_page = open(work_home_page_path, 'w')
                work_home_page.write(str(work_page))
                work_home_page.close()
            # print work_page
        except Exception, e:
            raise ConnectionException('打开' + title + '主页面失败: ' + url)
    else:
        work_page = urlopen(work_home_page_path).read()

    # 检查搜索结果是否为目的影片
    # works_page出现乱码 或者 查询关键字不准确
    if not title in work_page:
        os.remove(work_search_page_path)
        os.remove(work_home_page_path)
        raise EmptyResultException('搜索结果不包含 ' + title)

    # .replace('<br />', 'newline')和.replace('newline', '<br/>')
    # 是为了解决.getText()只能拿到标签中间的文本直接跳过<br/>的问题
    soup = BeautifulSoup(work_page.replace('<br />', 'newline'))
    if soup.find("a", rel="v:directedBy"):
        director = soup.find(
            "a", rel="v:directedBy").getText().encode('utf-8')
    if soup.findAll("span", property="v:genre"):
        vgenres = soup.findAll("span", property="v:genre")
        for vgenre in vgenres:
            genre += vgenre.getText().encode('utf-8') + '/'
        genre = genre.rstrip('/')

    if soup.find("span", "all hidden"):
        desc = soup.find("span", "all hidden").getText().replace('newline', '<br/>').encode(
            'utf-8')
    else:
        desc = soup.find(
            "span", property="v:summary").getText().replace('newline', '<br/>').encode('utf-8')

    url_t = url.rstrip('/')
    work_id = url_t[url_t.rindex('/') + 1:]     # work douban_id
    # 换中图（lpst大图，ipst小图）
    cover_url = tables[1].find('img').get("src").replace("ipst", "lpst")
    cover_path = os.path.join(
        COVERS_FOLDER_PATH, CATENAME_CHIN_TO_ENG[cate_name] + '_' + work_id + '.jpg')
    if not os.path.exists(cover_path):      # 不存在cover时下载cover
        if not downloadPic(cover_url, cover_path):
            raise ConnectionException('下载' + title + '封面失败')

    # return "\n".join([title, director, author, genre, str(score), desc, url,
    # cover_url, cover_path])
    # 将图片写进,../../static/covers/X.jpg, 但保存路径时只保存covers/X.jpg
    return title, director, author, genre, score, desc, url, cover_url, cover_path.replace('../../static/', '')


def getWorkInfo(cate_name, work_title):
    """根据作品名称解析douban对应页面获取作品详细信息, 下载封面
        eg:("电影", "星际穿越")
    """
    title = work_title
    director = ''
    author = ''
    genre = ''
    score = 0
    desc = ''
    url = ''
    cover_url = ''
    cover_path = ''
    if cate_name == '电影':
        return crawlMovieInfo(cate_name, title, director, author, genre, score, desc, url, cover_url, cover_path)


def main():
    # uncomment to add work into db from command line
    # if len(sys.argv) < 3:
    #     print 'Usage: python crawlDoubanWorkInfo.py <cate_name> <work_title1> <work_title2> ...'
    #     return
    # cate_name = sys.argv[1]
    # work_titles = sys.argv[2:]

    # uncomment to add work info db by manual input
    cate_name = '电影'
    work_titles = []
    names = open('names', 'r')  # w+是先清空文件内容再操作
    for name in names.readlines():
        work_titles.append(name.strip('\n'))

    success = open('successful-names', 'a+')
    failure = open('failed-names', 'a+')

    for work_title in work_titles:
        conn = Connection(dbHOST, dbNAME, dbUSER, dbPASSWORD)
        print '-' * 40
        try:
            title, director, author, genre, score, desc, url, cover_url, cover_path = getWorkInfo(
                cate_name, work_title)
            q = "select * from " + dbWORKSNAME + \
                " where title = %s and cate_id = %s"
            # 此处只有where从句中的变量能用%s
            qparas = [title, CATENAME_TO_CATEID[cate_name]]
            if not conn.query(q, *qparas):
                conn.insert(dbWORKSNAME, title=title, director=director, author=author, genre=genre, score=score, desc=desc, url=url,cover_url=cover_url, cover_path=cover_path, cate_id=CATENAME_TO_CATEID[cate_name], created=datetime.datetime.utcnow())
                u = "update " + dbRECOMMSNAME + \
                    " set status_id = 3 where status_id = 2 and cate_id = %s and name = %s"
                uparas = [CATENAME_TO_CATEID[cate_name], work_title]
                conn.execute(u, *uparas)
                conn.commit()
                success.seek(0)
                if work_title + '\n' not in success.readlines():
                    success.write(work_title + '\n')
                success.seek(2)
                print cate_name + ' ' + title + ' 信息成功写入数据库'
            else:
                print cate_name + ' ' + title + ' 信息在数据库已经存在'
            # print getWorkInfo('图书', '小王子')
        except Exception, e:
            failure.seek(0)
            if work_title + '\n' not in failure.readlines():
                failure.write(work_title + '\n')
            failure.seek(2)

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print exc_type, fname, exc_tb.tb_lineno
            print e
        finally:
            conn.close()
    names.close()
    open('names', 'w').close()  # 清空内容
    success.close()
    failure.close()
if __name__ == '__main__':
    main()
