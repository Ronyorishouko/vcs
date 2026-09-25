#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json

print('Content-Type: application/json\n')

# Подключение к базе данных
vers_conn = psycopg2.connect(
	host="localhost",
	database="trueconfdb",
	user="pusr",
	password="Polycom12#$"
)
vers_conn.autocommit = True
# Создание курсора

def start_sync():
	vers_cur = vers_conn.cursor()
	vers_cur.execute("select * from tc_versions_view")
	response = vers_cur.fetchall()
	
	dump = []
	
	for row in response:
		dump.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8].strftime('%d.%m.%Y %H:%M')])
	#print (json.dumps(dump))
	with open('/var/www/html/data/TC_Versions.txt', 'w+') as file:
		file.write(json.dumps(dump, ensure_ascii=False).encode('utf-8').decode())