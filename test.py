from db import subscription

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
		print(item)

if __name__ == '__main__':
	removeNoResult()