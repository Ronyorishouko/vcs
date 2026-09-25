#!/usr/bin/python3
# -*- coding: utf-8 -*-

import psycopg2
import sys
sys.path.append("/var/www/html/")
print('Content-Type: text/plain\n')
import openpyxl
from openpyxl.worksheet.table import Table
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
import datetime, calendar
from datetime import timedelta
from urllib.parse import parse_qs
import os
#import calendar

query = parse_qs(os.environ['QUERY_STRING'])
	
			
thin = Side(border_style="thin")

font = Font(name='Arial', size=12, bold=False, italic=False)
alignment=Alignment(wrapText=True, horizontal='center',vertical='center')

date_from = datetime.datetime.strptime(query["from_date"][0],'%Y-%m-%d')
date_to = datetime.datetime.strptime(query["to_date"][0],'%Y-%m-%d')
count_days = (date_to - date_from).days
#========================================================
tc_user = "vcs_scrpt"
tc_pass = "GW0x7byZ[dfOlq%-0"

main_tcDB = psycopg2.connect(
	host="localhost",
	database="trueconfdb",
	user="pusr",
	password="Polycom12#$"
)

tc1 = psycopg2.connect(
	host="10.62.254.47",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

tc2 = psycopg2.connect(
	host="10.62.254.48",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

tc3 = psycopg2.connect(
	host="10.62.254.49",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

tc4 = psycopg2.connect(
	host="10.62.254.43",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

tc5 = psycopg2.connect(
	host="10.62.254.197",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

EKBtc1 = psycopg2.connect(
	host="10.55.128.102",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

EKBtc2 = psycopg2.connect(
	host="10.55.128.103",
	database="tcs",
	port="5433",
	user=tc_user,
	password=tc_pass
)

main_tcDB.autocommit = True
tc1.autocommit = True
tc2.autocommit = True
tc3.autocommit = True
tc4.autocommit = True
tc5.autocommit = True
EKBtc1.autocommit = True
EKBtc2.autocommit = True
main_tcDB_cur = main_tcDB.cursor()
tc1_cur = tc1.cursor()
tc2_cur = tc2.cursor()
tc3_cur = tc3.cursor()
tc4_cur = tc4.cursor()
tc5_cur = tc5.cursor()
EKBtc1_cur = EKBtc1.cursor()
EKBtc2_cur = EKBtc2.cursor()



#=======================================================


def get_report(date_from=date_from, date_to=date_to, count_days=count_days):
	wb = openpyxl.Workbook()
	ws = wb.active
#	print ("\nstart script\n")
	array = []
	users_dict = {}
	count_users = 0
	
	for i in range(count_days):
		sel_day = (date_from + timedelta(days=i)).strftime('%d-%m-%Y')
		array.append(['','',''])
		array.append(['Дата','Сервер','Кол-во активных пользователей'])
		array.append([sel_day,'',''])
		query_req = "select count(distinct t.user) from (select split_part(object_name, '@', 1) as user from log.events where created_at between '{}' and '{}' and payload->>'NewStatus' in ('1','2','5') and object_name not ilike '#%') as t".format(date_from + timedelta(days=i), date_from + timedelta(days=i+1))
		
		tc1_cur.execute(query_req)
		response = tc1_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC1',response])
		count_users += int(response)
#		print("report from tc1 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		tc2_cur.execute(query_req)
		response = tc2_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC2',response])
		count_users += int(response)
#		print("report from tc2 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		tc3_cur.execute(query_req)
		response = tc3_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC3',response])
		count_users += int(response)
#		print("report from tc3 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		tc4_cur.execute(query_req)
		response = tc4_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC4',response])
		count_users += int(response)
#		print("report from tc4 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		tc5_cur.execute(query_req)
		response = tc5_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC5',response])
		count_users += int(response)
#		print("report from tc5 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		EKBtc1_cur.execute(query_req)
		response = EKBtc1_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC6',response])
		count_users += int(response)
#		print("report from tc6 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		EKBtc2_cur.execute(query_req)
		response = EKBtc2_cur.fetchall()[0][0]
		array.append([sel_day,'Server TC7',response])
		count_users += int(response)
#		print("report from tc7 " + (date_from + timedelta(days=i)).strftime('%d %m %Y') +" to "+ (date_from + timedelta(days=i+1)).strftime('%d %m %Y') , 'users: '+str(response))
		
		array.append(['','',''])
	
	
	query_req_dict = "select distinct t.user from (select split_part(object_name, '@', 1) as user from log.events where created_at between '{}' and '{}' and payload->>'NewStatus' in ('1','2','5') and object_name not ilike '#%') as t".format(date_from, date_to)
	tc1_cur.execute(query_req_dict)
	response = tc1_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	tc2_cur.execute(query_req_dict)
	response = tc2_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	tc3_cur.execute(query_req_dict)
	response = tc3_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	tc4_cur.execute(query_req_dict)
	response = tc4_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	tc5_cur.execute(query_req_dict)
	response = tc5_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	EKBtc1_cur.execute(query_req_dict)
	response = EKBtc1_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	EKBtc2_cur.execute(query_req_dict)
	response = EKBtc2_cur.fetchall()
	for user in response:
		users_dict.update({user[0]:'user'})
	ws.append(['Количество активных пользователей за '+date_from.strftime('%d-%m-%Y')+' - '+date_to.strftime('%d-%m-%Y')+' :',len(users_dict)+1])
	
	for elem in array:
		ws.append(elem)
	wb.save("/var/www/html/Reports/report_users.xlsx")
get_report()
#print("report from " + date_from.strftime('%d %m %Y') +" to "+ date_to.strftime('%d %m %Y') +" "+str(count_days)+" days. Users " + str(count_users))
#print(array)