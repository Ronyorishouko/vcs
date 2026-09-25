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
cur.execute("select * from tc_users")
response = cur.fetchall()

dump = []

for row in response:
	dump.append([row[0],row[6],row[8],row[1],row[2],row[3],row[4],row[5]])
print (json.dumps(dump))
