#!/usr/bin/env python3
#-*- coding: utf-8 -*-


__author__ = 'Hem1ng'


import os
from ..items import *
from scrapy import Request
from bs4 import BeautifulSoup
from scrapy.spiders import Rule,CrawlSpider, Spider
from scrapy.linkextractors import LinkExtractor

class NewsSpider(Spider):

    name = 'ITNews'
    allowed_domains = ['ithome.com']
    start_urls = ['https://www.ithome.com/blog/']

    def parse(self, response):
        # *********** 使用xpath解析 **************
        sel = scrapy.Selector(response)
        # xpath返回的是一个列表
        news_imgUrl    = sel.xpath('//a[@class="list_thumbnail"]/img/@src').extract()
        news_title     = sel.xpath('//div[@class="block"]/h2/a/text()|//div[@class="block"]/h2/a/font/text()').extract()
        news_time      = sel.xpath('//div[@class="block"]/h2/span/text()').extract()
        news_brief     = sel.xpath('//div[@class="memo"]/p/text()').extract()
        news_detailUrl = sel.xpath('//a[@class="list_thumbnail"]/@href').extract()

        # *********** 使用bs解析 *****************
        # soup = BeautifulSoup(response.text, 'lxml')
        # news_imgUrl    = [a.find('img')['src'] for a in soup.find_all('a',class_='list_thumbnail')]
        # news_detailUrl = [a['href'] for a in soup.find_all('a', class_='list_thumbnail')]
        # news_title     = [div.find('h2').find('a').string for div in soup.find_all('div', class_='block')]
        # news_time      = [div.find('h2').find('span').string for div in soup.find_all('div', class_='block')]
        # news_brief     = [div.find('p').string for div in soup.find_all('div', class_='memo')]

        for i in range(len(news_imgUrl)):
            print(i)
            item = NewsItem()
            item['imgUrl']    = 'https:'+news_imgUrl[i]
            item['title']     = news_title[i]
            item['time']      = news_time[i]
            item['brief']     = news_brief[i]
            item['detailUrl'] = news_detailUrl[i]
            yield item

class BZImageSpider(Spider):

    name = 'BZImage'
    allowed_domains = ['zol.com.cn']
    start_urls = ['http://desk.zol.com.cn/youxi/yingxionglianmeng/',
                  'http://desk.zol.com.cn/youxi/yingxionglianmeng/2.html']

    def parse(self, response):
        sel = scrapy.Selector(response)
        url_host = 'http://desk.zol.com.cn'
        page_urls = sel.xpath('//li[@class="photo-list-padding"]/a/@href').extract()
        for url in page_urls:
            yield Request(url_host+url,callback=self.get_downloadLinkOfImage)

    def get_downloadLinkOfImage(self, response):
        sel = scrapy.Selector(response)
        image_url = sel.xpath('//img[@id="bigImg"]/@src').extract()
        item = ImageItem()
        item['imageUrl'] = image_url[0]
        yield item
        next_url = sel.xpath('//a[@id="pageNext"]/@href').extract()
        url_host = 'http://desk.zol.com.cn'
        if next_url[0] != 'javascript:;':
            yield Request(url_host+next_url[0], callback=self.get_downloadLinkOfImage)

class ImageSpider(CrawlSpider):

    name = 'Image'
    download_delay = 1
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/photos/photo/2509468063/#title-anchor']
    rules = (Rule(LinkExtractor(allow=(r'https://movie\.douban\.com/photos/photo/(\d+)/#title-anchor',),), callback='parse_next',follow=True),)

    # 批量爬取网页时使用CrawlSpider,此时CrawlSpider已经重写了parse方法，所以重新写一个解析方法parse_next，不要与单页面爬取时混淆
    # 程序自动使用start_urls构造Request并发送请求，然后调用parse函数对其进行解析，在这个解析过程中使用rules中的规则从html（或xml）文本中提取匹配的链接，
    # 通过这个链接再次生成Request，如此不断循环，直到返回的文本中再也没有匹配的链接，或调度器中的Request对象用尽，程序才停止。
    # rules中的规则如果callback没有指定，则使用默认的parse函数进行解析，如果指定了，那么使用自定义的解析函数。
    # 如果起始的url解析方式有所不同，那么可以重写CrawlSpider中的另一个函数parse_start_url(self, response)
    # 用来解析第一个url返回的Response，但这不是必须的。
    # Rule对象的follow参数的作用是：指定了根据该规则从response提取的链接是否需要跟进
    def parse_next(self, response):
        sel = scrapy.Selector(response)
        image_url = sel.xpath('//div[@class="photo-wp"]/a[@class="mainphoto"]/img/@src').extract()
        if len(image_url):
            for url in image_url:
                item = ImageItem()
                item['imageUrl'] = url
                yield item

