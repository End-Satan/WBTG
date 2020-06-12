from telegram_util import matchKey

def getSingleCount(blog):
	try:
		return int(blog['reposts_count']) + int(blog['comments_count']) + int(blog['attitudes_count'])
	except:
		print(str(blog)[:100])
		return 0

def getCount(blog):
	if not blog:
		return 0
	count = getSingleCount(blog)
	if 'retweeted_status' in blog:
		blog = blog['retweeted_status']
		count += getSingleCount(blog) / 3
	return count

def shouldSend(db, card):
	if matchKey(str(card), db.blacklist.items):
		return False
	if matchKey(str(card), db.popularlist.items):
		return getCount(card.get('mblog')) > 1000
	return getCount(card.get('mblog')) > 100