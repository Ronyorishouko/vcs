#!/usr/bin/python3
# -*- coding: cp1251 -*-
#export PYTHONWARNINGS="ignore:Unverified HTTPS request"
import requests, json, xmltodict
from time import time
from datetime import datetime
requests.packages.urllib3.disable_warnings()


def rpg_control(ip):
	response = []
	connected = False
	URL = "https://"+str(ip)+"/rest"
	URL2 = "https://"+str(ip)+"/rest/current"
	URL3 = "http://"+str(ip)
	PARAMS1 = {'action': 'Login', 'user': 'admin', 'password': 'vk$_$ys@DMin'}
	PARAMS3 = {'action':'Logout'}
	PARAMS4 = {'names':['system.info.systemname', 'comm.nics.sipnic.sipusername', 'system.info.serialnumber', 'system.info.humanreadablemodel']}

	# Working with Sessions
	s = requests.Session()

	def login_rpg(URL, PARAMS, s, headers={}, verify=False):
		# Loging to WEB
		try:
			r1 = s.post(URL, json=PARAMS, headers = {'Authorization':'Basic '}, verify=verify)
			print('first try', r1.status_code, r1.cookies.get_dict(), r1.headers, URL)
			r1.encoding = 'UTF-8'
			status = True
			if r1.status_code == 403 or not (any([x in r1.cookies.get_dict() for x in ['SessionId','session_id']])):
				PARAMS.update({'password': 'G0D_F@ther-vcs'})
				r1 = s.post(URL, json = PARAMS, headers = {'Authorization':'Basic ='}, verify=False)
				print('second try', r1.status_code, r1.cookies.get_dict(), r1.headers, URL)
			if not any([x in r1.cookies.get_dict() for x in ['SessionId','session_id']]):
				try:
					json.loads(r1.text)
					status = True
				except ValueError:
					r1 = s.post(URL, json=PARAMS, headers = {'Authorization':'Basic ='}, verify=False)
					print('third try', r1.status_code, r1.cookies.get_dict(), r1.headers, URL)
					r1.encoding = 'UTF-8'
					if 'SessionId' in r1.cookies.get_dict() or 'ClientId' in r1.cookies.get_dict():
						status = True
					else:
						status = False
		except requests.exceptions.ConnectionError as err:
			r1 = f"Terminal {str(ip)} is unreachable. Error - {err}"
			status = False
			pass
		return [r1, status]

	def reboot_rpg(URL, PARAMS2, s):
		print('---------------Rebooting now------------------')
		r2 = s.post(URL, json = PARAMS2, verify=False) 
		r2.encoding = 'UTF-8'
		r2Content = r2.text
		r2ContentCheck = "System Diags Service: reboot carried out successfully"
		if (r2.status_code == 200 and r2ContentCheck in r2Content):
			return('----------------------Reboot '+str(ip)+' was started------------------------------')
		else:return('-----------------------Reboot '+str(ip)+' was not started-----------------------------')

	def conf_info(URL, s):
		req = s.get(URL, params={'_dc':int(time() * 1000)})
		return req

	def term_info(URL, s, PARAMS=PARAMS4):
		req = s.post(URL, json = PARAMS, verify=False)
		return req

	def logout_rpg(URL, PARAMS, s, model):
		if model == 'rpg':
			try:
				r1 = s.post(URL, json = PARAMS, data = PARAMS, verify=False)
				r1.encoding = 'UTF-8'
			except requests.exceptions.ConnectionError as err:
				r1 = f"Terminal {str(ip)} is unreachable. Error - {err}"
				pass
			return r1
		elif model == 'sx':
			try:
				r1 = s.delete(URL, verify=False)
				r1.encoding = 'UTF-8'
			except requests.exceptions.ConnectionError as err:
				r1 = f"Terminal {str(ip)} is unreachable. Error - {err}"
				pass
			return r1
		elif model == 'cisco':
			try:
				r1 = s.post(URL, verify=False)
				r1.encoding = 'UTF-8'
			except requests.exceptions.ConnectionError as err:
				r1 = f"Terminal {str(ip)} is unreachable. Error - {err}"
				pass
			return r1

	print('1 login')
	login = login_rpg(f'{URL}/session', PARAMS1, s)
	if login[1] and login[0].status_code == 200:
		conferences = conf_info(f'{URL}/conferences',s).json()
		if len(conferences) > 0:
			systemID = conferences[0]['terminals'][0]['systemID'] if len(conferences[0]['terminals']) > 0 else None
			callType = conferences[0]['connections'][0]['callType'] if len(conferences[0]['connections']) > 0 else None
			confName= conferences[0]['connections'][0]['address'].split(' ')[0] if len(conferences[0]['connections']) > 0 else None
			startTime = conferences[0]['startTime']
			duration = conferences[0]['duration'] if int(conferences[0]['duration']) > 0 else None
			status = 'InCall (Busy)' if int(conferences[0]['duration']) > 0 else 'Sleep'
		else:
			systemID = callType = confName = startTime = duration = None
			status = 'Sleep'

		terminal_info = term_info(f'{URL}/config?_dc={int(time() * 1000)}', s).json()
		response = [terminal_info['vars'][0]['value'],terminal_info['vars'][1]['value'],terminal_info['vars'][2]['value'],terminal_info['vars'][3]['value']]
		response.extend([systemID, callType, confName, startTime, duration, status])
		logout = logout_rpg(f'{URL}/session', PARAMS3, s, 'rpg') if terminal_info['vars'][3]['value'].__contains__('RealPresence') else logout_rpg(f'{URL2}/session', ' ', s, 'sx')
		connected = True
	elif not connected:
		print('2 login')
		login = login_rpg(f'{URL3}/xmlapi/session/begin', {'username':'admin', 'password':'', 'next':''}, s)
		if login[1] == True and (login[0].status_code == 200 or login[0].status_code == 204):
			terminal_info = json.loads(json.dumps(xmltodict.parse(conf_info(f'{URL3}/getxml?location=/Status/SystemUnit',s).text)))
			sip = json.loads(json.dumps(xmltodict.parse(conf_info(f'{URL3}/getxml?location=/Status/SIP',s).text)))
			conferences = json.loads(json.dumps(xmltodict.parse(conf_info(f'{URL3}/getxml?location=/Status/Call',s).text)))
			if not 'EmptyResult' in conferences:
				systemID = conferences['Status']['Call']['DisplayName']
				callType = conferences['Status']['Call']['Protocol']
				confName = conferences['Status']['Call']['DisplayName']
				duration = conferences['Status']['Call']['Duration']
				startTime = (datetime.timestamp(datetime.now()) - int(duration))*1000
				status = 'InCall (Busy)'
			else:
				systemID = callType = confName = startTime = duration = None
				status = 'Sleep'
			logout = logout_rpg(f'{URL3}/xmlapi/session/end', '', s, 'cisco')
			response = [terminal_info['Status']['SystemUnit']['BroadcastName'],sip['Status']['SIP']['Registration']['URI'],terminal_info['Status']['SystemUnit']['Hardware']['Module']['SerialNumber'],terminal_info['Status']['SystemUnit']['ProductId']]
			response.extend([systemID, callType, confName, startTime, duration, status])

	return (login, response)

