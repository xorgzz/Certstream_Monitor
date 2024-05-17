#!/usr/bin/python3

import subprocess
import sys
import os
import threading
import utils
from utils import log, err, clear, red, green, yellow, magenta, cyan, white

libs_required = ["certstream", "sqlite3", "Flask"]

def start_web_server():
	slash = "/" if os.name == "posix" else "\\"
	with open(os.devnull, "w") as devnull:
		subprocess.check_call([sys.executable, f"{os.path.dirname(os.path.abspath(__file__))}{slash}web_server.py"], stdout=devnull, stderr=subprocess.STDOUT)

def install_libs():
	global libs_required
	for lib in libs_required:
		try :
			__import__(lib)
			pass
		except:
			log(f"Instalacja brakującej biblioteki - {lib}...")
			subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--break-system-packages", "--no-warn-script-location"])

if __name__ == "__main__":
	clear()
	install_libs()
	try:
		slash = "/" if os.name == "posix" else "\\"
		if len(sys.argv) == 2:
			if not os.path.isfile(sys.argv[1]):
				clear()
				err("\nPlik z filtrami nie istnieje !!\n")
				sys.exit()
			web_server = threading.Thread(target=start_web_server)
			web_server.start()
			subprocess.check_call([sys.executable, f"{os.path.dirname(os.path.abspath(__file__))}{slash}app.py", sys.argv[1]])
		elif len(sys.argv) == 3:
			if not (sys.argv[2] == "--debug" or sys.argv[2] == "-d"):
				clear()
				err("\nPoprawne użycie programu:\n$ python3 run.py (plik ze słowani klucz)\n")
				sys.exit()
			if not os.path.isfile(sys.argv[1]):
				clear()
				err("\nPlik z filtrami nie istnieje !!\n")
				sys.exit()
			web_server = threading.Thread(target=start_web_server)
			web_server.start()
			subprocess.check_call([sys.executable, f"{os.path.dirname(os.path.abspath(__file__))}{slash}app.py", sys.argv[1], sys.argv[2]])
		else:
			clear()
			err("\nZła liczba argumentów\n")
			sys.exit()
	except KeyboardInterrupt:
		log("\nWyjście z programu\n", magenta)
		sys.exit()
