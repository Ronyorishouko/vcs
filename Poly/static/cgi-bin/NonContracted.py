#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import psycopg2
from get_active_endpnts import *
print('Content-Type: application/json\n')

endpoints = main()

# Подключение к базе данных
conn = psycopg2.connect(
	host="localhost",
	database="PolyDB",
	user="pusr",
	password="Polycom12#$"
)
conn.autocommit = True

# Создание курсора
cur = conn.cursor()
dump = []
dump2 = []
terminals = []
cur.execute("select ip from ksuit where active = \'Да\'")
response = cur.fetchall()
for elem in response:
	terminals.append(elem[0])
for keys2 in endpoints[0].keys():
	if keys2 not in terminals:
		dump.append(keys2)

for row in range(len(endpoints[0])):
	if endpoints[1][row].split(',')[10] in dump and endpoints[1][row].split(',')[10] != '':
		dump2.append([endpoints[1][row].split(',')[2],None, endpoints[1][row].split(',')[3],endpoints[1][row].split(',')[10],None, endpoints[1][row].split(',')[13][4:],None, None,None, None,endpoints[1][row].split(',')[22]])
print (json.dumps(dump2))
