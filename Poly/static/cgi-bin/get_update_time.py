#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json
import datetime

print('Content-Type: application/json\n')


# Подключение к базе данных
time_conn = psycopg2.connect(
	host="localhost",
	database="trueconfdb",
	user="pusr",
	password="Polycom12#$"
)
time_conn.autocommit = True
cur = time_conn.cursor()
# Создание курсора

app_row = {}

def serialize_datetime(obj):
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	raise TypeError("Type not serializable")
	
cur.execute("select * from times")
response = cur.fetchall()
for row in response:
	app_row.update({row[0]:row[1]})
		
#print (json.dumps(dump))
print((json.dumps(app_row, ensure_ascii=False,default=serialize_datetime).encode('utf-8').decode()))
