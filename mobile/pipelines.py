# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.crawler import Settings as settings
import traceback

class MobilePipeline(object):
	def __init__(self):
		conn = dict(
			host = "localhost",
			db = "zolmobile",
			user = "root",
			passwd = "12345678",
			charset = "utf8",
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode = True,
		)
		self.dbpool = adbapi.ConnectionPool("MySQLdb",**conn)

	def process_item(self,item,spider):
		if item['type'] == 'price':
			res = self.dbpool.runInteraction(self.insert_into_table,item)
		elif item['type'] == 'param':
			res = self.dbpool.runInteraction(self.insert_into_videotable,item)
		else:
			pass

	def insert_into_table(self,conn,item):
	    try:
		data = tuple([
						item['type'],
						item['source_url'],
						item['proId'],
						item['seriesId'],
						item['subcateId'],
						item['subcateName'],
						item['manuId'],
						item['manuName'],
						item['breadcrumb'],
						item['page_title'],
						item['anothername'],
						item['price'],
						item['rate'],
						item["commentCount"],
						item['goodWords'],
						item['badWords'],
				])
        	conn.execute(
		    'insert into price(type,source_url,proId,seriesId,subcateId,subcateName,manuId,manuName,breadcrumb,page_title,anothername,price,rate,commentCount,goodWords,badWords) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % data
                    )
					
            except Exception as e:
    		traceback.print_exc()

	def insert_into_videotable(self,conn,item):
		try:
		
			data = tuple([
						item['_id'],
						item['zolSubName'],
						item['type'],
						item['source_url'],
						item['mobile_code'],
						item['zolproductid'],
						item['zolproduct'],
						item['zolManuCnName'],
						item['breadcrumb'],
						item['page_title'],
						item['spec'],
			])

			print len(data)
        		conn.executemany(
				'insert into info(_id,zolSubName,type,source_url,mobile_code,zolproductid,zolproduct,zolManuCnName,breadcrumb,page_title,spec) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', [data, ]
				)
        	except Exception as e:
        		traceback.print_exc()
