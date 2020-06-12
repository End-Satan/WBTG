#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey, clearUrl, log_on_fail, removeOldFiles, commitRepo, splitCommand
import sys
from telegram.ext import Updater, MessageHandler, Filters
import yaml
import album_sender
from soup_get import SoupGet, Timer
from db import DB
import threading
import weibo_2_album
import urllib

with open('credential') as f:
	credential = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(credential['bot'], use_context=True)  # @weibo_subscription_bot
debug_group = tele.bot.get_chat(420074357)

HELP_MESSAGE = '''
本bot负责订阅微博信息。

可用命令：
/wb_subscribe 用户ID/关键词/用户链接 - 订阅
/wb_unsubscribe 用户ID/关键词/用户链接 - 取消订阅
/wb_view - 查看当前订阅

本bot在群组/频道中亦可使用。

Github： https://github.com/gaoyunzhi/weibo_subscription_bot
'''

sg = SoupGet()
db = DB()
timer = Timer()
cache = {}

# def getSingleCount(blog):
# 	try:
# 		return int(blog['reposts_count']) + int(blog['comments_count']) + int(blog['attitudes_count'])
# 	except:
# 		print(str(blog)[:100])
# 		return 0

# def getCount(blog):
# 	if not blog:
# 		return 0
# 	count = getSingleCount(blog)
# 	if 'retweeted_status' in blog:
# 		blog = blog['retweeted_status']
# 		count += getSingleCount(blog) / 3
# 	return count

# def shouldSend(card):
# 	if matchKey(str(card), db.whitelist.items):
# 		return True
# 	if matchKey(str(card), db.blacklist.items):
# 		return False
# 	if matchKey(str(card), db.preferlist.items):
# 		return getCount(card.get('mblog')) > 300
# 	if matchKey(str(card), db.popularlist.items):
# 		return getCount(card.get('mblog')) > 10000
# 	return getCount(card.get('mblog')) > 1000

# def processCard(card):
# 	if not shouldSend(card):
# 		return
# 	url = clearUrl(card['scheme'])
# 	if url in db.existing.items:
# 		return

# 	r = weibo_2_album.get(url)
# 	print('hash', r.hash)
# 	if (str(r.wid) in db.existing.items or str(r.rwid) in db.existing.items or 
# 		str(r.hash) in db.existing.items):
# 		return

# 	print('sending', url, r.wid, r.rwid)
# 	timer.wait(10)

# 	cache[r.hash] = cache.get(r.hash, 0) + 1
# 	if cache[r.hash] > 2:
# 		# for whatever reason, this url does not send to telegram, skip
# 		db.existing.add(r.hash)

# 	album_sender.send(channel, url, r)
	
# 	db.existing.add(url)
# 	db.existing.add(r.wid)
# 	db.existing.add(r.rwid)
# 	db.existing.add(r.hash)
	
def process(url):
	content = sg.getContent(url)
	content = yaml.load(content, Loader=yaml.FullLoader)
	try:
		content['data']['cards']
	except:
		return # url read fail, may due to rate limiting
	for card in content['data']['cards']:
		try:
			card['scheme']
		except:
			continue
		url = clearUrl(card['scheme'])
		print(url, card) # see if we can calculate hash based on card
		

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1)
	sg.reset()
	db.reload()
	for keyword in db.subscription.keywords():
		content_id = urllib.request.pathname2url('100103type=1&q=' + keyword)
		url = 'https://m.weibo.cn/api/container/getIndex?containerid=%s&page_type=searchall' % content_id
		process(url)
	for user in db.subscription.users():
		url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s' \
			% (user, user)
		process(url)
	commitRepo(delay_minute=0)

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

@log_on_fail(debug_group)
def handleCommand(update, context):
	msg = update.message
	if not msg or not msg.text.startswith('/wb'):
		return
	command, text = splitCommand(msg.text)
	if 'unsub' in command:
		db.subscription.remove(msg.chat_id, text)
	elif 'sub' in command:
		db.subscription.add(msg.chat_id, text)
	msg.reply_text(db.subscription.get(msg.chat_id))

def handleHelp(update, context):
	update.message.reply_text(HELP_MESSAGE)

def handleStart(update, context):
	if 'start' in update.message.text:
		update.message.reply_text(HELP_MESSAGE)

if __name__ == '__main__':
	loop()
	dp = tele.dispatcher
	dp.add_handler(MessageHandler(Filters.command, handleCommand))
	dp.add_handler(MessageHandler(Filters.private & (~Filters.command), handleHelp))
	dp.add_handler(MessageHandler(Filters.private & Filters.command, handleStart), group=2)
	tele.start_polling()
	tele.idle()