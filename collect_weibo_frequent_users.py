import telepost
from telegram_util import getWid, matchKey
import time
import cached_url
import yaml
import random
import plain_db
import os

blocklist = plain_db.loadKeyOnlyDB('blocklist')

DAYS = 365
channels = [
	'daily_feminist',
	'freedom_watch',
	'queer_liberation',
	'life_with_disabilities',
	'labor_one']

freq_count = {}
name = {}
description = {}

def process(status):
	user = status.get('user')
	if not user:
		return
	user_id = user.get('id')
	if not user_id:
		return
	name[user_id] = user.get('screen_name')
	description[user_id] = user.get('description').encode('utf-16', 'surrogatepass').decode('utf-16')
	freq_count[user_id] = freq_count.get(user_id, 0) + 1

wb_prefix = 'https://m.weibo.cn/statuses/show?id='
def getJson(link):
	wid = getWid(link)
	url = wb_prefix + wid
	if not os.path.exists(cached_url.getFilePath(url)):
		return {}
	try:
		json = yaml.load(cached_url.get(wb_prefix + wid, force_cache=True, sleep=5), Loader=yaml.FullLoader)
		json['data']['user']
		return json['data']
	except:
		print('fetch failed: ' + link)
		return {}

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
	process_count = 0
	for link in getWeiboLinks():
		status = getJson(link)
		if matchKey(str(status), blocklist.items()):
			continue
		process(status)
		process(status.get('retweeted_status', {}))
		process_count += 1
		if process_count % 100 == 0:
			print('process_count:', process_count)
	count = [(item[1], item[0]) for item in freq_count.items()]
	count.sort(reverse=True)
	print(count)
	ids = [item[1] for item in count if item[0] > 2]
	for user_id in ids:
		print('【%s】\n%s\nhttps://m.weibo.cn/u/%d\n' % (name.get(user_id), description.get(user_id), user_id))

if __name__ == '__main__':
	run()