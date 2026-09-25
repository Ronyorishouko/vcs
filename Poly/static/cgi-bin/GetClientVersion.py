#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json
import datetime

print('Content-Type: application/json\n')

tc1 = psycopg2.connect(
host="10.62.254.47",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")

tc1.autocommit = True

tc2 = psycopg2.connect(
host="10.62.254.48",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")

tc2.autocommit = True

tc3 = psycopg2.connect(
host="10.62.254.49",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")

tc3.autocommit = True

# Создание курсора
tc1_cur = tc1.cursor()
tc2_cur = tc2.cursor()
tc3_cur = tc3.cursor()

def serialize_datetime(obj):
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	raise TypeError("Type not serializable")
	
dt = datetime.datetime.now()
dump = []

def filling_data(response):
	for row in response:
		app_row = {"login":row[0],"app_id":row[1],"app_name":row[2],"login date":row[3],"app_version":row[4]}
		dump.append(app_row)


tc1_cur.execute("select * from app_version")
response = tc1_cur.fetchall()
filling_data(response)
tc2_cur.execute("select * from app_version")
response = tc2_cur.fetchall()
filling_data(response)
tc3_cur.execute("select * from app_version")
response = tc3_cur.fetchall()
filling_data(response)



#print (json.dumps(dump))
print((json.dumps(dump, ensure_ascii=False,default=serialize_datetime).encode('utf-8').decode()))
