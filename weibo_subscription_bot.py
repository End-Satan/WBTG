#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr, isInt, getChannelsLog
import album_sender
from db import subscription, existing, scheduled_key, log_existing
import threading
import weibo_2_album
from command import setupCommand
from common import debug_group, tele, logger
import weiboo
import random
from filter import passFilter
import time
import plain_db

def shouldProcess(channel, card, key):
	if not passFilter(channel, card, key):
		return False
	whash = weiboo.getHash(card) + str(channel.id)
	if not existing.add(whash):
		return False
	return True

def getResult(url, card, channels):
	result = weibo_2_album.get(url, card['mblog'])
	if '全文</a>' not in str(card['mblog']):
		return result
	full_result = weibo_2_album.get(url)
	if full_result.cap_html_v2:
		result.cap_html_v2 = full_result.cap_html_v2
	return result

@log_on_fail(debug_group)
def log(url, card, key, channels, sent):
	whash = weiboo.getHash(card)
	if not log_existing.add(whash):
		return
	additional_info = weibo_2_album.getAdditionalInfo(card['mblog'])
	if additional_info:
		additional_info += ' '
	message_1 = '%s <a href="%s">source</a>\n\nkey: %s channel_id: %s %s' % (
		weibo_2_album.getCap(card['mblog']), url,
		additional_info,
		key, ' '.join([str(channel.id) for channel in channels]), 
		getChannelsLog(channels))
	logger.send_message(message_1, parse_mode='html', disable_web_page_preview=(not additional_info))
	time.sleep(5)

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
		log(url, card, key, channels, result)

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

def backfill():
	process('5807402211', weiboo.backfill)
	process('1357494880', weiboo.backfill)

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher) 
	tele.start_polling()
	tele.idle()