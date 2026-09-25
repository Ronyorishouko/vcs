#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import json
import datetime
from urllib.parse import parse_qs
import os
query = parse_qs(os.environ['QUERY_STRING'])
sid = query["get_SID"][0]
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

dump = []

def serialize_datetime(obj):
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	raise TypeError("Type not serializable")
	
def filling_data(response):
	for row in response:
		dump.append([row[0],row[1],row[2].strftime('%d.%m.%Y %H:%M'),row[3],row[4],row[5],row[6],row[7],row[8],row[9]])

tc1_cur.execute("select conference_id, call_id, join_time, display_name, appid, instance, version, local_ip, ip, app_name from (select conference_id,call_id,join_time,display_name,app_id as appid,instance from stat.participants where conference_id ilike '{}%' and not app_id isnull) as main left join (select key, value as version from registry.keys where name = 'version') as ver on ver.key ilike '%' || main.appid || '%'  left join (select key, value as local_ip from registry.keys where name = 'Local_ip') as local_ip on local_ip.key ilike '%' || main.appid || '%' left join (select key, value as ip from registry.keys where name = 'IP') as ip on ip.key ilike '%' || main.appid || '%' left join (select key, value as app_name from registry.keys where name = 'app_name') as app_name on app_name.key ilike '%' || main.appid || '%'".format(sid))
response = tc1_cur.fetchall()
filling_data(response)

tc2_cur.execute("select conference_id, call_id, join_time, display_name, appid, instance, version, local_ip, ip, app_name from (select conference_id,call_id,join_time,display_name,app_id as appid,instance from stat.participants where conference_id ilike '{}%' and not app_id isnull) as main left join (select key, value as version from registry.keys where name = 'version') as ver on ver.key ilike '%' || main.appid || '%'  left join (select key, value as local_ip from registry.keys where name = 'Local_ip') as local_ip on local_ip.key ilike '%' || main.appid || '%' left join (select key, value as ip from registry.keys where name = 'IP') as ip on ip.key ilike '%' || main.appid || '%' left join (select key, value as app_name from registry.keys where name = 'app_name') as app_name on app_name.key ilike '%' || main.appid || '%'".format(sid))
response = tc2_cur.fetchall()
filling_data(response)

tc3_cur.execute("select conference_id, call_id, join_time, display_name, appid, instance, version, local_ip, ip, app_name from (select conference_id,call_id,join_time,display_name,app_id as appid,instance from stat.participants where conference_id ilike '{}%' and not app_id isnull) as main left join (select key, value as version from registry.keys where name = 'version') as ver on ver.key ilike '%' || main.appid || '%'  left join (select key, value as local_ip from registry.keys where name = 'Local_ip') as local_ip on local_ip.key ilike '%' || main.appid || '%' left join (select key, value as ip from registry.keys where name = 'IP') as ip on ip.key ilike '%' || main.appid || '%' left join (select key, value as app_name from registry.keys where name = 'app_name') as app_name on app_name.key ilike '%' || main.appid || '%'".format(sid))
response = tc3_cur.fetchall()
filling_data(response)

print((json.dumps(dump, ensure_ascii=False,default=serialize_datetime).encode('utf-8').decode()))