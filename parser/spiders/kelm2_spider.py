import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlparse
from langdetect import detect  # For language detection
from langdetect.lang_detect_exception import LangDetectException


class KelmSpider(scrapy.Spider):
    name = 'kelm'
    start_urls = ['https://kelm-immobilien.de/immobilien/']

    def parse(self, response):
        domain = urlparse(response.url).netloc
        country = self.get_country_from_domain(domain)
        rental_object = response.xpath('/html/body/div[2]/h1/text()').get()

        yield {
            'Country': country,
            'Domain': domain,
            'Rental Object': rental_object,
        }

        links = response.xpath('//h3/a/@href').extract()
        for link in links:
            yield response.follow(link, self.parse_property, meta={'country': country})

    def parse_property(self, response):
        # Extract all image URLs within the galleria
        image_urls = response.xpath('//div[@id="immomakler-galleria"]//img/@src').extract()
        for image_url in image_urls:
            if not image_url.startswith('http'):
                image_url = response.urljoin(image_url)
            yield scrapy.Request(image_url, self.save_image)

        title = response.xpath('/html/body/div[2]/h1/text()').get()
        price = response.xpath('//div[contains(text(), "Kaufpreis")]/following-sibling::div/text()').get()
        description_paragraphs = response.xpath(
            '//div[@class="property-description panel panel-default"]//div[@class="panel-body"]/p/text()').getall()
        description = ' '.join(description_paragraphs).strip() if description_paragraphs else None
        phone = response.xpath('//div[@class="dd col-sm-7 p-tel value"]/a/text()').get()
        email = response.xpath('//div[@class="dd col-sm-7 u-email value"]/a/text()').get()
        rental_object = response.xpath('/html/body/div[2]/h1/text()').get()

        # Logging for debugging
        self.logger.info(f'Extracted price: {price}')
        self.logger.info(f'Extracted description: {description}')
        self.logger.info(f'Extracted phone: {phone}')
        self.logger.info(f'Extracted email: {email}')
        self.logger.info(f'Extracted rental object: {rental_object}')

        yield {
            'Country': response.meta.get('country'),
            'Domain': response.url.split('/')[2],
            'Rental Object': rental_object.strip() if rental_object else None,
            'Title': title.strip() if title else None,
            'Link': response.url,
            'Price': price.strip() if price else None,
            'Description': description.strip() if description else None,
            'Phone': phone.strip() if phone else None,
            'Email': email.strip() if email else None,
        }

    def save_image(self, response):
        filename = response.url.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info('Saved image %s' % filename)

    def get_country_from_domain(self, domain):
        if domain.endswith('.de'):
            return 'Germany'
        if domain.endswith('.se'):
            return 'Sweden'
        return None