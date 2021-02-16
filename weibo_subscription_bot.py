#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr, isInt
import album_sender
from db import subscription, existing, scheduled_key
import threading
import weibo_2_album
from command import setupCommand
from common import debug_group, tele
import weiboo
import random
from filter import passFilter
import time

def shouldProcess(channel, card, key):
	if not passFilter(channel, card, key):
		return False
	whash = weiboo.getHash(card) + str(channel.id)
	if not existing.add(whash):
		return False
	return True

# a hack, we can fetch the single item again, but weibo will 
# be unhappy about the frequent calls
def removeSeeMore(result): 
	pivot = '[全文](/status/'
	result.cap = result.cap.split(pivot)[0]
	if result.cap.endswith('...') or result.cap.endswith('的微博视频'):
		total_len = len(result.cap)
		last_period_index = max(result.cap.rfind('。'), result.cap.rfind('？'))
		if last_period_index > max(total_len / 2, total_len - 80):
			result.cap = result.cap[:last_period_index + 1]

def getResult(url, card, channels):
	if '全文</a>' not in str(card['mblog']):
		return weibo_2_album.get(url, card['mblog'])
	if set([channel.id for channel in channels]) & set([-1001374366482, -1001340272388]):
		print('fetching full', url)
		return weibo_2_album.get(url)
	result = weibo_2_album.get(url, card['mblog'])
	removeSeeMore(result)
	return result

def process(key):
	channels = subscription.channels(tele.bot, key)
	try:
		search_result = weiboo.search(key, force_cache=True)
	except Exception as e:
		print('search failed', key, str(e))
		return
	if not search_result:
		print('no search result', key)
		return
	for url, card in search_result:
		result = None
		for channel in channels:
			if not shouldProcess(channel, card, key):
				continue
			try:
				if not result:
					result = getResult(url, card, channels)
				print(url, result.cap[:50].replace('\n', ' '))
				with open('tmp_mblog', 'a') as f:
					f.write(str(card['mblog']) + '\n\n')
				# album_sender.send_v2(channel, result)
			except Exception as e:
				debug_group.send_message(getLogStr(channel.username, channel.id, url, e))
			finally:
				...
				# time.sleep(120)

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1)
	if not scheduled_key:
		for key in subscription.subscriptions():
			scheduled_key.append(key)
		random.shuffle(scheduled_key)
	process(scheduled_key.pop())
		
def loop():
	loopImp()
	threading.Timer(30, loop).start() 
	# threading.Timer(60 * 2, loop).start() 

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()