#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import argparse, pickle, os, json, sys, time
sys.path.append("..")

def crawl_spys_ru(page):

	import requests, re, lxml.html, cStringIO
	from lxml import etree
	url = 'http://spys.ru/en/http-proxy-list/%d/'%page

	# payload = {
	# 	'sto': 'View+150+per+page'
	# }
	r = requests.get(url)

	html = r.text.encode('utf8')

	# the port numbers are coded...
	coded = re.findall(r'<\/table><script type="text\/javascript">(.*?)<\/script>', html)[0]
	xx = coded.split(';')
	for x in xx:
		exec(x)

	proxies = []

	ms = re.findall(r'<tr\sclass=spy1x.*?<\/tr>', html)
	#logger.info(len(ms))
	for m in ms:
		#logger.info(m)
		tr = lxml.html.fragment_fromstring(m)
		tds = tr.findall("td")

		if (len(tds) > 1):

			proxy = None
			proxy_type = None
			country = None
			cnt = 0
		# logger.info(len(tds))
			for td in tds:
				text = td.text_content().encode("utf8")
				if (text == 'Proxy address:port'):
					break

				if cnt == 0:
					hh = lxml.html.tostring(td)
					ip = re.findall(r'<font\sclass="spy14">(.*?)<script', hh)[0]

					pp = re.findall(r'\(([^"]*?)\)', hh)
					
					port = ""
					for p in pp:
						port += str(eval(p))

					proxy = '%s:%s'%(ip, port)
					

				if cnt == 1:
					proxy_type = text.lower()

				if cnt == 3:
					hh = lxml.html.tostring(td)
					country = re.findall(r'<font class="spy14">(.*?)<\/font>', hh)[0]

				cnt += 1

				if cnt > 3:
					break

			if (proxy):
				#proxies.append((proxy, proxy_type, country))
				proxies.append({proxy: proxy_type})

	return proxies
		

from tweetf0rm.proxies import proxy_checker

if __name__=="__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output', help="define the location of the output;", default="proxies.json")
	args = parser.parse_args()
	
	proxies = []
	for i in range(5):
		proxies.extend(crawl_spys_ru(i))

	proxies = [p['proxy'] for p in proxy_checker(proxies)]

	logger.info(len(proxies))
	with open(os.path.abspath(args.output), 'wb') as proxy_f:
		json.dump({'proxies':proxies}, proxy_f)
	

			