class HImageSpider(CrawlSpider):

    name = 'HImage'
    allowed_domains = ['42soso.com', '71kvkv.com']
    start_urls = ['http://www.42soso.com/tu/1.html']
    rules = (
                Rule(LinkExtractor(allow=(r'/news/class/\d+.html',),), callback='parse_next',follow=True),
                Rule(LinkExtractor(allow=(r'/news/other/10_\d+.html',),), callback='parse_next', follow=True),
            )

    def parse_next(self, response):
        sel = scrapy.Selector(response)
        image_urls = sel.xpath('//img/@src').extract()
        for url in image_urls:
            item = ImageItem()
            item['imageUrl'] = url
            yield item

class VideoSpider(CrawlSpider):

    name = 'Video'
    start_urls = ['http://www.42soso.com/diao/se57.html']
    # 如果多个rule匹配了相同的链接，则根据他们在本属性中被定义的顺序，第一个会被使用。
    rules = (
                Rule(LinkExtractor(allow=(r'/video/\w+',),), callback='parse_item', follow=True),
                Rule(LinkExtractor(allow=(r'/diao/se57_\d+.html',),), callback='parse_item', follow=True)
             )

    def parse_item(self, response):
        sel = scrapy.Selector(response)
        video_url = sel.xpath('//video[@id="video-js-id"]/source/@src').extract()
        print(video_url)
        if len(video_url):
            for url in video_url:
                item = VideoItem()
                item['videoUrl'] = url
                yield item

class YSDSpider(Spider):

    name = 'YSD'
    allowed_domains = ['yishoudan.com']
    # 获得全部商品的url，json=1返回json格式，version=2返回记录总数
    start_urls = ['http://www.yishoudan.com/all/index/pname/page/aname/page/p/1.html']

    def parse(self, response):
        sel = scrapy.Selector(response)
        all_page = sel.xpath('//div[@class="paging"]/a[@class="selectp"]/@p').extract()
        for i in range(max(map(int, all_page))):
            url = 'http://www.yishoudan.com/all/index/pname/page/aname/page/p/%s?json=1&version=2' % (i+1)
            yield Request(url, callback=self.parse_data)

    def parse_data(self, response):
        a = response.text
        if 'null' in response.text:
            a = a.replace('null', '"null"')
        # eval()或者exec()是将字符串转换成dict
        data = eval(a)
        item = YSDItem()
        item['goods'] = data['items']
        yield item

class NewVideoSpider(Spider):

    name = 'NewVideoSpider'
    allowed_domains = ['27ckck.com']
    start_urls = ['https://www.27ckck.com/html/vodlist/tp/4.html']

    def __init__(self):
        Spider.__init__(self)
        self.__video_links__ = []
        self.__video_count__ = None

    def parse(self, response):
        global video_links
        sel = scrapy.Selector(response)
        all_urls = sel.xpath('//div[@class="indexvod"]/ul/li/h3/a/@href').extract()
        all_titles = sel.xpath('//div[@class="indexvod"]/ul/li/h3/a/@title').extract()
        for i in range(len(all_urls)):
            item = VideoItem()
            item['videoUrl'] = 'https://www.27ckck.com'+all_urls[i]
            item['videoTitle'] = all_titles[i]
            self.save_toList(item)
        all_page = sel.xpath('//div[@class="left"]/strong/text()').extract()
        total_page = int(all_page[2])
        self.__video_count__ = int(all_page[0])
        for i in range(total_page):
            if i == 0:
                continue
            url = 'https://www.27ckck.com/html/vodlist/tp/4_%s.json' % (i+1)
            yield Request(url, callback=self.parse_data)

    def parse_data(self, response):
        resp = eval(response.text)
        all_item = resp['list']
        for i in range(len(all_item)):
            dic = all_item[i]
            item = VideoItem()
            item['videoUrl'] = 'https://www.27ckck.com' + dic['playurl'].replace("\\",'')
            item['videoTitle'] = dic['s_name']
            self.save_toList(item)
            if len(self.__video_links__) == self.__video_count__:
                self.save_toHtml()

    def save_toList(self, item):
        self.__video_links__.append('<p><a href="%s&j=1&hd=1" target="_blank">%s</a></p>' % (item['videoUrl'], item['videoTitle']))

    def save_toHtml(self):
        print('开始写入文件...')
        data = '<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<meta charset="UTF-8">\n\t<title>Videos</title>\n</head>\n<body>\n\t' + '\n\t'.join(
                self.__video_links__) + '\n</body>\n</html>'
        # data写入文件如果是文本必须是str,不能是list，dict
        with open(os.path.join(os.path.expanduser(r'~/Downloads'), 'Temp.html'), 'w') as f:
            f.write(data)
        print('写入文件完成...')







