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
cur.execute("select * from tc_calls_view where paticipant_count > 0")
response = cur.fetchall()

dump = []

for row in response:
	if row[6] != None: start_time = row[6].strftime('%d.%m.%Y %H:%M') 
	else: start_time = None
	if row[7] != None : end_time = row[7].strftime('%d.%m.%Y %H:%M') 
	else: end_time = None
	if row[3] == 5 and row[4] == 0: conf_type = 'Все на экране'
	elif row[3] == 5 and row[4] == 3: conf_type = 'Селектор'
	elif row[3] == 5 and row[4] == 1: conf_type = 'Видеоурок'
	else: conf_type = 'Точка-точка'
	
	app_row = [row[0],row[1],row[2],row[10],conf_type,row[5],start_time,end_time,row[8],row[9]]
	dump.append(app_row)
    
#print (json.dumps(dump))
with open('/var/www/html/data/TCconfs.txt', 'w') as file:
	file.write(json.dumps(dump, ensure_ascii=False).encode('utf-8').decode())
