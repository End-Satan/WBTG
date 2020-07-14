from telegram.ext import MessageHandler, Filters
from telegram_util import log_on_fail, splitCommand, commitRepo
from common import debug_group
from db import subscription, blocklist, popularlist

@log_on_fail(debug_group)
def handleAdmin(msg):
	if not msg.from_user or msg.from_user.id != debug_group.id:
		return
	command, text = splitCommand(msg.text)
	if not text:
		return
	success = False
	if command == '/abl':
		blocklist.add(text)
		success = True
	if command == '/apl':
		popularlist.add(text)
		success = True
	if success:
		msg.reply_text('succss')
		commitRepo(delay_minute=0)

@log_on_fail(debug_group)
def handleCommand(update, context):
	msg = update.effective_message
	if not msg:
		return
	handleAdmin(msg)
	if not msg.text.startswith('/wb'):
		return
	command, text = splitCommand(msg.text)
	if 'unsub' in command:
		subscription.remove(msg.chat_id, text)
	elif 'sub' in command:
		subscription.add(msg.chat_id, text)
	msg.reply_text(subscription.get(msg.chat_id))
	if 'sub' in command:
		commitRepo(delay_minute=0)

with open('help.md') as f:
	HELP_MESSAGE = f.read()

def handleHelp(update, context):
	update.message.reply_text(HELP_MESSAGE)

def handleStart(update, context):
	if 'start' in update.message.text:
		update.message.reply_text(HELP_MESSAGE)

def setupCommand(dp):
	dp.add_handler(MessageHandler(Filters.command, handleCommand))
	dp.add_handler(MessageHandler(Filters.private & (~Filters.command), handleHelp))
	dp.add_handler(MessageHandler(Filters.private & Filters.command, handleStart), group=2)