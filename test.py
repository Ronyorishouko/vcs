#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, django, re, datetime
sys.path.append('/var/www/VCS_Portal/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'VCS.settings'
django.setup()

from Poly.tasks import update_KSUIT
from django.db.models import Q
from TrueConf.models import User, Conference, tc_versions,db_connections, tc_ai_transcrib, Type_confs
from Poly.models import registry, physical_address, ksuit, maintable,manufacturer,do_reg,group_networker,service_wg,terminal_model,type_cabinet
from Poly.views import report_active_user, report_type_confs, report_chat_message_for_user, illegal_endpoints, suid_users,suid_catalog
import subprocess, codecs, requests, re,sys, io
from req_to_all_db import get_req_to_db, count_servers



#Conference.check_conferences('2025')
#Conference.update()
#Conference.update(True)
#tc_ai_transcrib.update()
#ksuit.update()
#registry.update()
#ksuit.update_registry()
update_KSUIT()



def update_users():
	return User.update()

def update_confs():
	Conference.update_app_id()
#	return Conference.update()

def update_vers():
#	return tc_versions.update_visible()
	return tc_versions.update()

def update_ksuit():
	ksuit.update()
	registry.update()
	return ksuit.update_registry()

def update_cdr():
	return maintable.update()

def update_other():
	return physical_address.update()

def update_active_cdr():
	return maintable.update_active_call()

def update_active_confs():
	return Conference.update_active_calls()


messages = {}
def filling_data(response):
	for row in response:
		messages.update({row[0]:messages.setdefault(row[0], 0)+row[1]})
		
#update_active_confs()
#update_vers()

def update_tc_users():
#	User.update()
#	User.update_first_logon()
	User.f_send_mail('16.05.2025')
	report_active_user('16.05.2025')
	return True


#update_tc_users()
#Conference.check_conferences('2025')
#Conference.update()

def test():
	sid1=[]
	sid2=[]

	def insert_tc_calls(server,conf_id):
		query = "select call_id, display_name, join_time, leave_time, leave_reason, instance, conference_id, app_id from stat.participants where conference_id = '" + conf_id + "'"
		response = get_req_to_db(server,query)
		print(response)
		for elem in response:
			app_key = elem[7]
			val_leave_time = elem[3]
			query = "select app_id from stat.participants where conference_id = '{}' and call_id = '{}' and join_time = '{}'".format(conf_id,elem[0],elem[2])
			user_server = get_user_server(elem[0],server)
			app_info, app_key = get_keys(user_server,conf_id,elem[0],query)
			print(app_info, app_key)


	def get_user_server(user_id,server):
		if len(re.findall('tc\d{1,3}', user_id)) > 0:
			return re.findall('tc\d{1,3}', user_id)[0][2:]
		else: return server


	def get_keys(server,conf_id,elem0,query):
		app_key = get_req_to_db(server,query)
		print(app_key)
		if len(app_key) > 0:
			app_key = app_key[0][0]
			query = "select value from registry.keys where key like '%{}%' and (name = 'version' or name = 'app_name')".format(app_key)
			app_info = get_req_to_db(server,query)
		else:
			query = "select value from registry.keys where key like '%{}%' and (name = 'version' or name = 'app_name')".format(app_key)
			app_info = get_req_to_db(server,query)
		return app_info, app_key



	def get_cofs_from_tc(server):
		condition1 = "tc"+str(server)
		condition2 = "vks0"+str(server)
		for elem in response:
			if not elem[0] in sid2 and (condition1 in elem[0] or condition2 in elem[0]):
				sid2.append(elem[0])
				if elem[7] != None:
					duration = float(round((elem[7]-elem[6]).total_seconds()/60,2))
				else: duration = None
				if elem[1] == None and elem[8] == 2:
					topic = 'Точка-точка'
				elif elem[1] == None and elem[8] > 2: topic = 'Конференция'
				else:topic = elem[1]
				user_login, created_some_user = User.objects.get_or_create(login = elem[2].split('@')[0].lower(), defaults={"visible": False})
				if elem[3] == 5 and elem[4] == 0: conf_type = Type_confs.objects.get(id=1)
				elif elem[3] == 5 and elem[4] == 3: conf_type = Type_confs.objects.get(id=2)
				elif elem[3] == 5 and elem[4] == 1: conf_type = Type_confs.objects.get(id=3)
				else: conf_type = Type_confs.objects.get(id=0)
				sid1.append([elem[0]])
	#			sid1.append([elem[0],topic,elem[2],conf_type,elem[5],elem[6],elem[7],duration,None, user_login])
				topic = None


	tc_sql_query = "select id, topic, owner, type, subtype, named_conf_id, start_time, end_time, max_participants from stat.conferences where start_time between '{}' and '{}' ".format('2025-02-01', '2025-02-03')


	for serv in range(1,count_servers):
		response = get_req_to_db(serv,tc_sql_query)
		get_cofs_from_tc(serv)


	for string in sid1:
		if 'wtc' not in string[0].split('@')[1]:
			insert_tc_calls(string[0].split('@')[1][2:].split('.')[0],string[0])


#report_active_user(False)
