import scrapy
from myproject.items import MyItem  # Adjust the import path as necessary


class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://example.com/page1']

    def parse(self, response):
        # Parse all items from the first page
        for item_selector in response.css('your_css_selector_for_items'):
            item = MyItem()
            item['field1'] = item_selector.css('your_css_selector_for_field1::text').get()
            item['field2'] = item_selector.css('your_css_selector_for_field2::text').get()
            # Add more fields as needed

            # Check if the condition to scrape the second page is met
            if 'full text' in item['field1'] or 'full text' in item['field2']:
                # Extract the parameter needed for the second URL
                parameter = item['field1']  # or any other field containing the parameter
                # Construct the URL for the second page
                second_url = f'https://example.com/page2?parameter={parameter}'
                # Yield a request to scrape the second URL, passing the item in the meta to carry it through
                yield scrapy.Request(second_url, callback=self.parse_second_page, meta={'item': item})
            else:
                yield item

    def parse_second_page(self, response):
        # Extract additional data from the second page
        additional_field = response.css('your_css_selector_for_additional_field::text').get()

        # Retrieve the item from meta
        item = response.meta['item']

        # Update the item with additional data
        item['additional_field'] = additional_field

        yield item
