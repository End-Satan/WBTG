from db import subscription
from command import core_channels_ids

def oneTimeCleanSubscriber():
	for chat_id in list(subscription.sub.keys()):
		try:
			r = tele.bot.send_message(chat_id, 'test')
			r.delete()
		except:
			del subscription.sub[chat_id]
	subscription.save()

def removeNoResult():
	items = {}
	with open('tmp_no_result') as f:
		for line in f:
			item = line.strip()
			items[item] = items.get(item, 0) + 1
	for item, count in items.items():
		if count < 3:
			continue
		for chat_id in subscription.sub:
			if chat_id in core_channels_ids:
				continue
			if sum(['ilter' in key for key in subscription.sub.get(chat_id, [])]):
				continue
			if item in subscription.sub.get(chat_id, []):
				subscription.sub[chat_id].remove(item)
	subscription.save()
				
if __name__ == '__main__':
	removeNoResult()