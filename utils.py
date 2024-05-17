#!/usr/bin/python3

import os

red = "\033[0;31m"
green = "\033[0;32m"
yellow = "\033[0;33m"
blue = "\033[0;34m"
magenta = "\033[0;35m"
cyan = "\033[0;36m"
white = "\033[0;37m"

def clear():
	if os.name == "posix":
		os.system("clear")
	elif os.name == "nt":
		os.system("cls")

def log(log_message, color=green):
	print(color, end="")
	print(log_message, end="")
	print(white)

def err(error_message):
	log(error_message, red)