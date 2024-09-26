# import scrapy
# from bs4 import BeautifulSoup

# class SimpleSpider(scrapy.Spider):
#     name = 'simple'
    
#     def __init__(self, url=None, *args, **kwargs):
#         super(SimpleSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [url]

#     def parse(self, response):
#         body_html = response.css('body').get()
#         soup = BeautifulSoup(body_html, 'html.parser')
#         body_text = soup.get_text(separator=' ', strip=True)
#         yield {
#             'content': body_text,
#         }
import scrapy
from bs4 import BeautifulSoup

class SimpleSpider(scrapy.Spider):
    name = 'simple'
    
    def __init__(self, url=None, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True)
    
    def parse(self, response):
        body_html = response.css('body').get()
        soup = BeautifulSoup(body_html, 'html.parser')
        body_text = soup.get_text(separator=' ', strip=True)
        yield {
            'content': body_text,
        }

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'HTTPCACHE_ENABLED': False,
        'HTTPCACHE_EXPIRATION_SECS': 60 * 60 * 24,  # 1 day
        'HTTPCACHE_DIR': 'httpcache',
        'HTTPCACHE_IGNORE_HTTP_CODES': [301, 302, 403, 404, 500, 503],
        'HTTPERROR_ALLOWED_CODES': [301, 302, 403, 404, 500, 503],
    }