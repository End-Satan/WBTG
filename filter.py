from telegram_util import matchKey, isInt, clearUrl
from db import subscription, blocklist, popularlist
import weiboo

def shouldApplyFilter(channel_id, key):
	if isInt(key):
		return subscription.filterOnUser(channel_id)
	return subscription.filterOnKey(channel_id)

def passKeyFilter(card):
	if matchKey(str(card), popularlist.items()):
		return weiboo.getCount(card) > 10000
	return weiboo.getCount(card) > 1000

def passMasterFilter(card):
	if weiboo.getCount(card) < 300:
		return False
	for item in blocklist.items():
		if item in str(card):
			print('wb_blocked', clearUrl(card.get('scheme')), item)
			return False
	return True

def tooOld(card):
	created_at = card['mblog']['created_at']
	if len(created_at) != 5:
		return False
	return created_at <= '2-15' # repository move date

def passFilter(channel, card, key):
	channel_id = channel.id
	if (shouldApplyFilter(channel_id, key) and 
		not passKeyFilter(card)):
		return False
	if (subscription.hasMasterFilter(channel_id) and 
		not passMasterFilter(card)):
		return False
	return True