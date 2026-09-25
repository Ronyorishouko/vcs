#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json

print('Content-Type: application/json\n')

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
cur.execute("select * from TC_View")
#cur.execute("select distinct sid, named_conf_id, start_time, topic, owner from tc_calls order by named_conf_id")
response = cur.fetchall()

dump = []

for row in response:
	dump.append([row[0],row[1],row[2],row[3],row[4].strftime('%d.%m.%Y %H:%M'),row[5].strftime('%d.%m.%Y %H:%M'),row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]])
with open('/var/www/html/data/calls.txt', 'w') as file:
	file.write(json.dumps(dump, ensure_ascii=False).encode('utf-8').decode())
