#!/usr/bin/env python
# encoding: utf-8
"""
fetch.py

Created by Roy on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import re 
import lxml.html
import web
from sinat import Sinat, OAuthToken, OAuthConsumer  
from trunkly import Trunkly

                                           
TRUNK_KEY='5229-4bdad3ab-650d-4f6d-9e8e-8912cb841d76'
SINA_CONSUMER_KEY = '3892402622' # your App Key
SINA_CONSUMER_SECRET = '6af8bdaa10fb55fa82089a8a29787f81' # your App Secret  

db = web.database(dbn='mysql', db='SINALY', user='root', pw='')
sinaConsumer = OAuthConsumer(SINA_CONSUMER_KEY, SINA_CONSUMER_SECRET)
p = re.compile('http://[\\w\\.\\-\\/]+')


def main():  
	users = db.select("users")
	for user in users:
		# print 'user %s ' % user.token
		# print 'user %s ' % user.secret
		access_token = OAuthToken(user.token, user.secret) 
		sinat = Sinat(sinaConsumer, access_token=access_token)	
		
		if not user.trunk_key:
			continue
			
		t = Trunkly(user.trunk_key) 
		
		statuses = sinat.statuses__user_timeline('GET')
		for status in statuses:
			weibo = status['text']
			if status.has_key('retweeted_status'):
				weibo = '%s //@%s: %s' % (weibo , 
											status['retweeted_status']['user']['name'],
											status['retweeted_status']['text'])
				
			# print 'status %s' % status['text']
			urls = p.findall(weibo)
			for url in urls:
				print 'url is %s ' % url
				try:
					html = lxml.html.parse(url)
					title = html.find(".//title").text
					print 'title is %s' % title
					t.post_link({'url': url,
									'title': title,
									'tags' : '',
									'note' : weibo,
									'text' : weibo})
									
				except:
					print 'url %s fetch error: %s' % (url, html.message)
				

if __name__ == '__main__':
	main()
