import os
import yaml
import threading
import time

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
			return
		self.items.add(x)
		with open(self.fn, 'a') as f:
			f.write('\n' + x)

	def contains(self, x):
		x = str(x).strip()
		return x in self.items

class Subscription(object):
	def __init__(self):
		with open('db/subscription') as f:
			self.subscription = yaml.load(f, Loader=yaml.FullLoader)

	def add(self, chat_id, text):
		pass

	def remove(self, chat_id, text):
		...

	def get(self, chat_id):
		...

	def keywords(self):
		...

	def users(self):
		...

	def channels(self, text):
		...

class DB(object):
	def __init__(self):
		self.reload()

	def reload(self):
		self.existing = DBItem('existing')
		self.blacklist = DBItem('blacklist')
		self.popularlist = DBItem('popularlist')
		self.subscription = Subscription()
