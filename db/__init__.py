import os
import yaml
import threading
import time
from telegram_util import commitRepo
import uuid

def getFile(name):
	fn = 'db/' + name
	os.system('touch ' + fn)
	with open(fn) as f:
		return set([x.strip() for x in f.readlines() if x.strip()])

class DBItem(object):
	def __init__(self, name):
		self.items = getFile(name)
		self.fn = 'db/' + name

	def add(self, x):
		x = str(x).strip()
		if not x or x in self.items:
			return False
		self.items.add(x)
		with open(self.fn, 'a') as f:
			f.write('\n' + x)
		return True

class Subscription(object):
	def __init__(self):
		with open('db/subscription') as f:
			self.sub = yaml.load(f, Loader=yaml.FullLoader)

	def add(self, chat_id, text):
		if not text:
			return
		try:
			user_id = text.strip('/').split('/')[-1]
			int(user_id)
			text = user_id
		except:
			...
		self.sub[chat_id] = self.sub.get(chat_id, []) + [text]
		self.save()

	def remove(self, chat_id, text):
		self.sub[chat_id] = self.sub.get(chat_id, [])
		try:
			self.sub[chat_id].remove(text)
		except:
			...

	def get(self, chat_id):
		return '当前订阅：' + ' '.join(self.sub.get(chat_id, []))

	def subscriptions(self):
		result = set()
		for chat_id in self.sub:
			for item in self.sub.get(chat_id, []):
				result.add(item)
		return result

	def keywords(self):
		for item in self.subscriptions():
			try:
				int(item)
			except:
				yield item

	def users(self):
		for item in self.subscriptions():
			try:
				int(item)
				yield item
			except:
				...

	def channels(self, bot, text):
		for chat_id in self.sub:
			if text in self.sub.get(chat_id, []):
				try:
					yield bot.get_chat(chat_id)
				except:
					...

	def save(self):
		with open('db/subscription', 'w') as f:
			f.write(yaml.dump(self.sub, sort_keys=True, indent=2, allow_unicode=True))
		commitRepo(delay_minute=0)

class Existing(object):
	def __init__(self):
		fn = 'existing_' + uuid.getnode()
		self.current = DBItem(fn)
		for fn in os.listdir('db'):self.all

class DB(object):
	def __init__(self):
		self.reload()

	def reload(self):
		self.existing = Existing()
		self.blacklist = DBItem('blacklist')
		self.popularlist = DBItem('popularlist')
		self.subscription = Subscription()
