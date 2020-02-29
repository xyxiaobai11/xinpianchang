# -*- coding: utf-8 -*-
import json
import random
import string
import scrapy
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from xinpianchang.items import XPCVideoItem, XPCCommentItem, XPCAuthorItem, VideoItem, XPCFansAttenItem
import re
import datetime


# 生成一个新的sessionid
def gen_sessionid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=26))

cookies = {'Authorization': '06D7C40A0222B8F2F0222B486C0222BA6760222BD440E4C2A9AF'}


class XpcSpider(scrapy.Spider):
    name = 'xpc'
    allowed_domains = ['www.xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/page-1']
    video_url = 'https://openapi-vtom.vmovier.com/v3/video/{}?expand=resource&usage=xpc_web'
    comment_url = 'https://app.xinpianchang.com/comments?resource_id={}&type=article&page=1'
    auth_url = 'https://www.xinpianchang.com/u10065201?from=articleList'
    page_count = 0
    def parse(self, response):
        self.page_count += 1
        if self.page_count % 100 == 0:
            cookies.update(PHPSESSID=gen_sessionid())
        data_articleid_list = response.xpath("//ul[@class='video-list']/li/@data-articleid").extract()
        for data_articleid in data_articleid_list:
            url = 'https://www.xinpianchang.com/a{}'.format(data_articleid)
            yield scrapy.Request(url, callback=self.parse_video, meta={'article_id': data_articleid})
            yield scrapy.Request(self.comment_url.format(data_articleid), callback=self.parse_comment, dont_filter=True)

        next_url_list = response.xpath("//div[contains(@class, 'page')]//a/@href").extract()
        for next_url in next_url_list:
            next_full_url = (urljoin(response.url, next_url))
            yield scrapy.Request(next_full_url, callback=self.parse, cookies=cookies)

    def parse_video(self, response):
        # 请求视频真正播放接口
        vid = re.findall(r'vid: "(.*?)"', response.text)[0]
        url = self.video_url.format(vid)
        yield scrapy.Request(url, callback=self.video, dont_filter=True)
        # 当前视频页面解析数据
        loader = ItemLoader(item=XPCVideoItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', "//div[@class='title-wrap']/h3/text()")
        loader.add_xpath('desc_info', "//div[@class='filmplay-info-desc left-section']/p/text()")
        loader.add_xpath('favor_num', "//span[@class='v-center like-counts fs_12 c_w_f fw_300']/text()")
        loader.add_xpath('tags', "//div[@class='fs_12 fw_300 c_b_3 tag-wrapper']/a/text()")
        loader.add_xpath('publish_time', "//span[@class='update-time v-center']/i/text()")
        loader.add_value('article_id', response.meta.get('article_id'))
        if '本片创作人' in response.text:
            loader.add_xpath('creator_rose', "//ul[@class='creator-list']//span[@class='roles fs_12 fw_300 c_b_9']/text()")
            loader.add_xpath('creator_name', "//ul[@class='creator-list']//div[contains(@class,'follow-btn fs_12 c_w_f bg-red')]/@data-username")
            loader.add_xpath('creator_id', "//ul[@class='creator-list']//div[contains(@class,'follow-btn fs_12 c_w_f bg-red')]/@data-userid")
        else:
            loader.add_value('creator_rose', '')
            loader.add_value('creator_name', '')
            loader.add_value('creator_id', '')
        loader.add_value('crawl_time', datetime.datetime.now())
        item = loader.load_item()
        yield item


    def video(self, response):
        content = json.loads(response.text)['data']
        item = VideoItem()
        item['cover_image'] = content['video']['cover']
        item['duration'] = content['video']['duration']
        item['video_url'] = content['resource']['default']['url']
        item['author_id'] = content['resource']['default']['id']
        item['crawl_time'] = datetime.datetime.now()
        yield item

    def parse_comment(self, response):
        content = json.loads(response.text)['data']
        data_list = content['list']
        for data in data_list:
            item = XPCCommentItem()
            item['user_id'] = data['userid'] or ''
            item['articleid'] = data['resource_id']
            item['content'] = data['content']
            item['addtime'] = data['addtime']
            item['approve_num'] = data['count_approve']
            item['username'] = data['userInfo']['username'] or ''
            item['avator'] = data['userInfo']['avatar']
            web_url = data['userInfo']['web_url'] or ''
            item['web_url'] = web_url
            item['crawl_time'] = datetime.datetime.now()
            yield item
            yield scrapy.Request(web_url, callback=self.parse_author, meta={'userid': data['userid']})
        next_page_url = urljoin(response.url, content['next_page_url'])
        print(next_page_url)
        if next_page_url:
            yield scrapy.Request(next_page_url, callback=self.parse_comment)


    def parse_author(self, response):
        loader = ItemLoader(item=XPCAuthorItem(), response=response)
        loader.add_xpath('creator_name', "//div[@class='creator-info']//p[contains(@class, 'creator-name')]/text()")
        loader.add_xpath('creator_desc', "//div[@class='creator-info']//p[contains(@class, 'creator-desc')]/text()")
        loader.add_xpath('like_counts', "//span[contains(@class, 'like-counts')]/text()")
        loader.add_xpath('fans_counts', "//span[contains(@class, 'fans-counts')]/text()")
        loader.add_xpath('follow_wrap', "//span[@class='follow-wrap']//span[@class='fw_600 v-center']/text()")
        loader.add_xpath('location', "//span[@style='margin-left: 5px;']/text()")
        loader.add_value('crawl_time', datetime.datetime.now())
        item = loader.load_item()
        yield item

        # 粉丝url
        followed_url = 'https://www.xinpianchang.com/user/getUserfollow?type=followed&page=1&userid={}'.format(response.meta.get('userid'))
        # 关注url
        follow_url = 'https://www.xinpianchang.com/user/getUserfollow?type=follow&page=1&userid={}'.format(response.meta.get('userid'))
        yield scrapy.Request(followed_url, callback=self.parse_person, dont_filter=True, meta={'type': 'fans','personid': response.meta.get('userid')})
        yield scrapy.Request(follow_url, callback=self.parse_person, dont_filter=True, meta={'type': 'atten', 'personid': response.meta.get('userid')})

    def parse_person(self, response):
        data = json.loads(response.text)['data']
        for content in data['list']:
            item = XPCFansAttenItem()
            if response.meta.get('type') == 'fans':
                item['type_name'] = 'fans'
            else:
                item['type_name'] = 'attention'
            item['author_id'] = response.meta.get('personid')
            item['userid'] = content['userid']
            item['username'] = content['username']
            item['count_follow'] = content['count_follow']
            item['count_followed'] = content['count_followed']
            item['face'] = content['face']
            item['email'] = content['email'] or ''
            item['descri'] = content['desc'] or ''
            item['phone'] = content['phone'] or ''
            item['country'] = content['country'] or ''
            item['province']  = content['province'] or ''
            item['city'] = content['city']
            item['profession'] = content['profession']
            item['year'] = content['year'] or ''
            item['mouth'] = content['mouth']
            item['day'] = content['day']
            yield item
        total_page = data['totalPage']
        curr_page = re.search(r'page=(\d+)', response.url).group(1)
        if int(curr_page) < total_page:
            next_page = int(curr_page) + 1
            url = response.url.replace(str(curr_page), str(next_page))
            yield scrapy.Request(response.url.replace(str(curr_page), str(next_page), 1), callback=self.parse_person, dont_filter=True)



