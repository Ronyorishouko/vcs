#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json

print('Content-Type: application/json\n\n')

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
#cur.execute("select do_name, starttime, callidentifier, originator, numberdigits,dialstring, destination, duration, callsignaling, conference from maintable where duration > '00:10:00.000' and not (originator like 'sip:gatewayRMX%' or originator like '%s4b01.gazprom-neft.local%' or originator like '%Control%' or originator like '%TechSupport %' )")
cur.execute("select do_name, starttime, ksuit_name, callidentifier, originator, numberdigits, dialstring, destination, duration, callsignaling, conference,orig_ip, dest_ip from calls_view where orig_ip != dest_ip")
response = cur.fetchall()
dump = []

for row in response:
        dump.append([row[0],row[1].strftime('%d.%m.%Y %H:%M'),row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]])
#print (json.dumps(dump))
with open('/var/www/html/data/cdr.txt', 'w') as file:
	file.write(json.dumps(dump, ensure_ascii=False).encode('utf-8').decode())