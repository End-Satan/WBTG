#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr, isInt, getChannelsLog, matchKey
import album_sender
from db import subscription, existing, scheduled_key, log_existing, keywords, blocklist, mutual_add_existing, popularlist
import threading
import weibo_2_album
from command import setupCommand, core_channels_ids
from common import debug_group, tele, logger
import weiboo
import random
from filter import passFilter, shouldProcessResult, shouldSendMutalHelp, passBasicFilter
import time

auto_collect_channel_id = -1001598520359
mutual_help_channel = tele.bot.get_chat(-1001570955777)

def shouldProcess(channel, card, key):
	if not passFilter(channel, card, key):
		return False
	whash = weiboo.getHash(card) + str(channel.id)
	if not existing.add(whash):
		return False
	return True

def getResult(url, card):
	result = weibo_2_album.get(url, card['mblog'])
	if '全文</a>' not in str(card['mblog']):
		return result
	full_result = weibo_2_album.get(url)
	if full_result.cap_html_v2:
		result.cap_html_v2 = full_result.cap_html_v2
	return result

def tryExtendSubscription(key, channels, card):
	if not isInt(key):
		return
	core_card = card.get('mblog', {}).get('retweeted_status')
	if not core_card:
		return
	if matchKey(str(card), blocklist.items()):
		return
	if matchKey(str(card), popularlist.items()):
		return
	if not (set([channel.id for channel in channels]) & 
		(core_channels_ids - set([auto_collect_channel_id]))):
		return 
	user_id = (core_card.get('user') or {}).get('id')
	if not user_id:
		return
	for chat_id in core_channels_ids:
		if str(user_id) in subscription.sub.get(chat_id, []):
			return
	subscription.sub[auto_collect_channel_id].append(str(user_id))
	scheduled_key.append(str(user_id))

def trySend(channel, url, card, sent_channels, result):
	try:
		if not result:
			result.append(getResult(url, card))
		if not shouldProcessResult(channel, result[0]):
			return
		album_sender.send_v2(channel, result[0])
		sent_channels.append(channel)
	except Exception as e:
		debug_group.send_message(getLogStr(channel.username, channel.id, url, e))

@log_on_fail(debug_group)
def sendMutualhelp(url, card, sent_channels, result):
	if not shouldSendMutalHelp(card):
		return
	whash = ''.join(weibo_2_album.getCap(card['mblog'])[:20].split())
	if not mutual_add_existing.add(whash):
		return
	trySend(mutual_help_channel, url, card, sent_channels, result)

@log_on_fail(debug_group)
def log(url, card, key, channels, sent):
	if weiboo.getCount(card) < 40:
		return
	whash = weiboo.getHash(card)
	if not log_existing.add(whash):
		return
	tryExtendSubscription(key, channels, card)
	additional_info = weibo_2_album.getAdditionalInfo(card['mblog'])
	if additional_info:
		additional_info += ' '
	disable_web_page_preview = not matchKey(additional_info, ['imgs:', 'video:'])
	if set([channel.id for channel in channels]) & core_channels_ids:
		mark = ''
	else:
		mark = ' weibo_channel_ignore'
	if set([channel.id for channel in sent]) & core_channels_ids:
		sent = ' weibo_bot_sent' # means sent to core channel
	else:
		sent = ''
	if not isInt(key):
		mark += ' weibo_string_key_ignore'
	message = '%s\n\n%skey: %s channel_id: %s %s%s%s %s <a href="%s">source</a>' % (
		weibo_2_album.getCap(card['mblog']),
		additional_info,
		key, ' '.join([str(channel.id) for channel in channels]), 
		getChannelsLog(channels), sent, mark, url, url)
	try:
		logger.send_message(message, parse_mode='html', disable_web_page_preview=disable_web_page_preview)
	except Exception as e:
		print('log failed', str(e), message)
	time.sleep(5)	

def process(key, method=weiboo.search):
	channels = subscription.channels(tele.bot, key)
	try:
		search_result = method(key, ttl = 5 * 50 * 60)
	except Exception as e:
		print('search failed', key, str(e))
		return
	if not search_result:
		print('no search result', key)
		return
	for url, card in search_result:
		result = []
		sent_channels = []
		for channel in channels:
			if not shouldProcess(channel, card, key):
				continue
			trySend(channel, url, card, sent_channels, result)
		sendMutualhelp(url, card, sent_channels, result)
		log(url, card, key, channels, sent_channels)

@log_on_fail(debug_group)
def loopImp():
	if not scheduled_key:
		for key in subscription.subscriptions():
			scheduled_key.append(key)
		random.shuffle(scheduled_key)
	process(scheduled_key.pop())
		
def loop():
	loopImp()
	threading.Timer(1, loop).start() 

def backfill():
	process('5402666134', weiboo.backfill)
	print('backfill finish')
	loop()

if __name__ == '__main__':
	subscription.sub[auto_collect_channel_id] = ['noSendFilter']
	threading.Timer(1, loop).start() 
	# threading.Timer(1, backfill).start() 
	setupCommand(tele.dispatcher) 
	tele.start_polling()
	tele.idle()