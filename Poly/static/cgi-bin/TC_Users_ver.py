#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json
import datetime, sys
from TC_Versions import start_sync
sys.path.append("/var/www/html/cgi-bin")
sys.path.append("/var/www/html/data")

print('Content-Type: application/json\n')

conn = psycopg2.connect(
	host="localhost",
	database="trueconfdb",
	user="pusr",
	password="Polycom12#$"
)


tc1 = psycopg2.connect(
host="10.62.254.47",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")


tc2 = psycopg2.connect(
host="10.62.254.48",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")


tc3 = psycopg2.connect(
host="10.62.254.49",
database="tcs",
port="5433",
user="vcs_scrpt",
password="GW0x7byZ[dfOlq%-0")


conn.autocommit = True
tc1.autocommit = True
tc2.autocommit = True
tc3.autocommit = True

# Создание курсора
cur = conn.cursor()
tc1_cur = tc1.cursor()
tc2_cur = tc2.cursor()
tc3_cur = tc3.cursor()

def serialize_datetime(obj):
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	raise TypeError("Type not serializable")
	
dt = datetime.datetime.now()
dump = []
user_log_info = {}
app_row = []

def filling_data(response):
	for row in response:
		app_row.append([row[0],row[1],row[2],row[3],row[4]])



tc1_cur.execute("select * from app_version")
response = tc1_cur.fetchall()
filling_data(response)

tc2_cur.execute("select * from app_version")
response = tc2_cur.fetchall()
filling_data(response)

tc3_cur.execute("select * from app_version")
response = tc3_cur.fetchall()
filling_data(response)


for row in app_row:
	cur.execute("INSERT INTO tc_versions (login, app_id,app_name, last_logon_date, app_version) select %s,%s,%s,%s,%s WHERE NOT EXISTS (SELECT 1 FROM tc_versions WHERE login=%s and app_name=%s)", (row[0],row[1],row[2],row[3],row[4],row[0],row[2]))
	cur.execute("UPDATE tc_versions SET app_id=%s, last_logon_date=%s,app_version=%s WHERE login=%s and app_name=%s",(row[1],row[3],row[4],row[0],row[2]))


start_sync()