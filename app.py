#!/usr/bin/python3

import os
import sys
import datetime
import threading
import sqlite3
import json
import certstream
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import utils
from utils import log, err, clear, red, green, yellow, magenta, cyan, white

key_words = list()
debug_mode = False
email_data = dict()
slash = "/" if os.name == "posix" else "\\"
db_name = f"{os.path.dirname(os.path.abspath(__file__))}{slash}logs.db"

def init():
	global debug_mode
	global email_data
	if len(sys.argv) == 3:
		if not (sys.argv[2] == "--debug" or sys.argv[2] == "-d"):
			err("\nPoprawne użycie programu:\n$ python3 run.py (plik ze słowani klucz)\n")
			return
		debug_mode = True
	elif len(sys.argv) != 2:
		err("\nPoprawne użycie programu:\n$ python3 run.py (plik ze słowani klucz)\n")
		return
	
	clear()

	if not os.path.isfile(sys.argv[1]):
		err(f"\nPlik \"{sys.argv[1]}\" nie istnieje !!\n")
		return

	if not debug_mode:
		if not os.path.isfile(f"{os.path.dirname(os.path.abspath(__file__))}{slash}email.json"):
			err(f"\nPlik \"email.json\" nie istnieje !!")
			log(f"Umieść dane email potrzebne do połączenia się przez email w pliku email.json\n")
			with open("./email.json", "w") as fp:
				fp.write('{\n\t"sender_email": "",\n\t"password": "",\n\t"recipient_email": ""\n\t"smtp_server": ""\n\t"smtp_port": \n}')
			return
		else:
			with open(f"{os.path.dirname(os.path.abspath(__file__))}{slash}email.json", "r") as fp:
				email_data = json.loads(fp.read())

	if not os.path.isfile(db_name):
		create_db()

	main()

def main():
	global email_data
	clear()
	import certstream
	global key_words
	try:
		key_words = read_input(sys.argv[1])
	except UnicodeDecodeError:
		err(f"\nPilk {sys.argv[1]} jest źle zakodowany, inaczej niż utf-8 !!\n"
		+"Upewnij się że to prawidłowy plik.\n")

		return
	if debug_mode:
		log("[DEBUG MODE ON]", magenta)
	else:
		log("[Maile wysyłane do " + email_data["recipient_email"] + "]", magenta)
	log("Monitorowanie...")
	log("Data; Godzina; Domena;", white)
	log("", yellow)
	certstream.listen_for_events(start_monitor, url='wss://certstream.calidog.io/')

def create_db():
	conn = sqlite3.connect(db_name)
	curr = conn.cursor()
	curr.execute("CREATE TABLE logs (id int primary key, data date, czas time, domena varchar(256), raw_data text);")
	conn.commit()

def send_mail(subject, body, recipient):
	global email_data

	message = MIMEMultipart()
	message["From"] = email_data["sender_email"]
	message["To"] = recipient
	message["Subject"] = subject
	message.attach(MIMEText(body, "plain"))
	with smtplib.SMTP_SSL(email_data["smtp_server"], email_data["smtp_port"]) as server:
		server.login(email_data["sender_email"], email_data["password"])
		server.sendmail(email_data["sender_email"], recipient, message.as_string())

def prettify_domain(domain):
	global key_words
	out = yellow
	for key_word in key_words:
		if key_word in domain:
			key_word_index = domain.find(key_word)
			out += (domain[:key_word_index] + cyan +domain[key_word_index:key_word_index+len(key_word)] + yellow + domain[key_word_index+len(key_word):])
			break
	return out

def upload2db(date, time, domain, cert_info):
	conn = sqlite3.connect(db_name)
	curr = conn.cursor()
	record_id = curr.execute("SELECT COUNT(*) FROM logs;").fetchall()[0][0]
	curr.execute('INSERT INTO logs(id, data, czas, domena, raw_data) VALUES (?, ?, ?, ?, ?);', (record_id, str(date), str(time), str(domain), str(cert_info)))
	conn.commit()

def process_domain(domains, cert_info):
	for word in key_words:
		domain = domains[0]
		if word in domain:
			date = datetime.datetime.now().strftime('%m/%d/%y')
			time = datetime.datetime.now().strftime('%H:%M:%S')

			upload2db(date, time, domain, str(cert_info))
			log(f"{date}"+red+";"
				+yellow+f"{time}"+red+";"
				+yellow+f"{prettify_domain(domain)}"+red+";"
				, yellow)


			if not debug_mode:
				msg = f"Dnia: {date}\nGodzina: {time}\n\nDomena: {domain}\n"
				for domain in domains[1:]:
					msg+= f"\t{domain}\n"
				
				
				msg += "\n"
				msg += ("Certificate Issuer: " + str(cert_info["issuer"]["O"]) + "\n")
				msg += ("Authority Key Identifier: " + cert_info["extensions"]["authorityKeyIdentifier"][6:])
				msg += (cert_info["extensions"]["authorityInfoAccess"] + "\n")
				msg += ("Subject Key Identifier: " + cert_info["extensions"]["subjectKeyIdentifier"] + "\n")
				msg += ("Numer seryjny: " + cert_info["serial_number"] + "\n")
				msg += ("Fingerprint: " + cert_info["fingerprint"] + "\n")
				msg += ("Algorytm: " + cert_info["signature_algorithm"] + "\n")
				
				epoch_time_not_before = cert_info["not_before"]
				epoch_time_not_after = cert_info["not_after"]
				not_before = str(datetime.datetime.utcfromtimestamp(epoch_time_not_before)).replace("-", "/")
				not_after = str(datetime.datetime.utcfromtimestamp(epoch_time_not_after)).replace("-", "/")

				msg += "\n"
				msg += (f"Not before: {not_before}\n")
				msg += (f"Not after:  {not_after}\n")
				msg += "\n"

				send_mail(f"Rejestracja domeny z filtrem", msg, email_data["recipient_email"])
			
			break

def start_monitor(message, context):
	if message["message_type"] == "heartbeat":
		err("\nHeartbeat\n")
		return
	if message["message_type"] == "certificate_update":
		domains = message["data"]["leaf_cert"]["all_domains"]
		cert_info = message["data"]["leaf_cert"]
		if len(domains) != 0:
			domain = domains[0]
			process_domain(domains, cert_info)
			
def read_input(file):
	with open(file, "r") as fp:
		out = fp.read().split("\n")
	i=0
	while i < len(out):
		if out[i].strip() == "":
			out.pop(i)
			i-=1
		else:
			if " " not in out[i].strip():
				out[i] = out[i].strip()
			else:
				out.pop(i)
				i-=1
		i+=1

	return out

if __name__ == "__main__":
	init()
