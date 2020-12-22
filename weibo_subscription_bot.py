#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr, isInt
import album_sender
from db import subscription, existing
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

def process(key):
	channels = subscription.channels(tele.bot, key)
	search_result = weiboo.search(key, force_cache=True)
	if not search_result:
		print('no search result', key)
	for url, card in search_result:
		result = None
		for channel in channels:
			if not shouldProcess(channel, card, key):
				continue
			try:
				if not result:
					result = weibo_2_album.get(url, card['mblog'])
					removeSeeMore(result)
				album_sender.send_v2(channel, result)
			except Exception as e:
				debug_group.send_message(getLogStr(channel.username, channel.id, url, e))
				return
		if result:
			return

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1) # video could be very large
	for key in subscription.subscriptions():
		if random.random() > 0.01:
			continue
		process(key)
		return

def loop():
	loopImp()
	threading.Timer(60 * 2, loop).start() 

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()