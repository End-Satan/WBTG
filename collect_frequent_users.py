import telepost
from telegram_util import getWid
import time
import cached_url
import yaml

DAYS = 1 # 365
channels = [
	'daily_feminist',
	'freedom_watch',
	'queer_liberation',
	'life_with_disabilities',
	'labor_one']

wb_prefix = 'https://m.weibo.cn/statuses/show?id='
def getJson(link):
	wid = getWid(link)
	try:
		time.sleep(5)
		json = yaml.load(cached_url.get(wb_prefix + wid, force_cache=True), Loader=yaml.FullLoader)
		return json['data']
	except:
		return

def getWeiboLinks():
	existing = set()
	for channel in channels:
		for post in telepost.getPosts(channel, min_time=time.time() - 24 * 60 * 60 * DAYS):
			if not post.text:
				continue
			for item in post.text.find_all('a', href=True):
				if 'weibo.' in item['href']:
					link = item['href']
					if link not in existing:
						yield link
						existing.add(link)

def run():
	for link in getWeiboLinks():
		print(link)
		status = getJson(link)
		if not status:
			continue
		print(status)
		return # testing

if __name__ == '__main__':
	run()