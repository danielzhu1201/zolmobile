import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider


class DatabloggerSpider(CrawlSpider):
    # The name of the spider
    name = "datablogger"

    # The domains that are allowed (links to other domains are skipped)
    allowed_domains = ["zol.com.cn"]

    # The URLs to start with
    start_urls = ["http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_1.html"]

    # This spider has one rule: extract all (unique and canonicalized) links, follow them and parse them using the parse_items method
    rules = [
	Rule(
	     LinkExtractor(
		allow = ('param.shtml',)
	     ),
	     follow=False,
	     callback="parse2"
	),
	Rule(
            LinkExtractor(
		allow = ('cell_phone/index\d*?.shtml',)
            ),
            follow=False,
            callback="parse_price"
        ),
	Rule(
	    LinkExtractor(
		allow = ('/subcate57_0_list_1_0_1_2_0[_\d]*?\.html',),
		deny=('digital','notebook','tablepc','gps','keyboards_mouse','desktop_pc',
                      'gpswatch','zsyxj','motherboard','vga','cpu','hard_drives','menmery',
                      'case','power','cooling_product','solid_state_drive','dvdrw','sound_card',
                      'diy_host','usb-hub','speaker','mb_chip')
            ),
            follow=True
	)
    ]

    # Method which starts the requests by visiting all URLs specified in start_urls
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    # Method for parsing items
    def parse_price(self, response):
	print (response.url)	
	print ("parse\n\n")
        # The list of items that are found on the particular page
	items = {}
	items["type"] = "mobile"
	yield items

	#item2 = {}
	#item2["hey"] = "halo"
	#yield item2     # will be divided into two pipelines
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(allow = ('param.shtml',),canonicalize=True,unique=True).extract_links(response)
        for link in links:
		yield scrapy.Request(link.url, callback = self.parse2)
   
    def parse2(self, response):
	print (response.url)
	print ("parse 2\n\n")
        # The list of items that are found on the particular page
        items = []
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        return items	
