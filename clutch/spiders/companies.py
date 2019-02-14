# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request
import js2xml
import re


class CompaniesSpider(Spider):
    name = 'companies'
    allowed_domains = ['clutch.co/seo-firms']
    start_urls = ['https://clutch.co/seo-firms']

    def _get_email(self, email):
        email = email.split('\n')[0].split(' ').pop()
        email = re.sub("'", '', email)
        email = re.sub(';', '', email)
        return email.split('#')

    def _parse_script(self, snippet):
        order = js2xml.parse(snippet).xpath('//number/@value')
        return order[:len(order)/2:]

    def parse(self, response):
        companies = response.xpath('//ul/li[@class="provider-row"]')
        for company in companies:
            company_name = company.xpath('.//h3[@class="company-name"]/span/a/text()').extract_first()
            company_url = company.xpath('.//li[@class="website-link website-link-a"]/a/@href').extract_first()
            email = company.xpath('.//div[@class="item"]/script/text()').extract_first()

            if email:
                order = self._parse_script(email)
                email = self._get_email(email)
                company_email = ''

                for num in order:
                    company_email = company_email + email[int(num)]
            else:
                company_email = ''

            employee_range = company.xpath('.//span[@class="employees"]/text()').extract_first()
            city = company.xpath('.//span[@class="locality"]/text()').extract_first("")
            region = company.xpath('.//span[@class="region"]/text()').extract_first("")

            if region:
                s = (city, region)
            else:
                s = (city, company.xpath('.//span[@class="country-name"]/text()').extract_first(""))

            location = ' '
            location = location.join(s)

            yield {
                'company_name': company_name,
                'company_url': company_url,
                'company_email': company_email,
                'employee_range': employee_range,
                'location': location
            }

        next_page = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()
        absolute_next_page = response.urljoin(next_page)
        yield Request(absolute_next_page, callback=self.parse, dont_filter=True)
