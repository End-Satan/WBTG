from telegram.ext import MessageHandler, Filters
from telegram_util import log_on_fail, splitCommand, commitRepo, tryDelete, autoDestroy
from common import debug_group
from db import subscription, blocklist, popularlist, scheduled_key

core_channels_ids = set([-1001496977825, -1001374366482, -1001340272388, -1001326932731, -1001598520359])

@log_on_fail(debug_group)
def handleAdmin(msg):
	if msg.chat.id not in core_channels_ids:
		return
	command, text = splitCommand(msg.text)
	if not text:
		return
	success = False
	if command == '/abl' and len(text) > 1:
		blocklist.add(text)
		success = True
	if command == '/apl':
		popularlist.add(text)
		success = True
	if success:
		autoDestroy(msg.reply_text('success'), 0.1)
		tryDelete(msg)
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
		result = subscription.remove(msg.chat_id, text)
		try:
			scheduled_key.remove(result)
		except:
			...
	elif 'sub' in command:
		result = subscription.add(msg.chat_id, text)
		scheduled_key.append(result)
	reply = msg.reply_text(subscription.get(msg.chat_id), 
		parse_mode='markdown', disable_web_page_preview=True)
	if msg.chat_id < 0:
		tryDelete(msg)
	if 'sub' in command:
		commitRepo(delay_minute=0)
		if msg.chat_id < 0:
			autoDestroy(reply, 0.1)

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