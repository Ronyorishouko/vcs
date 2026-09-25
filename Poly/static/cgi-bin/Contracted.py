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

cur.execute("select name, manufacturer_name, model_name, ip, serial_number, do_name, type_cab_name, address, site, wg from viev1")
response = cur.fetchall()
dump = []

for row in response:
	dump.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],[endpoints[0].get(row[4])]])
print (json.dumps(dump))
