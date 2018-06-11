#coding:utf-8
import scrapy
import re
import json
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
        mobile_info_dict['proId']=re.findall('proId\D*(\d*)',response.body)[0].replace("\n","")
        mobile_info_dict['seriesId']='|'.join(re.findall('seriesId\D*(\d*)',response.body)) #this one's right
        mobile_info_dict['subcateId']=re.findall('subcateId\D*(\d*)',response.body)[0].replace("\n","")
        mobile_info_dict['subcateName']='|'.join([line.strip() for line in re.findall(u'subcateName[\s，,：:\']*(\S*?)\'',response.body_as_unicode())]).replace("\n","")# dont work
        mobile_info_dict['manuId']='|'.join(re.findall('manuId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['manuName']='|'.join([line.strip() for line in re.findall(u'manuName[\s，,：:\']*(\S*?)\'',response.body_as_unicode())]).replace("\n","")# that's the brand
        
        selector_res=Selector(response)
        mobile_info_dict['breadcrumb']='|'.join([line.strip() for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()]).replace("\n","")
        mobile_info_dict['page_title']=''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"product-model page-title clearfix")]/h1/text()').extract()]).replace("\n","")
        mobile_info_dict['anothername']=re.sub(u'\u522b\u540d\uff1a','',''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"page-title")]/h2/text()').extract()])).replace("\n","")
        #if anothername empty - use zolproduct from info page
        mobile_info_dict['price']=''.join(selector_res.xpath('//div[@class="price price-normal"]/span/b[contains(@class,"price-type")]/text()').extract())
        if mobile_info_dict['price'] == '':
            mobile_info_dict['price'] = ''.join(selector_res.xpath('/html/body/div[13]/div[2]/div[2]/div/span[1]/b[2]/text()').extract())
        #that's a placeholder, need to do request on another page to get real price
        if mobile_info_dict['price'] == '':
            temp_url = 'http://detail.zol.com.cn/xhr4_Merchant_DetailList_proId='+mobile_info_dict['proId']+'%5EprovinceId=30%5EcityId=347%5Etype=1%5Emark=201861112.html'
            yield scrapy.Request(temp_url, callback=self.parse_real_price)
        
        mobile_info_dict['rate'] = "|".join([line.strip() for line in selector_res.xpath("//div[@class='review-comments-score clearfix']//div[@class='total-score']/strong/text()").extract()]).replace("\n","")
        mobile_info_dict['commentCount'] = "|".join(selector_res.xpath("//div[@class='section comments-section']//div[@class='section-header']//span[@class='section-header-desc']//em/text()").extract()).replace("\n","")
        temp = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='good-words']/a/text()").extract()).replace("\n","")
        if temp: mobile_info_dict['goodWords'] = temp
        else: mobile_info_dict['goodWords'] = 'null'
        temp2 = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='bad-words']/a/text()").extract()).replace("\n","")
        if temp2: mobile_info_dict['badWords'] = temp2
        else: mobile_info_dict['badWords'] = 'null'
        
        yield mobile_info_dict

        #create new requests to search param
        links = LinkExtractor(allow = ('param.shtml',),canonicalize=True,unique=True).extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback = self.parse2)
   
    def parse2(self, response):
        print ("\n\n\n\n parse 2\n\n")
        # The list of items that are found on the particular page
        mobile_info_dict={}
        mobile_info_dict['_id'] = response.url
        mobile_info_dict['zolSubName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolSubName\s*= \'([^\']*)',response.body_as_unicode())]) #can we do better than this?
        if mobile_info_dict['zolSubName']!=u'\u624b\u673a':yield {}  #"手机"的unicode
        mobile_info_dict['type']='param'

        mobile_info_dict['source_url']=response.url

        mobile_code_match=re.match('http://detail.zol.com.cn/\d*?/\d*?/param.shtml',response.url)

        if mobile_code_match: mobile_info_dict ['mobile_code']= mobile_code_match.group()
        mobile_info_dict['zolproductid']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproductid\D*(\d*)',response.body)])
        mobile_info_dict['zolproduct']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproduct\s*= \"([^\"]*)',response.body_as_unicode())]) #model #
        mobile_info_dict['zolManuCnName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolManuCnName\s*= \'([^\']*)',response.body_as_unicode())])

        selector_res=Selector(response)

        mobile_info_dict['breadcrumb']='|'.join([line.strip().replace("\n","") for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()])
        mobile_info_dict['page_title']=''.join([line.strip().replace("\n","") for line in selector_res.xpath('//h1/text()').extract()])	
	#ok
        #use another dictionary for spec
        mobile_spec_dict = {}
        mobile_infos=selector_res.xpath('//div[@class="detailed-parameters"]/table/tr') #直接在tr下面找就行，要匹配newPmName 和 newPmVal
        for mobile_info in mobile_infos:
            mobile_info_tag=''.join([line.strip().replace("\n","") for line in mobile_info.xpath('th/span[contains(@id,"newPmName")]/text()').extract()])

            mobile_info_value_p1=[line.strip().replace("\n","") for line in mobile_info.xpath('td/span[contains(@id,"newPmVal")]/text()').extract()] #只要value有<a> 就不行
            mobile_info_value_p2 = [line.strip().replace("\n","") for line in mobile_info.xpath('td/span[contains(@id,"newPmVal")]/a/text()').extract()]
            mobile_info_value = [re.sub(u'^，', '', re.sub(u"，$", '', keyword)) for keyword in mobile_info_value_p1] + mobile_info_value_p2
            mobile_info_value='|'.join([_item for _item in mobile_info_value if _item])

            if mobile_info_tag!=u'\u8be6\u7ec6\u5185\u5bb9' and mobile_info_value: pass	
	        #else:
            #    print 666
                #mobile_info_value='|'.join([line.strip().replace("\n","") for line in mobile_info.xpath('td/span[contains(@id,"newPmVal")]/text()').extract()])
            if mobile_info_tag:
                mobile_spec_dict[mobile_info_tag]=mobile_info_value

        mobile_info_dict['spec'] = json.dumps(mobile_spec_dict) #dump all spec out with json.dumps

        yield mobile_info_dict
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

    def parse_real_price(self,response):
        mobile_info_dict={}
        mobile_info_dict['type'] = 'realprice'
        mobile_info_dict['proId'] = ''.join([line.strip().replace("\n","") for line in re.findall('proId\D*(\d*)',response.url)])
        mobile_info_dict['price'] = ''.join([line.strip().replace("\n","") for line in re.findall('price-type\D*(\d*)',response.body)])
        yield mobile_info_dict
