to_remove = [
	'1497705225',
	'1497705225',
	'1564756410',
	'1564756410',
	'1601316190',
	'1647850037',
	'1647850037',
	'1651908361',
	'1708735260',
	'1708735260',
	'1917036491',
	'1917036491',
	'2588011444',
	'2588011444',
	'34962',
	'3982803458',
	'3982803458',
	'4646012587868553',
	'4646012587868553',
	'4646396986392882',
	'4646396986392882',
	'4646405824315612',
	'4646409976676571',
	'4646409976676571',
	'5226408495',
	'5226408495',
	'5326908395',
	'5816275164',
	'5816275164',
	'6344730619',
	'6344730619',
	'6451185052',
	'6656022511',
	'6656022511',
	'6697728700',
	'7244454633',
	'7244454633',
	'7270922137',
	'7270922137',
	'7327753702',
	'7327753702',
	'7366621253',
	'7370838439',
	'7375461423',
	'7376766667',
	'7502816383',
	'7502816383',
	'7547765664',
	'7547765664',
	'7582786599',
	'7582786599',
	'@江卓尔_莱比特矿池',
	'@江卓尔_莱比特矿池',
	'digitalchatstation',
	'哎就是改着玩儿',
	'哎就是改着玩儿',
	'工具狂人ToolsMan']

from db import subscription

if __name__ == '__main__':
	for item in to_remove:
		subscription.remove_invalid(item)