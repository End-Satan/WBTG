from telegram_util import matchKey, isInt, clearUrl
from db import subscription, blocklist, popularlist
import weiboo

def shouldApplyFilter(channel_id, key):
	if isInt(key):
		return subscription.filterOnUser(channel_id)
	return subscription.filterOnKey(channel_id)

def passKeyFilter(card):
	# if matchKey(str(card), ['5807402211', '1357494880']): # testing
	# 	return True
	if matchKey(str(card), popularlist.items()):
		return weiboo.getCount(card) > 10000
	return weiboo.getCount(card) > 1000

def passMasterFilter(card):
	if weiboo.getCount(card) < 300:
		return False
	for item in blocklist.items():
		if item in str(card):
			return False
	return True

def passBasicFilter(result):
	if result.imgs or result.video:
		return True
	return len(result.cap_html_v2) > 20

def shouldProcessResult(channel, result):
	if subscription.hasVideoOnlyFiler(channel.id):
		return result.video
	if not subscription.hasBasicFilter(channel.id):
		return True
	return passBasicFilter(result)

# def tooOld(card):
# 	created_at = card['mblog']['created_at']
# 	if len(created_at) != 5:
# 		return False
# 	return created_at <= '2-15' # repository move date

def passFilter(channel, card, key):
	channel_id = channel.id
	if subscription.hasNoSendFilter(channel_id): # random_weibo
		return False
	if (shouldApplyFilter(channel_id, key) and 
		not passKeyFilter(card)):
		return False
	if (subscription.hasMasterFilter(channel_id) and 
		not passMasterFilter(card)):
		return False
	return True