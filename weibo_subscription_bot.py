#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles
import album_sender
from db import db
import threading
import weibo_2_album
from util import shouldSend
from command import setupCommand
from common import debug_group, tele
import weiboo

def process(key):
	channels = db.subscription.channels(key)
	for url, card in weiboo.search(key):
		result = None
		for channel in channels:
			whash = weiboo.getHash(card) + str(channel.id)
			if not db.existing.add(whash):
				continue
			if not result:
				result = weibo_2_album.get(url, card.get('mblog'))
			album_sender.send_v2(channel, result)

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1) # video could be very large
	for key in db.subscription.subscriptions():
		if random.random() > 0.1:
			continue
		process(key)

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()