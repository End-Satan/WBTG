import plain_db
from telegram_util import isInt
import yaml

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
				if 'filter' not in item:
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

	# by default, we don't do filter
	def filterOnUser(self, chat_id):
		return 'filter_on_user' in self.sub.get(chat_id, [])

	# by default, we do filter
	def filterOnKey(self, chat_id):
		return 'no_filter_on_key' not in self.sub.get(chat_id, [])

	def hasMasterFilter(self, chat_id):
		return 'has_master_filter' in self.sub.get(chat_id, [])

	def save(self):
		with open('db/subscription', 'w') as f:
			f.write(yaml.dump(self.sub, sort_keys=True, indent=2, allow_unicode=True))

existing = plain_db.loadKeyOnlyDB('existing')
blocklist = plain_db.loadKeyOnlyDB('blocklist')
popularlist = plain_db.loadKeyOnlyDB('popularlist')
subscription = Subscription()