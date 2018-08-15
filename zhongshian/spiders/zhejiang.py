# -*- coding: utf-8 -*-
import re
import json
import time
import scrapy
import pymysql
from scrapy import Request
from scrapy import FormRequest
from datetime import datetime
from dateutil import parser
from scrapy.utils.project import get_project_settings


class ZhejiangSpider(scrapy.Spider):
    name = 'zhejiang'
    allowed_domains = ['xyxx.zjfda.gov.cn']
    start_urls = ['http://xyxx.zjfda.gov.cn/ajax/ajax!new_xy_index.do?queryBean.pn=1&queryBean.pageSize=20&orgId=33000000&queryBean.areaId=33000000&category=cjxx_sp']

    def parse(self, response):
        current_page = self.get_page(response.url)
        start_path = '//table[contains(@cellpadding, "2")]//a/@href'
        link_urls = response.xpath(start_path).extract()
        while current_page > 6:
            break
        else:
            i = 0
            while i < len(link_urls):
                for link_url in link_urls:
                    id = self.get_parameter(link_url)[0]
                    newsType = self.get_parameter(link_url)[1]
                    url = 'http://xyxx.zjfda.gov.cn' + link_url
                    request = Request(url, callback=self.parse_link, meta={'id': id, 'newsType': newsType})
                    yield request
                    i += 1
            else:
                next_page = current_page + 1
                next_url = 'http://xyxx.zjfda.gov.cn/ajax/ajax!new_xy_index.do?queryBean.pn=%s&queryBean.pageSize=20&orgId=33000000&queryBean.areaId=33000000&category=cjxx_sp'
                request = Request(next_url % str(next_page), callback=self.parse)
                yield request


    def parse_link(self, response):
        id = response.meta['id']
        newsType = response.meta['newsType']
        url = 'http://xyxx.zjfda.gov.cn/ajax/ajax!detail_cjbhg_sp.do'
        post_request = FormRequest(url=url, formdata={'queryBean.id': '%s' % id, 'queryBean.newsType': '%s' % newsType}, callback=self.parse_page)
        yield post_request

    def parse_page(self, response):
        try:
            resp = json.loads(response.text, encoding='gbk')[0]
            listEnty = resp['listEnty']
            if listEnty:
                for dt in listEnty:
                    item = {}
                    item['stampDateTime'] = datetime.now()
                    item['commodityName'] = dt['commodityName']
                    item['corpNameBy'] = dt['corpNameBy']
                    item['addressBy'] = dt['addressBy']
                    item['addressByRegionId'] = self.zoning(dt['addressBy'])
                    item['corpName'] = dt['corpName']
                    item['address'] = dt['address']
                    item['addressRegionId'] = self.zoning(dt['address'])
                    item['createDate'] = dt['createDate']
                    item['fl'] = dt['fl']
                    item['flId'] = self.category(dt['fl'])
                    if '浙江/(省抽)' in dt['ggh']:
                        item['ggh'] = dt['ggrq']
                        item['ggrq'] = self.str_times(dt['rwly'])
                        item['rwly'] = dt['ggh']
                        item['rwly_id'] = self.rwly_standic(dt['ggh'])
                    else:
                        item['ggh'] = dt['ggh']
                        item['ggrq'] = self.str_times(dt['ggrq'])
                        item['rwly'] = dt['rwly']
                        item['rwly_id'] = self.rwly_standic(dt['rwly'])
                    item['id'] = dt['id']
                    if 'inspectionUnit' in dt:
                        item['inspectionUnit'] = dt['inspectionUnit']
                    else:
                        item['inspectionUnit'] = '/'
                    item['model'] = dt['model']
                    item['newsDetailType'] = int(dt['newsDetailType'])
                    item['newsDetailTypeId'] = self.news_detail(int(dt['newsDetailType']))
                    item['note'] = dt['note']
                    item['productionDate'] = self.str_time(dt['productionDate'])
                    item['sampleOrderNumber'] = dt['sampleOrderNumber']
                    item['status'] = int(dt['status'])
                    item['statusEnumValue'] = dt['statusEnumValue']
                    if 'trademark' in dt:
                        item['trademark'] = dt['trademark']
                    else:
                        item['trademark'] = '/'
                    item['transId'] = dt['transId']
                    if 'unqualifiedItem' not in dt:
                        item['unqualifiedItem'] = '/'
                        item['checkResult'] = '/'
                        item['standardValue'] = '/'
                    elif 'unqualifiedItem' in dt and '║' in dt['unqualifiedItem']:
                        ls = self.split_unqualify(dt['unqualifiedItem'])
                        item['unqualifiedItem'] = self.clean_n(ls[0])
                        item['checkResult'] = self.clean_n(ls[1])
                        item['standardValue'] = self.clean_n(ls[2])
                    else:
                        item['unqualifiedItem'] = dt['unqualifiedItem']
                        item['checkResult'] = self.clean_n(dt['checkResult'])
                        item['standardValue'] = self.clean_n(dt['standardValue'])
                    if 'approvalNumber' in dt:
                        item['approvalNumber'] = dt['approvalNumber']
                    else:
                        item['approvalNumber'] = '/'
                    if 'batchNumber' in dt:
                        item['batchNumber'] = dt['batchNumber']
                        yield item
                    else:
                        item['batchNumber'] = '/'
                        yield item
        except KeyError:
            pass

    @staticmethod
    def get_page(url):
        ls = re.match(".*pn=(\d+)", url)
        str = ls.group(1)
        return int(str)

    @staticmethod
    def get_parameter(url):
        id_ls = re.findall(".*id=(\w+)", url)
        type_ls = re.findall(".*type=(\d+)", url)
        id = id_ls[0]
        newsType = type_ls[0]
        return id, newsType

    @staticmethod
    def split_unqualify(str):
        ls = str.split('║')
        return ls

    @staticmethod
    def clean_n(str):
        if '\n' in str:
            return str.strip('\n')
        else:
            return str

    @staticmethod
    def str_time(str):
        return parser.parse(str)

    @staticmethod
    def str_times(str):
        stp = time.strptime(str, '%Y.%m.%d')
        return time.strftime("%Y-%m-%d", stp)

    @staticmethod
    def zoning(str):
        settings = get_project_settings()
        link = pymysql.connect(settings['MYSQL_HOST'], settings['MYSQL_USER'], settings['MYSQL_PASSWORD'], settings['MYSQL_DB'])
        link.set_charset('utf8')
        cursor = link.cursor()
        sql1 = "select region_name from region r where r.parent_id in (select r.region_id from region r where r.parent_id=(select r.region_id from region r where r.region_name='浙江省'))"
        cursor.execute(sql1)
        allData1 = cursor.fetchall()
        sql2 = "select region_name from region r where r.parent_id=(select r.region_id from region r where r.region_name='浙江省')"
        cursor.execute(sql2)
        allData2 = cursor.fetchall()
        i = 0
        stp = []
        while i < len(allData1):
            j = 0
            while j < len(allData1[i]):
                if allData1[i][j][:-1] in str:
                    stp.append(allData1[i][j])
                    sql3 = "select region_id from region r where r.region_name='%s'" % stp[0]
                    cursor.execute(sql3)
                    allData3 = cursor.fetchall()
                    region_id = int(allData3[0][0])
                    return region_id
                    break
                else:
                    j += 1
            i += 1
        if not stp:
            m = 0
            while m < len(allData2):
                n = 0
                while n < len(allData2[m]):
                    if allData2[m][n][:-1] in str:
                        stp.append(allData2[m][n])
                        sql4 = "select region_id from region r where r.region_name='%s'" % stp[0]
                        cursor.execute(sql4)
                        allData4 = cursor.fetchall()
                        region_id = int(allData4[0][0])
                        return region_id
                        break
                    else:
                        n += 1
                m += 1
        if not stp and "浙江" in str:
            return 12
        elif not stp and "浙江" not in str:
            return 1

    @staticmethod
    def rwly_standic(str):
        if '省抽' in str:
            return 521
        elif '国抽' in str:
            return 520
        else:
            return 524
        
    @staticmethod
    def news_detail(i):
        if i >= 54 and i <= 76 or i == 100:
            return 1
        elif i >= 77 and i <= 99 or i == 101:
            return 2

    @staticmethod
    def category(str):
        settings = get_project_settings()
        link = pymysql.connect(settings['MYSQL_HOST'], settings['MYSQL_USER'], settings['MYSQL_PASSWORD'],
                               settings['MYSQL_DB'])
        link.set_charset('utf8')
        cursor = link.cursor()
        sql = "select sys_data_group_id from sys_data_item where key_value='%s'" % str
        cursor.execute(sql)
        allData = cursor.fetchall()
        return allData[0][0]
