# -*- coding: utf-8 -*-


__author__ = 'frank'


"""适用于beautifulsoup4
爬取douban.com相关页面提取work数据
beautifulsoup3的getText()直接去除标签内部字符串首位的空白符
beautifulsoup4的get_text()保留标签内部字符串首位的空白符

例：爬取电影的desc

"""
import os
import sys
import datetime
from urllib import urlretrieve, urlopen
import logging

from bs4 import BeautifulSoup

from spider_config import *
from python_mysql import *

LOG_PATH = '/var/log/sharefun/spider'
logging.basicConfig(filename=os.path.join(LOG_PATH, 'log.out'), filemode='a',
                    format='%(asctime)s,%(name)s %(levelname)5s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)


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


def crawlMovieInfo(cate_name, title, director, author, genre, score, desc, url, cover_url, cover_path, WEBPAGES_PATH, COVERS_FOLDER_PATH):
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
        except Exception, e:
            logging.debug('搜索' + title + '失败: ' + search_url)
            logging.exception(e)
            raise ConnectionException('搜索' + title + '失败: ' + search_url)
    else:
        works_page = urlopen(work_search_page_path).read()

    soup = BeautifulSoup(works_page)
    tables = soup.find_all('table')
    if len(tables) == 1:                # 系统第一个自带table与搜索结果无关
        os.remove(work_search_page_path)
        logging.debug('搜索 ' + title + ' 结果为空')
        raise EmptyResultException('搜索 ' + title + ' 结果为空')
    # 检查搜索结果是否为目的影片
    # 此处检查可能有bug，因为搜索牯岭街少年杀人事件时该页面乱码，但是进一步搜索时页面正常
    # if title != tables[1].find("a", "nbg").get("title").encode('utf-8'):
    #     raise EmptyResultException('搜索列表中不包含 ' + title)

    url = tables[1].find("a", "nbg").get("href")
    if tables[1].find("span", "rating_nums"):
        score = float(tables[1].find("span", "rating_nums").get_text())

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
        except Exception, e:
            logging.debug('打开' + title + '主页面失败: ' + url)
            logging.exception(e)
            raise ConnectionException('打开' + title + '主页面失败: ' + url)
    else:
        work_page = urlopen(work_home_page_path).read()

    # 检查搜索结果是否为目的影片
    # works_page出现乱码 或者 查询关键字不准确
    if not title in work_page:
        os.remove(work_search_page_path)
        os.remove(work_home_page_path)
        logging.info('搜索结果不包含 ' + title)
        raise EmptyResultException('搜索结果不包含 ' + title)

    # 清除占用空间
    os.remove(work_search_page_path)
    os.remove(work_home_page_path)

    # .replace('<br />', 'newline')和.replace('newline', '<br/>')
    # 是为了解决.get_text()只能拿到标签中间的文本直接跳过<br/>的问题
    soup = BeautifulSoup(work_page.replace('<br />', 'newline'))
    if soup.find("a", rel="v:directedBy"):
        director = soup.find(
            "a", rel="v:directedBy").get_text().encode('utf-8')
    if soup.find_all("span", property="v:genre"):
        vgenres = soup.find_all("span", property="v:genre")
        for vgenre in vgenres:
            genre += vgenre.get_text().encode('utf-8') + '/'
        genre = genre.rstrip('/')

    if soup.find("span", "all hidden"):
        desc = soup.find("span", "all hidden").get_text().replace('newline', '<br/>').encode(
            'utf-8')
    else:
        desc = soup.find(
            "span", property="v:summary").get_text().replace('newline', '<br/>').encode('utf-8')

    url_t = url.rstrip('/')
    work_id = url_t[url_t.rindex('/') + 1:]     # work douban_id
    # 换中图（lpst大图，ipst小图）
    cover_url = tables[1].find('img').get("src").replace("ipst", "lpst")
    cover_path = os.path.join(
        COVERS_FOLDER_PATH, CATENAME_CHIN_TO_ENG[cate_name] + '_' + work_id + '.jpg')
    if not os.path.exists(cover_path):      # 不存在cover时下载cover
        if not downloadPic(cover_url, cover_path):
            logging.info('下载' + title + '封面失败')
            raise ConnectionException('下载' + title + '封面失败')

    # return "\n".join([title, director, author, genre, str(score), desc, url,
    # cover_url, cover_path])
    # 将图片写进,../../static/covers/X.jpg, 但保存路径时只保存covers/X.jpg, url_for('static'. cover_path)
    return title, director, author, genre, score, desc, url, cover_url, cover_path[cover_path.find('static/') + 7:]


def getWorkinfo(cate_name, work_title, WEBPAGES_PATH, COVERS_FOLDER_PATH):
    """根据作品名称解析douban对应页面获取作品详细信息, 下载封面
        eg:("电影", "星际穿越")，('图书', '小王子')
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
        return crawlMovieInfo(cate_name, title, director, author, genre, score, desc, url, cover_url, cover_path, WEBPAGES_PATH, COVERS_FOLDER_PATH)


def main(NAMES_PATH, SUCCESSFUL_NAMES_PATH, FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH):
    """抓取NAMES中的作品信息，并分类存放"""
    names = open(NAMES_PATH, 'r')  # w+是先清空文件内容再操作
    success = open(SUCCESSFUL_NAMES_PATH, 'a+')
    failure = open(FAILED_NAMES_PATH, 'a+')

    for catename_worktitle in names.readlines():
        cate_name = catename_worktitle.strip('\n').split(':')[0]
        work_title = catename_worktitle.strip('\n').split(':')[1]
        conn = Connection(dbHOST, dbNAME, dbUSER, dbPASSWORD)
        print '-' * 40
        logging.info('-' * 40)
        try:
            title, director, author, genre, score, desc, url, cover_url, cover_path = getWorkinfo(cate_name, work_title, WEBPAGES_PATH, COVERS_FOLDER_PATH)
            q = "select * from " + dbWORKSNAME + \
                " where title = %s and cate_id = %s"        # 此处只有where从句中的变量能用%s
            qparas = [title, CATENAME_TO_CATEID[cate_name]]
            if not conn.query(q, *qparas):
                wid = conn.insert(dbWORKSNAME, title=title, director=director, author=author, genre=genre, score=score, desc=desc, url=url, cover_url=cover_url, cover_path=cover_path, cate_id=CATENAME_TO_CATEID[cate_name], created=datetime.datetime.utcnow())
                u = "update " + dbRECOMMSNAME + \
                    " set status_id = 3, work_id = %s where status_id = 2 and cate_id = %s and name = %s "
                uparas = [wid, CATENAME_TO_CATEID[cate_name], work_title]
                conn.execute(u, *uparas)
                conn.commit()
                # 读取文件内容查看该类别作品是否已经被成功抓取
                success.seek(0)
                if cate_name + ':' + work_title not in success.read():
                    success.write(
                        'UTC+8 ' + str(datetime.datetime.now()) + ':' + cate_name + ':' + work_title + '\n')
                success.seek(2)
                print cate_name + ' ' + title + ' 信息成功写入数据库'
                logging.info(cate_name + ' ' + title + ' 信息成功写入数据库')
            else:
                print cate_name + ' ' + title + ' 信息在数据库已经存在'
                logging.info(cate_name + ' ' + title + ' 信息在数据库已经存在')
        except Exception, e:
            # 读取文件内容查看该类别作品是否已经抓取失败并记录
            failure.seek(0)
            if cate_name + ':' + work_title not in failure.read():
                failure.write('UTC+8 ' + str(datetime.datetime.now()) + ':' + cate_name + ':' + work_title + '\n')
            failure.seek(2)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print exc_type, fname, exc_tb.tb_lineno
            print e
            logging.exception(e)
        finally:
            conn.close()
    names.close()
    success.close()
    failure.close()
    open(NAMES_PATH, 'w').close()  # 清空文件内容准备下次写入


if __name__ == '__main__':
    main(NAMES_PATH, SUCCESSFUL_NAMES_PATH, FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH)
