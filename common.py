import yaml
from telegram.ext import Updater

with open('credential') as f:
	credential = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(credential['bot'], use_context=True)  # @weibo_subscription_bot
debug_group = tele.bot.get_chat(420074357)