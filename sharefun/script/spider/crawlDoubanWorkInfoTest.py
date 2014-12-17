# -*- coding: utf-8 -*-

__author__ = 'frank'

"""Unit Test Cases for crawller"""

import unittest
from crawlDoubanWorkInfo import *
from spider_config import *
from bs4 import BeautifulSoup
import os


class crawllerTest(unittest.TestCase):

    def testDownloadPic(self):
        url = 'http://img3.douban.com/view/movie_poster_cover/lpst/public/p1798867092.jpg'
        self.assertTrue(
            downloadPic(url,  os.path.join('.', url[url.rfind('/') + 1:])))
        os.remove(os.path.join('.', url[url.rfind('/') + 1:]))

    def testOutputNewLine(self):
        text = """ <div class="indent" id="link-report">

                        <span property="v:summary" class="">
                                　　藤本幸世（森山未来 饰），男，31岁，典型的死宅型二次处男。为了忘却一年前那如梦如幻的桃花期，他来到某娱乐网站求职，却被一名痴情墨田（リリー・フランキー 饰）的女子刺伤。借着对桃花期强大的执念，幸世奇迹般地死而复生，并成功在该网站任职。在上司墨田和前辈唐木素子（真木よう 子 饰）的呵斥下，他每天疲于奔命地采访，在此期间意外邂逅了美丽的女孩美由纪（長澤まさみ 饰）。幸世的桃花期如约而至，但是烦恼也纷至沓来……
                                    <br />
                                　　本片根据久保ミツロウ的同名漫画原著改编，并荣获2011年电影旬报十佳影片第7名。
                        </span>
            </div>"""

        soup = BeautifulSoup(text)
        self.assertNotIn('<br/>', soup.find("span", property="v:summary"))

        soup = BeautifulSoup(text.replace('<br />', 'newline'))
        self.assertIn(
            '<br/>', soup.find("span", property="v:summary").get_text().replace('newline', '<br/>').encode('utf-8'))

    def testEmptyResultException(self):

        title = 'agafdgdsagf'
        """测试搜索结果为空"""
        with self.assertRaises(EmptyResultException):
            crawlMovieInfo('电影', title, '', '', '', '', '', '', '', '', '', '')

        title = '春风沉醉的夜晚'
        """测试搜索结果不包含"""
        with self.assertRaises(EmptyResultException):
            crawlMovieInfo('电影', title, '', '', '', '', '', '', '', '', '', '')

    def testOutput(self):
        text = """ <div class="indent" id="link-report">

                        <span property="v:summary" class="">
                                　　藤本幸世（森山未来 饰），男，31岁，典型的死宅型二次处男。为了忘却一年前那如梦如幻的桃花期，他来到某娱乐网站求职，却被一名痴情墨田（リリー・フランキー 饰）的女子刺伤。借着对桃花期强大的执念，幸世奇迹般地死而复生，并成功在该网站任职。在上司墨田和前辈唐木素子（真木よう 子 饰）的呵斥下，他每天疲于奔命地采访，在此期间意外邂逅了美丽的女孩美由纪（長澤まさみ 饰）。幸世的桃花期如约而至，但是烦恼也纷至沓来……
                                    <br />
                                　　本片根据久保ミツロウ的同名漫画原著改编，并荣获2011年电影旬报十佳影片第7名。
                        </span>
            </div>"""
        soup = BeautifulSoup(text)
        print soup.find("span", property="v:summary").get_text().encode('utf-8')

    def test_python_mysql_query(self):
        conn = Connection(dbHOST, dbNAME, dbUSER, dbPASSWORD)
        q = "select * from " + dbWORKSNAME + \
            " where title = %s and cate_id = %s"
        cate_name = '电影'
        title = '空房间'
        qparas = [title, CATENAME_TO_CATEID[cate_name]]
        self.assertTrue(conn.query(q, *qparas))

    def test_python_mysql_insert(self):
        conn = Connection(dbHOST, dbNAME, dbUSER, dbPASSWORD)
        print 'id is',conn.insert("roles", name='Test', default=0, permissions=0)
        q = "DELETE FROM `roles` WHERE permissions = 0"
        print conn.execute(q)
        conn.commit()

    def test_readfromfile_and_writeintofile(self):

        names = open(NAMES_PATH, 'r')  # w+是先清空文件内容再操作
        for catename_worktitle in names.readlines():
            cate_name = catename_worktitle.strip('\n').split(':')[0]
            work_title = catename_worktitle.strip('\n').split(':')[1]
            print type(work_title)
            print isinstance(work_title, unicode)
            print cate_name, work_title
            print work_title.decode('utf-8')
            work_search_page_path = os.path.join(
                WEBPAGES_PATH,  CATENAME_CHIN_TO_ENG[cate_name] + '_' + work_title + '_search_page.html')
            print work_search_page_path


if __name__ == '__main__':
    unittest.main()
