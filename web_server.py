#!/usr/bin/python3

from flask import Flask
from werkzeug.serving import make_server
import os
import sys
import sqlite3
import json

slash = "/" if os.name == "posix" else "\\"
sys.stdout = open(os.devnull, "w")
app = Flask(__name__)

def load_style():
	with open(f"{os.path.dirname(os.path.abspath(__file__))}{slash}style.css", "r") as fp:
		style = fp.read()
	return f"<style>{style}</style>"

def process_json(text):
	out_text = ""
	x = False
	for i in range(len(text)):
		if not x and text[i] == "\"":
			out_text += "\"<font class=\"str\">"
			x = True
		elif x and text[i] == "\"":
			out_text += "</font>\""
			x = False
		elif text[i] == ":" and not x:
			out_text += "<b class=\"dots\">:</b>"
		else:
			out_text += text[i]

	return out_text

@app.route("/<id_number>", methods=["GET"])
def more_info(id_number):
	html = load_style()
	conn = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}{slash}logs.db")
	curr = conn.cursor()
	select = curr.execute("SELECT * FROM logs WHERE id=" + id_number + ";").fetchall()
	
	html += f"<h1>{select[0][3]}</h1>"
	html += "<p>"

	json_raw = str(select[0][4]).replace("'", "\"").replace("None", "\"None\"").replace("Let\"s", "Let's").replace("True", "\"True\"").replace("False", "\"False\"")
	json_text = json.dumps(json.loads(json_raw), indent=4).replace(" ", "&ensp;").replace("\n", "<br>")

	html += process_json(json_text)

	html +="</p>"
	return html

@app.route('/')
def index():
	html = load_style()

	conn = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}{slash}logs.db")
	curr = conn.cursor()
	select = curr.execute("SELECT * FROM logs ORDER BY id DESC;").fetchall()
	html += "<table>"
	html += "<tr>"
	html += "<th>ID</th>"
	html += "<th>Date</th>"
	html += "<th>Hour</th>"
	html += "<th>Domain</th>"
	html += "<th>More info</th>"
	html += "</tr>"

	for i in range(len(select)):
		html += "<tr>"
		for j in range(4):
			if j == 0:
				style_class = " class=\"id_pos\""
			elif j == 1:
				style_class = " class=\"date_pos\""
			elif j == 2:
				style_class = " class=\"time_pos\""
			elif j == 3:
				style_class = " class=\"dom_pos\""
			else:
				style_class = ""
			html += f"<td{style_class}>{select[i][j]}</td>"
		html += f"<td class=\"info_pos\"><a href=\"{select[i][0]}\">Więcej informacji</a></td>"
		html += "</tr>"
	html += "</table>"

	return html



if __name__ == '__main__':
	server = make_server('127.0.0.1', 51820, app)
	server.serve_forever()
