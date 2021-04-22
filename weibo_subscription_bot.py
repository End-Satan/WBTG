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

def getResult(url, card, channels):
	if '全文</a>' not in str(card['mblog']):
		return weibo_2_album.get(url, card['mblog'])
	if set([channel.id for channel in channels]) & set([-1001374366482, -1001340272388, -1001427773894, -1001437951226]):
		return weibo_2_album.get(url)
	return weibo_2_album.get(url, card['mblog'])

def process(key, method=weiboo.search):
	channels = subscription.channels(tele.bot, key)
	try:
		search_result = method(key, force_cache=True)
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
			result_posts = []
			try:
				if not result:
					result = getResult(url, card, channels)
				result_posts = album_sender.send_v2(channel, result)
			except Exception as e:
				debug_group.send_message(getLogStr(channel.username, channel.id, url, e))
			finally:
				post_len = len(result_posts or [])
				time.sleep((post_len ** 2) / 2 + post_len * 10)

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

def test():
	process('7020024436', method=weiboo.backfill)

if __name__ == '__main__':
	threading.Timer(1, test).start() 
	setupCommand(tele.dispatcher) 
	tele.start_polling()
	tele.idle()