#coding:utf-8
import scrapy
import re
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class DatabloggerSpider(CrawlSpider):
    # The name of the spider
    name = "zol"

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
        print ("parse \n\n")
        # parsing all the info from webpage
        mobile_info_dict={}
        mobile_info_dict['type']='price'
        mobile_info_dict['source_url']=response.url
        mobile_info_dict['proId']='|'.join(re.findall('proId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['seriesId']='|'.join(re.findall('seriesId\D*(\d*)',response.body)) #this one's right
        mobile_info_dict['subcateId']='|'.join(re.findall('subcateId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['subcateName']='|'.join([line.strip() for line in re.findall('subcateName\D*(\s*)',response.body_as_unicode())]).replace("\n","")# dont work
        mobile_info_dict['manuId']='|'.join(re.findall('manuId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['manuName']='|'.join([line.strip() for line in re.findall('manuName\s*= \'([^\']*)',response.body_as_unicode())]).replace("\n","")# dont work
        
        selector_res=Selector(response)
        mobile_info_dict['breadcrumb']='|'.join([line.strip() for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()]).replace("\n","")
        mobile_info_dict['page-title']=''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"product-model page-title clearfix")]/h1/text()').extract()]).replace("\n","")
        mobile_info_dict['anothername']=re.sub(u'\u522b\u540d\uff1a','',''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"page-title")]/h2/text()').extract()])).replace("\n","")
        mobile_info_dict['price']=''.join(selector_res.xpath('//div[@class="price price-normal"]/span/b[contains(@class,"price-type")]/text()').extract())
        mobile_info_dict['rate'] = "|".join([line.strip() for line in selector_res.xpath("//div[@class='review-comments-score clearfix']//div[@class='total-score']/strong/text()").extract()]).replace("\n","")
        mobile_info_dict['commentCount'] = "|".join(selector_res.xpath("//div[@class='section comments-section']//div[@class='section-header']//span[@class='section-header-desc']//em/text()").extract()).replace("\n","")
        mobile_info_dict['goodWords'] = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='good-words']/a/text()").extract()).replace("\n","")
        mobile_info_dict['badWords'] = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='bad-words']/a/text()").extract()).replace("\n","")

        yield mobile_info_dict
        #item2 = {}
        #item2["hey"] = "halo"
        #yield item2     # will be divided into two pipelines
        # Only extract canonicalized and unique links of param (with respect to the current page)
        links = LinkExtractor(allow = ('param.shtml',),canonicalize=True,unique=True).extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback = self.parse2)
   
    def parse2(self, response):
        print (response.url)
        print ("\n\n\n\n parse 2\n\n")
        # The list of items that are found on the particular page
        mobile_info_dict={}
        mobile_info_dict["_id"] = response.url
        mobile_info_dict['zolSubName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolSubName\s*= \'([^\']*)',response.body_as_unicode())]) #can we do better than this?
        if mobile_info_dict['zolSubName']!=u'\u624b\u673a':yield {}  #"手机"的unicode
        mobile_info_dict['type']='param'

        mobile_info_dict['source_url']=response.url

        mobile_code_match=re.match('http://detail.zol.com.cn/\d*?/\d*?/param.shtml',response.url)

        if mobile_code_match: mobile_info_dict ['mobile_code']= mobile_code_match.group()
        mobile_info_dict['zolproductid']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproductid\D*(\d*)',response.body)])
        mobile_info_dict['zolproduct']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproduct\s*= \"([^\"]*)',response.body_as_unicode())])
        mobile_info_dict['zolManuCnName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolManuCnName\s*= \'([^\']*)',response.body_as_unicode())])

        selector_res=Selector(response)

        mobile_info_dict['breadcrumb']='|'.join([line.strip().replace("\n","") for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()])
        mobile_info_dict['page-title']=''.join([line.strip().replace("\n","") for line in selector_res.xpath('//h1/text()').extract()])	
	#ok
        mobile_infos=selector_res.xpath('//div[@class="detailed-parameters"]/table/tr') #直接在tr下面找就行，要匹配newPmName 和 newPmVal
        for mobile_info in mobile_infos:
            mobile_info_tag=''.join([line.strip().replace("\n","") for line in mobile_info.xpath('th/span[contains(@id,"newPmName")]/text()').extract()])

            mobile_info_value='|'.join([line.strip().replace("\n","") for line in mobile_info.xpath('td/span[contains(@id,"newPmVal")]/text()').extract()])

            if mobile_info_tag!=u'\u8be6\u7ec6\u5185\u5bb9' and mobile_info_value: pass	
	        #else:
            #    print 666
                #mobile_info_value='|'.join([line.strip().replace("\n","") for line in mobile_info.xpath('td/span[contains(@id,"newPmVal")]/text()').extract()])
            
            mobile_info_dict[mobile_info_tag]=mobile_info_value

        yield mobile_info_dict
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)	
