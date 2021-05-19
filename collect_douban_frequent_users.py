import telepost
from telegram_util import getWid, matchKey
import time
import cached_url
import yaml
import random
import plain_db
import os
from bs4 import BeautifulSoup

DAYS = 365
channels = [
	'daily_feminist',
	'freedom_watch',
	'queer_liberation',
	'life_with_disabilities',
	'labor_one']

freq_count = {}
name = {}

def process(item):
	try:
		uid = int(item.get('data-uid'))
	except:
		return
	name_block = item.find('a', href=True, title=True)
	freq_count[uid] = freq_count.get(uid, 0) + 1
	name[uid] = name_block['title']

def getSoup(link):
	if not os.path.exists(cached_url.getFilePath(link)):
		return
	return BeautifulSoup(cached_url.get(link, sleep=1), 'html.parser')

def getDoubanLinks():
	existing = set()
	for channel in channels:
		for post in telepost.getPosts(channel, min_time=time.time() - 24 * 60 * 60 * DAYS):
			if not post.text:
				continue
			for item in post.text.find_all('a', href=True):
				if 'douban.' in item['href']:
					link = item['href']
					if link not in existing:
						yield link
						existing.add(link)

def run():
	process_count = 0
	for link in getDoubanLinks():
		soup = getSoup(link)
		if not soup:
			continue
		items = list(soup.find_all('div', class_='status-item'))
		for item in items:
			process(item)
		process_count += 1
		if process_count % 100 == 0:
			print('process_count:', process_count)
	count = [(item[1], item[0]) for item in freq_count.items()]
	count.sort(reverse=True)
	print(count)
	ids = [item[1] for item in count if item[0] > 2]
	for user_id in ids:
		print('【%s】\nhttps://www.douban.com/people/%d\n' % (name.get(user_id), user_id))

if __name__ == '__main__':
	run()