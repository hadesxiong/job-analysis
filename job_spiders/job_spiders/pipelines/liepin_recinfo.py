# coding=utf8

from job_spiders.items.liepin_items import LiePinRecItem
from scrapy.exceptions import DropItem

import redis,json

class JobRecPipeline:

    @classmethod
    def from_crawler(cls,crawler):

        # redis配置信息
        redis_conf = {
            'redis_host': crawler.settings.get('REDIS_HOST'),
            'redis_port': crawler.settings.get('REDIS_PORT'),
            'redis_db': crawler.settings.get('REDIS_DB_STORGE'),
            'redis_pw': crawler.settings.get('REDIS_PW')
        }

        return cls(redis_conf)
    
    def __init__(self,redis_conf):

        self.redis_conf = redis_conf

    def open_spider(self,spider):

        # REDIS数据库
        self.redis_pool = redis.ConnectionPool(
            host=self.redis_conf.get('redis_host'),
            port=self.redis_conf.get('redis_port'),
            db=self.redis_conf.get('redis_db'),
            password=self.redis_conf.get('redis_pw'),
            decode_responses=True)
        self.redis_db =  redis.Redis(connection_pool=self.redis_pool)

        # 声明数据存储列表
        # self.rec_list = []

    def process_item(self,item,spider):

        if item is not None:

            data_item = item.get('item')

            rec_item = LiePinRecItem()
            rec_data = data_item.get('recruiter')

            rec_item['rec_id'] = rec_data.get('recruiterId')
            rec_item['rec_name'] = rec_data.get('recruiterName')
            rec_item['rec_title'] = rec_data.get('recruiterTitle')
            rec_item['rec_imtype'] = rec_data.get('imUserType')
            rec_item['rec_imid'] = rec_data.get('imId')
            rec_item['rec_img'] = f'https://image0.lietou-static.com/big/{rec_data.get("recruiterPhoto")}'

            # redis写入
            rec_res = self.redis_db.hsetnx(
                'job_spiders_liepin_recinfo',
                rec_item['rec_id'],
                json.dumps(dict(rec_item))
            )

            if rec_res != 1:
                DropItem()
            else:
                return item
            
        else:
            pass
    
    def close_spider(self,spider):

        self.redis_pool.disconnect()