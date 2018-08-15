# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FoodItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stampDateTime = scrapy.Field()    #数据抓取时间
    address = scrapy.Field()    #标称生产企业地址
    addressRegionId = scrapy.Field()    #标称生产企业所属区id
    addressBy = scrapy.Field()    #被抽检单位地址
    addressByRegionId = scrapy.Field()    #被抽检单位地址所属区id
    commodityName = scrapy.Field()    #食品名称
    corpName = scrapy.Field()    #标称生产企业名称
    corpNameBy = scrapy.Field()    #被抽检单位名称
    createDate = scrapy.Field()    #抽检日期
    fl = scrapy.Field()    #分类
    flId = scrapy.Field()    #分类id
    ggh = scrapy.Field()    #公告所属刊次
    ggrq = scrapy.Field()    #公告发布日期
    id = scrapy.Field()
    inspectionUnit = scrapy.Field()    #检验机构
    model = scrapy.Field()    #规格型号
    newsDetailType = scrapy.Field()    #是否合格
    newsDetailTypeId = scrapy.Field()    #是否合格ID（1合适，2不合格）
    note = scrapy.Field()    #备注
    productionDate = scrapy.Field()    #生产日期/批号
    rwly = scrapy.Field()    #抽检级别(省抽/国抽)
    rwly_id = scrapy.Field()    #抽检级别(省抽/国抽/专项)对应id
    sampleOrderNumber = scrapy.Field()    #样品单号
    status = scrapy.Field()
    statusEnumValue = scrapy.Field()
    trademark = scrapy.Field()    #商标
    transId = scrapy.Field()
    unqualifiedItem = scrapy.Field()    #抽检项目
    checkResult = scrapy.Field()    #检查结果
    standardValue = scrapy.Field()    #标准值
    approvalNumber = scrapy.Field()    #许可号
    batchNumber = scrapy.Field()    #批号
