# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from xinpianchang.settings import SQL_DATETIME_FORMAT


def deal_crator_info(name, rose, id):
    if name and rose and id:
        return '-'.join([ ','.join(i) for i in list(zip(name, rose, id))])
    else:
        return None


def deal_num(value):
    return int(value.replace(',', ''))


def deal_city_and_roles(values):
    if len(values) != 1:
        return (values[0], values[1])
    else:
        return (values[0], '')


class XinpianchangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class XPCVideoItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    desc_info = scrapy.Field()
    favor_num = scrapy.Field()
    tags = scrapy.Field()
    publish_time = scrapy.Field()
    article_id = scrapy.Field()
    creator_rose = scrapy.Field()
    creator_name = scrapy.Field()
    creator_id = scrapy.Field()
    creator_info = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into xpcvideo(url, title, desc_info, favor_num, tags, publish_time, article_id,
                creator_info, crawl_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)  on duplicate key update favor_num=favor_num,
                article_id=article_id
        '''
        if self['desc_info']:
            desc_info = self['desc_info'][0].strip()
        else:
            desc_info = ''
        article_id = self['article_id']
        favor_num = deal_num(self['favor_num'][0])
        tags = ''.join(self['tags'])
        creator_info = deal_crator_info(self['creator_name'], self['creator_rose'], self['creator_id'])
        crawl_time = self['crawl_time'][0].strftime(SQL_DATETIME_FORMAT)
        params = (self['url'][0], self['title'][0], desc_info, favor_num, tags, \
                  self['publish_time'][0], article_id, creator_info, crawl_time)
        return insert_sql, params

class VideoItem(scrapy.Item):
    cover_image = scrapy.Field()
    duration = scrapy.Field()
    video_url = scrapy.Field()
    author_id = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into video_url(cover_image, duration, video_url, author_id, crawl_time) values(%s, %s, %s, %s, %s)
             on duplicate key update crawl_time=crawl_time
        '''
        crawl_time = self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        params = (self['cover_image'], self['duration'], self['video_url'], self['author_id'], crawl_time)
        return insert_sql, params


class XPCCommentItem(scrapy.Item):
    user_id = scrapy.Field()
    articleid = scrapy.Field()
    content = scrapy.Field()
    addtime = scrapy.Field()
    approve_num = scrapy.Field()
    username = scrapy.Field()
    avator = scrapy.Field()
    web_url = scrapy.Field()
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = '''
            insert into xpccomment(user_id, articleid, content, addtime, approve_num, username, avator, web_url, crawl_time)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update crawl_time=crawl_time
        '''
        crawl_time = self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        params = (self['user_id'], self['articleid'], self['content'], self['addtime'], self['approve_num'],\
                  self['username'], self['avator'], self['web_url'], crawl_time)
        return insert_sql, params


class XPCAuthorItem(scrapy.Item):
    creator_name = scrapy.Field()
    creator_desc = scrapy.Field()
    like_counts = scrapy.Field()
    fans_counts = scrapy.Field()
    follow_wrap = scrapy.Field()
    location = scrapy.Field()
    roles = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                insert into xpcauthor(creator_name, creator_desc,like_counts, fans_counts, follow_wrap,location, roles, crawl_time) values
                (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update like_counts=like_counts
        '''
        like_counts = deal_num(self['like_counts'][0])
        fans_counts = deal_num(self['fans_counts'][0])
        follow_wrap = deal_num(self['follow_wrap'][0])
        location, roles = deal_city_and_roles(self['location'])
        params = (self['creator_name'][0], self['creator_desc'][0], like_counts, fans_counts, follow_wrap, location, roles, \
                  self['crawl_time'][0].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params

class XPCFansAttenItem(scrapy.Item):
    type_name = scrapy.Field()
    author_id = scrapy.Field()
    username = scrapy.Field()
    userid = scrapy.Field()
    count_follow = scrapy.Field()
    count_followed = scrapy.Field()
    face = scrapy.Field()
    email = scrapy.Field()
    descri = scrapy.Field()
    phone = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    profession = scrapy.Field()
    year = scrapy.Field()
    mouth = scrapy.Field()
    day = scrapy.Field()
    province = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into xpcperson(type_name, author_id, username, userid, count_follow, count_followed, face, email, descri,
                phone, country, city, profession, year, mouth, day, province) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE count_follow=count_follow, author_id=author_id
        '''
        author_id = self['author_id']
        user_id = int((self['userid']))
        count_follow = deal_num(self['count_follow'])
        count_followed = deal_num(self['count_followed'])
        params = (self['type_name'], author_id, self['username'], user_id, count_follow, count_followed, self['face'], self['email'], \
                  self['descri'], self['phone'], self['country'], self['city'], self['profession'], self['year'], self['mouth'], \
                  self['day'], self['province'])
        return insert_sql, params
