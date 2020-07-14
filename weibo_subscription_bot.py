#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import clearUrl, log_on_fail, removeOldFiles, commitRepo, splitCommand
import yaml
import album_sender
from db import db
import threading
import weibo_2_album
import urllib
from util import shouldSend
from command import setupCommand
from common import debug_group, credential
	
def getResults(url):
	content = cached_url.get(url, 
			headers = {'cookie': credential['cookie']}, sleep = 30)
	content = yaml.load(content, Loader=yaml.FullLoader)
	for card in content['data']['cards']:
		if 'scheme' not in card:
			continue
		if 'type=uid' not in url and not shouldSend(db, card):
			continue
		print(card['scheme'])
		result = weibo_2_album.get(clearUrl(card['scheme']))
		if not db.existing.add(result.hash):
			continue
		yield result

def process(url, key):
	channels = db.subscription.channels(tele.bot, key)
	for item in getResults(url):
		for channel in channels:
			try:
				album_sender.send_v2(channel, item)
			except Exception as e:
				debug_group.send_message((channel.first_name or channel.title) 
					+ ' ' + item.url + ' ' + str(e))

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1) # video could be very large
	db.reload()
	for keyword in db.subscription.keywords():
		content_id = urllib.request.pathname2url('100103type=1&q=' + keyword)
		url = 'https://m.weibo.cn/api/container/getIndex?containerid=%s&page_type=searchall' % content_id
		process(url, keyword)
	for user in db.subscription.users():
		url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s' \
			% (user, user)
		process(url, user)
	commitRepo(delay_minute=0)

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()