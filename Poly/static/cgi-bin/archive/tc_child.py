#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json
import cgi, cgitb
print('Content-Type: application/json\n\n')

# Подключение к базе данных
conn = psycopg2.connect(
	host="localhost",
	database="trueconfdb",
	user="pusr",
	password="Polycom12#$"
)
conn.autocommit = True
# Создание курсора
cur = conn.cursor()

data = cgi.FieldStorage()
sid = data['sid'].value

cur.execute("select call_id, display_name, duration, join_time, leave_time, leave_reason, instance from tc_calls_partisipants where sid = '" + sid + "'")
response = cur.fetchall()

dump = []

for row in response:
	dump.append([row[0],row[1],row[2],row[3].strftime('%d.%m.%Y %H:%M'),row[4].strftime('%d.%m.%Y %H:%M'),row[5],row[6]])
print (json.dumps(dump))
