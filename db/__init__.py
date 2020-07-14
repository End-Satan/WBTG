import plain_db
from telegram_util import isInt

class Subscription(object):
	def __init__(self):
		with open('db/subscription') as f:
			self.sub = yaml.load(f, Loader=yaml.FullLoader)

	def add(self, chat_id, text):
		if not text:
			return
		text = text.split('?')[0]
		user_id = text.strip('/').split('/')[-1]
		if isInt(user_id):
			text = user_id
		self.sub[chat_id] = self.sub.get(chat_id, []) + [text]
		self.save()

	def remove(self, chat_id, text):
		self.sub[chat_id] = self.sub.get(chat_id, [])
		try:
			self.sub[chat_id].remove(text)
		except:
			...
		self.save()

	def get(self, chat_id):
		return '当前订阅：' + ' '.join(self.sub.get(chat_id, []))

	def subscriptions(self):
		result = set()
		for chat_id in self.sub:
			for item in self.sub.get(chat_id, []):
				result.add(item)
		return result

	def _channels(self, bot, text):
		for chat_id in self.sub:
			if text in self.sub.get(chat_id, []):
				try:
					yield bot.get_chat(chat_id)
				except:
					...

	def channels(self, bot, text):
		return list(self._channels(bot, text))

	def save(self):
		with open('db/subscription', 'w') as f:
			f.write(yaml.dump(self.sub, sort_keys=True, indent=2, allow_unicode=True))

existing = plain_db.loadKeyOnlyDB('existing')
blacklist = plain_db.loadKeyOnlyDB('blacklist')
popularlist = plain_db.loadKeyOnlyDB('popularlist')
subscription = Subscription()