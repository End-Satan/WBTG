from telegram_util import matchKey
from db import subscription, blacklist, popularlist
import weiboo

def shouldApplyFilter(channel_id, key)
	if isInt(key):
		return subscription.filterOnUser(channel_id):
	return subscription.filterOnKey(channel_id)

def passKeyFilter(card):
	if matchKey(str(card), popularlist.items):
		return weiboo.getCount(card) > 10000
	return weiboo.getCount(card) > 1000

def passMasterFilter(card):
	if matchKey(str(card), blacklist.items):
		return False
	return weiboo.getCount(card) > 300

def passFilter(channel, card, key):
	channel_id = channel.id
	if (subscription.hasMasterFilter(channel_id) and 
		not passMasterFilter(card)):
		return False
	if (shouldApplyFilter(channel_id, key) and 
		not passKeyFilter(card)):
		return False
	return True