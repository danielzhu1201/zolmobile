#coding:utf-8
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json,re
from scrapy.conf import settings
from lxml import etree
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from twisted.internet import reactor
reactor.suggestThreadPoolSize(30)

class mobilephoneSpider(CrawlSpider):
    name="mobilephone"
    allowed_domains=["zol.com.cn"]
    start_urls=['http://detail.zol.com.cn/cell_phone_index/subcate57_list_1.html']
    
	rules=(
		Rule(
		    LxmlLinkExtractor(
		        allow=('detail.zol.com.cn/\d*?/\d*?/param.shtml',), //means only allow this webpage
		        deny=(),
		        ),
		    follow=False, //if links should be followed from each response extracted with this rule
		    process_links=lambda links:[link for link in links if not link.nofollow],
		    callback='parse'),
		Rule(
		    LxmlLinkExtractor(
		        allow=('detail.zol.com.cn/cell_phone/index\d*?.shtml',),
		        deny=(),
		        ),
		    follow=False,
		    process_links=lambda links:[link for link in links if not link.nofollow],
		    callback='parse_price'),
		Rule(
		    LxmlLinkExtractor(
		        allow=('/cell_phone_index/subcate57_\d*?_list_1[_\d]*?\.html',), //this format is wrong 
			// check this http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_1.html
		        deny=('digital','notebook','tablepc','gps','keyboards_mouse','desktop_pc',
		              'gpswatch','zsyxj','motherboard','vga','cpu','hard_drives','menmery',
		              'case','power','cooling_product','solid_state_drive','dvdrw','sound_card',
		              'diy_host','usb-hub','speaker','mb_chip'),
		        ),
		    follow=True,
		    process_links=lambda links:[link for link in links if not link.nofollow],
		    )
        )

    def parse(self,response):
        mobile_info_dict={}
        mobile_info_dict["_id"] = response.url
        mobile_info_dict['zolSubName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolSubName\s*= \'([^\']*)',response.body_as_unicode())]) //can we do better than this?
        if mobile_info_dict['zolSubName']!=u'\u624b\u673a':return []  //"手机"的unicode
        mobile_info_dict['type']='param'

        mobile_info_dict['source_url']=response.url

        mobile_code_match=re.match('http://detail.zol.com.cn/\d*?/\d*?/param.shtml',response.url)

        if mobile_code_match:mobile_info_dict['mobile_code']=mobile_code_match.group()

        mobile_info_dict['zolproductid']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproductid\D*(\d*)',response.body)])

        mobile_info_dict['zolproduct']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolproduct\s*= \"([^\"]*)',response.body_as_unicode())])

        mobile_info_dict['zolManuCnName']='|'.join([line.strip().replace("\n","") for line in re.findall('var zolManuCnName\s*= \'([^\']*)',response.body_as_unicode())])

        selector_res=Selector(response)

#        mobile_info_dict['param-icon']='|'.join(['|'.join([x.strip().replace("\n","") for x in re.findall('/(\d*)\.png',link)]) for link in selector_res.xpath('//table[@class="param-icon-table"]//li/img/@src').extract()]) #doesn't work

        mobile_info_dict['breadcrumb']='|'.join([line.strip().replace("\n","") for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()])

        mobile_info_dict['page-title']=''.join([line.strip().replace("\n","") for line in selector_res.xpath('//h1/text()').extract()])

#        mobile_info_dict['version-series']=''.join([line.strip().replace("\n","") for line in selector_res.xpath('//div[@class="version-series"]/span/text()').extract()]) #doesnt work
	

	#not ok
        mobile_infos=selector_res.xpath('//div[@class="detailed-parameters"]/table/tr') #直接在tr下面找就行，要匹配newPmName 和 newPmVal
	# extract all tables out
        for mobile_info in mobile_infos:
            mobile_info_tag=''.join([line.strip().replace("\n","") for line in mobile_info.xpath('span[contains(@id,"newPmName")]/text()').extract()])

            mobile_info_value='|'.join([line.strip().replace("\n","") for line in mobile_info.xpath('span[contains(@id,"newPmVal")]/a/text()').extract()])

            if mobile_info_tag!=u'\u8be6\u7ec6\u5185\u5bb9' and mobile_info_value:
                pass	
            
	    else:
                mobile_info_value='|'.join([line.strip().replace("\n","") for line in mobile_info.xpath('span[contains(@id,"newPmVal")]/text()').extract()])
            mobile_info_dict[mobile_info_tag]=mobile_info_value
            
        return [mobile_info_dict,]

    def parse_price(self,response):
        mobile_info_dict={}
        mobile_info_dict['type']='price'
        mobile_info_dict['source_url']=response.url
        mobile_info_dict['proId']='|'.join(re.findall('var proId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['seriesId']='|'.join(re.findall('seriesId\D*(\d*)',response.body)) #this one's right
        mobile_info_dict['subcateId']='|'.join(re.findall('var subcateId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['subcateName']='|'.join([line.strip() for line in re.findall('var subcateName\s*= \'([^\']*)',response.body_as_unicode())]).replace("\n","")
        mobile_info_dict['manuId']='|'.join(re.findall('var manuId\D*(\d*)',response.body)).replace("\n","")
        mobile_info_dict['manuName']='|'.join([line.strip() for line in re.findall('var manuName\s*= \'([^\']*)',response.body_as_unicode())]).replace("\n","")
        mobile_info_dict['proName']='|'.join([line.strip() for line in re.findall('var proName\s*= \'([^\']*)',response.body_as_unicode())]).replace("\n","")



        selector_res=Selector(response)
	#ok
        mobile_info_dict['breadcrumb']='|'.join([line.strip() for line in selector_res.xpath('//div[@class="wrapper clearfix"]/div[@class="breadcrumb"]/a/text()').extract()]).replace("\n","")

        mobile_info_dict['page-title']=''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"product-model page-title clearfix")]/h1/text()').extract()]).replace("\n","")

        mobile_info_dict['anothername']=re.sub(u'\u522b\u540d\uff1a','',''.join([line.strip() for line in selector_res.xpath('//div[contains(@class,"page-title")]/h2/text()').extract()])).replace("\n","")

        mobile_info_dict['price']=''.join(selector_res.xpath('//div[@class="price price-normal"]/span/b[contains(@class,"price-type")]/text()').extract())

        mobile_info_dict['rate'] = "|".join([line.strip() for line in selector_res.xpath("//div[@class='review-comments-score clearfix']//div[@class='total-score']/strong/text()").extract()]).replace("\n","")
	
        mobile_info_dict['commentCount'] = "|".join(selector_res.xpath("//div[@class='section comments-section']//div[@class='section-header']//span[@class='section-header-desc']//em/text()").extract()).replace("\n","")

        mobile_info_dict['goodWords'] = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='good-words']/a/text()").extract()).replace("\n","")
        mobile_info_dict['badWords'] = "|".join(selector_res.xpath("//div[@class='comments-words']//ul[@class='words-list clearfix']/li[@class='bad-words']/a/text()").extract()).replace("\n","")
        return mobile_info_dict
		#
