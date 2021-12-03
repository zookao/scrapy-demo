# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders.crawl import Rule
from Boss.items import BossItem


class BossSpider(RedisCrawlSpider):
    name = 'BossSpider'
    allowed_domains = ['zhipin.com"']

    redis_key = "boss:start_urls"

    cookie_list = "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1618820773; lastCity=100010000; __g=-; wt2=DduKFGCrL5ZDcFyofHa1dLYZJi9lyrzGlKU1co-V5cv1EvzVeTI5dJUXK7CIXjHXzYaGlgMcmyl935FKYy6uPTQ~~; geek_zp_token=V1Rd8gFOT001hgXdNoxh0dKS2z5D_fwA~~; __c=1618820775; __a=74953393.1618820775..1618820775.15.1.15.15; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1619050098; __zp_stoken__=8a2dcOEx%2BGVYcJWYaeF5wEQY6KnJxajljSgZzdXZRO20WKjc1MRwadQAUEQEIUWshJmQSfyAMeHdtcQYtDVIFR0IXO2dhFTY0UwI%2FQ19wLAESJVwSVBJmYmF9blF%2FSk1cFkcCZF99BnZkOF0N"
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Cookie': cookie_list,
            'Referer': 'https://www.zhipin.com/beijing/',
        }
    }

    rules = (
        Rule(LinkExtractor(allow=r'.+page=%d+&ka=page-%d+/'), follow=True),
        Rule(LinkExtractor(allow=r'.+/job_detail/.+\.html'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        # print("="*40)
        # print(response.body)
        # print("=" * 40)
        job_name = response.xpath('//div[@class="name"]/h1/text()').get()
        job_detail = response.xpath('//div[@class="info-primary"]/p//text()').getall()
        job_city = job_detail[0]
        job_experience = job_detail[1]
        job_education = job_detail[2]
        company_name = response.xpath('//div[@class="info-company"]/h3/a/text()').get()
        loc_job = response.xpath('//div[@class="location-address"]/text()').get()

        job_secs = response.xpath('//div[@class="job-sec company-info"]/h3/text()').get()
        if job_secs == '公司介绍':
            company_describe_detail = response.xpath('//div[@class="job-sec company-info"]/div[@class="text"]/text()').getall()
            company_describe_detail = '\n'.join(company_describe_detail).strip()
        else:
            company_describe_detail = '无'

        job_secs = response.xpath('//div[@class="job-sec"]')
        job_describe_detail,team_describe_detail,business_information = '无','无','无'
        for job_sec in job_secs:
            sec_describe = job_sec.xpath('./h3/text()').get()
            if sec_describe == '职位描述':
                job_describe_detail = job_sec.xpath('./div[@class="text"]/text()').getall()
                job_describe_detail = '\n'.join(job_describe_detail).strip()

            if sec_describe == '团队介绍':
                team_describe_detail = job_sec.xpath('./div[@class="text"]/text()').getall()
                team_describe_detail = '\n'.join(team_describe_detail).strip()

            if sec_describe == '工商信息':
                business_information_1 = job_sec.xpath('./div[@class="name"]/text()').getall()
                business_information_1 = ''.join(business_information_1).strip()
                business_information_2 = job_sec.xpath('./div[@class="level-list"]/li//text()').getall()
                business_information_2 = '\n'.join(business_information_2).strip()
                business_information = business_information_1+'\n'+business_information_2

        item = BossItem(
            job_name =  job_name,
            job_city = job_city,
            job_experience = job_experience,
            job_education = job_education,
            company_name = company_name,
            loc_job = loc_job,
            company_describe_detail = company_describe_detail,
            job_describe_detail = job_describe_detail,
            team_describe_detail = team_describe_detail,
            business_information = business_information
        )

        yield item




