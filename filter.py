from telegram_util import matchKey, isInt, clearUrl
from db import subscription, blocklist, popularlist
import weiboo

def shouldApplyFilter(channel_id, key):
	if isInt(key):
		return subscription.filterOnUser(channel_id)
	return subscription.filterOnKey(channel_id)

def passKeyFilter(card):
	if matchKey(str(card), ['5776930791']):
		return True
	if matchKey(str(card), popularlist.items()):
		return weiboo.getCount(card) > 10000
	return weiboo.getCount(card) > 1000

def passMasterFilter(card):
	if ((not matchKey(str(card), ['5776930791'])) and 
		weiboo.getCount(card) < 300):
		return False
	# TODO: change this to matchKey
	for item in blocklist.items():
		if item in str(card):
			return False
	return True

MUTUAL_HELP_KEYS = ['互助', '求助', '帮帮', '救援', '求救']

def shouldSendMutalHelp(card):
	if weiboo.getCount(card) < 10:
		return False
	if matchKey(str(card), blocklist.items()):
		return False
	if matchKey(str(card), popularlist.items()):
		return False
	if matchKey(str(card), MUTUAL_HELP_KEYS):
		return True
	return False

def passBasicFilter(result):
	if result.imgs or result.video:
		return True
	return len(result.cap_html_v2) > 40

def shouldProcessResult(channel, result):
	if subscription.hasVideoOnlyFiler(channel.id):
		return result.video
	if subscription.hasMutualHelpFilter(channel.id):
		if not matchKey(result.cap_html_v2, MUTUAL_HELP_KEYS):
			return False
	if not subscription.hasBasicFilter(channel.id):
		return True
	return passBasicFilter(result)

def passBasicKeyFilter(card):
	if matchKey(str(card), blocklist.items()):
		return False
	if matchKey(str(card), popularlist.items()):
		return False
	return True

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
	if not isInt(key) and subscription.hasBasicKeyFilter(channel_id):
		return passBasicKeyFilter(card)
	return True