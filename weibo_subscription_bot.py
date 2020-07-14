#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr
import album_sender
from db import subscription, existing
import threading
import weibo_2_album
from command import setupCommand
from common import debug_group, tele
import weiboo
import random
from filter import passFilter

processed_channels = set()

def shouldProcess(channel, card, key):
	if channel.id in processed_channels:
		return False
	if not passFilter(channel, card, key):
		return False
	whash = weiboo.getHash(card) + str(channel.id)
	if not existing.add(whash):
		return False
	processed_channels.add(channel.id)
	return True

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
			print(url, channel.id, channel.username)
			if not result:
				result = weibo_2_album.get(url, card.get('mblog'))
			try:
				album_sender.send_v2(channel, result)
			except Exception as e:
				debug_group.send_message(getLogStr(channel.username, channel.id, url, e))
				raise e

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1) # video could be very large
	global processed_channels 
	processed_channels = set()
	for key in subscription.subscriptions():
		if random.random() > 0.1:
			continue
		process(key)

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

def oneTimeCleanSubscriber():
	for chat_id in list(subscription.sub.keys()):
		try:
			r = tele.bot.send_message(chat_id, 'test')
			r.delete()
		except:
			del subscription.sub[chat_id]
	subscription.save()

if __name__ == '__main__':
	oneTimeCleanSubscriber()
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()