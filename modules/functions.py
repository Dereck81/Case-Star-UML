#!/usr/bin/python
#

'''
try:
	import __builtin__ as builtins
except ImportError:
	import builtins
'''
from colorama import init, Fore, Style
from datetime import datetime
import builtins

init(autoreset = True)

def print(text: object, mode: int = 1, state: int = 1, **kwargs) -> None:
	'''
	-----------------------
	mode: 1 -> normal
	mode: 2 -> datetime
	-----------------------
	state: 1 -> Information
	state: 2 -> Error
	state: 3 -> Warning
	state: 4 -> Correct
	-----------------------
	'''

	datetime_ = datetime.now().strftime('%H:%M:%S')

	if(state == 2):
		color = Fore.RED
	elif(state == 3):
		color = Fore.YELLOW
	elif(state == 4):
		color = Fore.GREEN
	else:
		color = Fore.WHITE

	if(mode == 1):
		builtins.print(f"{color}{text} {Style.RESET_ALL}", end='')
		builtins.print(**kwargs)
	elif(mode == 2):
		builtins.print(f"{Fore.LIGHTBLACK_EX}[{Fore.CYAN}{datetime_}{Fore.LIGHTBLACK_EX}] {color}{text}{Style.RESET_ALL}", end='')
		builtins.print(**kwargs)

def _deletekeys(dict_: dict, keysD: list = None) -> dict:
	#keysDelete: list = ["_type", "_parent", "documentation"]
	keysDelete: list = ["_type", "documentation"]

	if not keysD is None:
		keysDelete = keysD

	for keysDel in keysDelete:
		try:
			dict_.pop(keysDel)
		except KeyError:
			continue
	return dict_
