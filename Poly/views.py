from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from .models import maintable, ksuit, table_files, suid_users, catalog_do_file,suid_catalog, logs
from .models import registry, type_cabinet, service_wg, do_reg, manufacturer, terminal_model, subnet_mask, physical_address, group_networker
from django.db.models import Q, Count, Sum
from django.core.exceptions import FieldError
from TrueConf.models import User, channels
from .serializers import maintableSerializer, endpointSerializer, EditEndpointSerializer, ExportEndpointSerializer
import json, datetime, openpyxl, calendar, requests, re, sys, app_logger, subprocess
from openpyxl.worksheet.table import Table
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from req_to_all_db import get_req_to_db, count_servers, access_users, admins, operators
from collections import Counter, defaultdict
sys.path.append("/var/www/VCS_Portal/static/scripts")
from collections import OrderedDict

#========================================================
logger = app_logger.get_logger(__name__, '/var/log/VCS_portal/VCS_portal_Poly.log')
#=======================================================

def cred(request):
	if 'REMOTE_USER' in request.META:
		if request.META['REMOTE_USER'].lower() in access_users:
			return 'User', request.META['REMOTE_USER']
		elif request.META['REMOTE_USER'].lower() in operators:
			return 'Operator', request.META['REMOTE_USER']
		elif request.META['REMOTE_USER'].lower() in admins:
			return 'Admin', request.META['REMOTE_USER']
		else:
			return 'Anonymous', 'user'
	else:
		return 'Anonymous', 'user'


def upload_page(request):
	auth, user = cred(request)
	if request.method == 'POST' and request.FILES:
		if request.FILES.get('myfile1', False):
			test = table_files.objects.create(title='SUID_File', table_file=request.FILES['myfile1'], actualization=datetime.datetime.now(), uploader = request.META['REMOTE_USER'])
			test.save()
			wb = openpyxl.load_workbook(f'/var/www/VCS_Portal/media/{str(table_files.objects.order_by("-actualization").first().table_file)}', data_only=True)
			ws = wb.active
			for row in ws.iter_rows('B{}:B{}'.format(2,ws.max_row)):
				for cell in row:
					suid_users.objects.update_or_create(login = ws['N'+str(cell.row)].value, defaults={'company' : cell.value, 'email': ws['R'+str(cell.row)].value, 'user':request.META['REMOTE_USER']})
			return JsonResponse(json.dumps("update success"), safe=False)
		elif  request.FILES.get('catalog_File', False):
			test = catalog_do_file.objects.create(title='catalog_File', table_file=request.FILES['catalog_File'], actualization=datetime.datetime.now(), uploader = request.META['REMOTE_USER'])
			test.save()
			wb = openpyxl.load_workbook(f'/var/www/VCS_Portal/media/{str(catalog_do_file.objects.order_by("-actualization").first().table_file)}', data_only=True)
			ws = wb.active
			for row in ws.iter_rows('A{}:A{}'.format(2,ws.max_row)):
				for cell in row:
					suid_catalog.objects.update_or_create(company_slave = cell.value, defaults={'company_master' : ws['B'+str(cell.row)].value})
			return JsonResponse(json.dumps("update success"), safe=False)

	return JsonResponse('update false', safe=False)


def cdr(request):
	auth, user = cred(request)
	return render(request,'Poly/cdr.html', {'user':user,'auth':auth})

def reports(request):
	auth, user = cred(request)
	return render(request, 'Poly/reports.html', {'user':user,'auth':auth})

def endpoints(request):
	auth, user = cred(request)
	return render(request, 'Poly/endpoints.html', {'user':user,'auth':auth})

def illegal(request):
	auth, user = cred(request)
	return render(request, 'Poly/illegal.html', {'user':user,'auth':auth})

def update_KSUIT(request):
	auth, user = cred(request)
	if auth != 'User':
		last_update_time = get_req_to_db(0,"select * from times where table_name = 'ksuit'")[0][1]
		if (last_update_time + datetime.timedelta(minutes=5)) < datetime.datetime.now().astimezone():
			try:
				result = subprocess.run(['bash','/var/www/VCS_Portal/Poly/SQL_KSUIT.sh'], capture_output=True,text=True,check=True)
				ksuit.update()
				registry.update()
				ksuit.update_registry()
				get_req_to_db(0,"update times set time = '{}' where table_name = 'ksuit'".format(datetime.datetime.now().astimezone()),False)
			except subprocess.CalledProcessError as e:
				result = e.stderr
				logger.warn(f'SQL_KSUIT.sh error{result}')
			return JsonResponse(['Синхронизация выполнена'], safe=False)
		else:
			return JsonResponse(['Ещё слишком рано '], safe=False)
	else:
		return JsonResponse(['Недостаточно прав для выполнения данной операции'], safe=False)


def tasks(request):
	from VCS import celery_app
	all_tasks = celery_app.control.inspect()
	tasks = []
	for name in all_tasks.active()['celery@SPB99-VCSFS1']:
		tasks.append(name['name'])
	for name in all_tasks.reserved()['celery@SPB99-VCSFS1']:
		tasks.append(name['name'])
	tasks = list(map(lambda x: x.replace('Poly.tasks.send_active_users', 'Выгрузка активных пользователей'), tasks))
	tasks = list(map(lambda x: x.replace('Poly.tasks.update_KSUIT', 'Обновление реестра'), tasks))
	tasks = list(map(lambda x: x.replace('Poly.tasks.update_CDR', 'Обновление CDR Poly'), tasks))
	tasks = list(map(lambda x: x.replace('TrueConf.tasks.update_tc_calls_confs', 'Обновление конфренций TC'), tasks))
	tasks = list(map(lambda x: x.replace('TrueConf.tasks.update_tc_users', 'Обновление пользователей TC'), tasks))
	tasks = list(map(lambda x: x.replace('TrueConf.tasks.update_tc_versions', 'Обновление TrueConf Versions'), tasks))
	return HttpResponse(json.dumps(tasks, ensure_ascii=False), content_type='application/html')


def report_channels(request):
	server_stats = channels.objects.values('server').annotate(
		channels_count=Count('id'),
		total_messages=Sum('messages_count')
		).order_by('server')

	return JsonResponse(list(server_stats), safe=False)


def report_chat_message(request):
	date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
	date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
	logger.info(f'start report_chat_message - date_from: {date_from}, date_to: {date_to}')

	query_req_dict = "select id, sender, type, round((content::json->>'file_size')::numeric / 1048576, 2) as MB  from chat.messages where sender_type = 1 and (type = 200 or type = 201 or type = 204) and client_timestamp between '{}' and '{}'".format(date_from, date_to)

	server_stats = defaultdict(lambda: {'text': 0, 'file': 0, 'size': 0, 'survey': 0})
	processed_messages = set() # Для отслеживания уже обработанных message_id

	for serv in range(1, count_servers):
		logger.info(f'get data from server tc{serv}')
		response = get_req_to_db(serv, query_req_dict)
		for id in response:
			message_id, sender, msg_type, size = id

			# Пропускаем если сообщение уже обработано
			if message_id in processed_messages:
				continue

			# Извлекаем сервер из sender
			if '@' in sender:
				sender_server = sender.split('@')[1]
			else:
				sender_server = sender

			# Определяем, к какому серверу принадлежит sender
			target_server = determine_server(sender_server) # Ваша функция определения
			# Считаем на том сервере, к которому принадлежит sender
			if str(serv) == target_server:
				processed_messages.add(message_id)

				if msg_type == 200:
					server_stats[target_server]['text'] += 1
				elif msg_type == 201:
					server_stats[target_server]['file'] += 1
					server_stats[target_server]['size'] += size
				elif msg_type == 204:
					server_stats[target_server]['survey'] += 1

	result = []
	for server, stats in server_stats.items():
		result.append([server, stats['text'], stats['file'], float(stats['size']), stats['survey']])

	return JsonResponse(json.dumps(result), safe=False)



def determine_server(sender):
	traget_server = sender[2:].split('.pp.')[0]
	return traget_server 

def report_chat_message_for_user(request):
	if request == False:
		date_to = datetime.date.today()
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	elif isinstance(request, str):
		date_to = datetime.datetime.strptime(request, '%d.%m.%Y')
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	else:
		date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
		date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
	messages_id = {}


	if request == False or isinstance(request, str):
		query_req_dict = "select id, split_part(sender,'@',1) as p_sender from chat.messages where sender_type = 1 and type = 200 and db_timestamp between '{}' and '{}'".format(date_from, date_to)

		for serv in range(1,count_servers):
			response = get_req_to_db(serv,query_req_dict)
			for id in response:
				messages_id.update({id[0]:id[1][id[1].find('@')+1:]})

		ws.append(['Логин','Количество сообщений', 'Дата'])
		for row in list(Counter(messages_id.values()).items()):
			ws.append(list(row) + [str(date_from.strftime('%d.%m.%Y'))])
		wb.save("/var/www/VCS_Portal/static/Reports/Messages_TrueConf "+ str(date_from.strftime('%d.%m.%Y')) + ".xlsx")
		wb.close()
	else:

		server_stats = defaultdict(lambda: {'type_200': 0, 'type_201': 0, 'size': 0, 'type_204': 0})
		processed_messages = set()
		query_req_dict = "select id, split_part(sender,'@',1) as p_sender, type, round((content::json->>'file_size')::numeric / 1048576, 2) as MB from chat.messages where sender_type = 1 and (type = 200 or type = 201 or type = 204) and db_timestamp between '{}' and '{}'".format(date_from, date_to)
		for serv in range(1,count_servers):
			response = get_req_to_db(serv,query_req_dict)
			for row in response:
				message_id, sender, msg_type, size = row
				if message_id in processed_messages:
					continue

				processed_messages.add(message_id)

				if msg_type == 200:
					server_stats[sender]['type_200'] += 1
				elif msg_type == 201:
					server_stats[sender]['type_201'] += 1
					server_stats[sender]['size'] += size
				elif msg_type == 204:
					server_stats[sender]['type_204'] += 1

		result = []
		for sender, stats in server_stats.items():
			result.append([sender, stats['type_200'], stats['type_201'], float(stats['size']), stats['type_204']])

		return JsonResponse(json.dumps(result), safe=False)

def report_active_app(request):
	date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
	date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
	app_id = {}

	query_req_dict = "select payload->>'appId' as app_id, payload->>'AppName' as AppName from (select *, row_number() over (partition by split_part(object_name,'@',1), payload->>'AppName' order by created_at desc) as row_number from log.events where object_type='user' and (type='login' or type='authorize') and not payload->>'appId' isnull and not payload->>'AppName' = 'Transcoder' and payload->>'Result' = '0' and not object_name ilike '#guest%' and created_at between '{}' and '{}' ) as rows where row_number = 1 order by app_id".format(date_from, date_to)

	for serv in range(1,count_servers):
		response = get_req_to_db(serv,query_req_dict)
		for id in response:
			app_id.update({id[0]:id[1]})


	return JsonResponse(json.dumps(list(Counter(app_id.values()).items())), safe=False)


def illegal_endpoints(request):
	dump = {}
	response = {"recordsFiltered":0,"recordsTotal":0, "data":[]}
	req = requests.get('https://spb99-vcsdm.gazprom-neft.local/api/rest/devices', headers={'dataType': 'json',"Authorization": "Basic AsdfMovie123",'Accept': 'application/vnd.plcm.plcm-device-list-v3+json','contentType': 'application/json'})
	logger.info(f'{req}, {req.json()}, {req.text}')
	if 'plcmPage' in req.json():
		data = json.loads(req.text)['plcmPage']
		last_page = (-(-data['totalSize'] // data['pageSize']))
		for page in range(1, last_page+1):
			req = requests.get(f'https://ekb99-vcsdm.gazprom-neft.local/api/rest/devices?page={page}', headers={'dataType': 'json',"Authorization": "Basic AsdfMovie123",'Accept': 'application/vnd.plcm.plcm-device-list-v3+json','contentType': 'application/json'})
			endpoints = json.loads(req.text)['plcmDeviceV3List']
			for point in endpoints:
				logger.info(f'{point}')
				if 'ipAddress' in point:
					ipAddress = point['ipAddress'].split(',')[1] if ',' in point['ipAddress'] else point['ipAddress']
				else: ipAddress = None
				if 'deviceModel' not in point:
					point.update({'deviceModel':None})
				if point['deviceAdmissionPolicy'] == 'ACTIVE' and point['deviceModel'] != 'HarmanMediaSuite' and point['deviceModel'] != 'IntegrIT' and point['deviceModel'] != 'Polycom RealPresence Desktop for Windows' and (ksuit.objects.filter(ip=ipAddress, active=False).exists() or ksuit.objects.filter(ip=re.sub("^\d*","0",ipAddress), active=False).exists() or ksuit.objects.filter(ip=re.sub("^\d*.\d*","0.0",ipAddress), active=False).exists() or not ksuit.objects.filter(ip=ipAddress).exists()):
					if ksuit.objects.filter(ip=ipAddress, active=False).exists():
						terminal_name = ksuit.objects.filter(ip=ipAddress).get().name
						NewIP = ipAddress
					elif ksuit.objects.filter(ip=re.sub("^\d*","0",ipAddress), active=False).exists():
						terminal_name = ksuit.objects.filter(ip=re.sub("^\d*","0",ipAddress)).get().name
						NewIP = re.sub("^\d*","0",ipAddress)
					elif ksuit.objects.filter(ip=re.sub("^\d*.\d*","0.0",ipAddress), active=False).exists():
						terminal_name = ksuit.objects.filter(ip=re.sub("^\d*.\d*","0.0",ipAddress)).get().name
						NewIP = re.sub("^\d*.\d*","0.0",ipAddress)
					else: terminal_name = 'Undefined'
					if dump.get(ipAddress) == None:
						response["data"].append([NewIP, point['deviceName'],point['deviceModel'], terminal_name])
						dump.update({ipAddress: ''})
			response["recordsFiltered"] = len(dump)
			response["recordsTotal"] = len(dump)
		return JsonResponse(response, safe=False)
	else:
		return HttpResponse('Ошибка получения информации с DMA', status=418)


def report_type_confs(request):
	if request == False:
		date_to = datetime.date.today()
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	elif isinstance(request, str):
		date_to = datetime.datetime.strptime(request, '%d.%m.%Y')
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	else:
		date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
		date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
	app_id = []
	query_req_dict = "select id,owner,start_time,end_time,type,subtype,is_public,named_conf_id,topic,new_value->>'vad_selector' as vad_selector, max_participants from (select *, row_number() over (partition by start_time) as row_number from (select * from (select id,owner, start_time, end_time, type, subtype, is_public, named_conf_id, topic, max_participants from stat.conferences where start_time between '{}' and '{}' and named_conf_id like '{}%' order by start_time desc) as main left join (select id as L_id,user_name,new_value,created_at from log.logs where object_type = 'conference') as slog on slog.new_value->>'id' = main.named_conf_id and slog.created_at < main.start_time and slog.new_value ? 'vad_selector' order by start_time, slog.L_id desc) as dump) as final where row_number = 1;"

	def set_type_conf(conf):
		if conf[4] == 5 and conf[5] == 3 and (conf[9] == '1' or conf[9] == None):
			return conf[1],conf[8],conf[7],'Автоселектор',conf[6],conf[2].strftime('%d.%m.%Y %H:%M:%S'),conf[10]
		elif conf[4] == 5 and conf[5] == 3 and conf[9] == '0':
			return conf[1],conf[8],conf[7],'Управляемый селектор',conf[6],conf[2].strftime('%d.%m.%Y %H:%M:%S'),conf[10]
		elif conf[4] == 5 and conf[5] == 0:
			return conf[1],conf[8],conf[7],'Все на экране',conf[6],conf[2].strftime('%d.%m.%Y %H:%M:%S'),conf[10]
		elif conf[4] == 5 and conf[5] == 1:
			return conf[1],conf[8],conf[7],'Видео урок',conf[6],conf[2].strftime('%d.%m.%Y %H:%M:%S'),conf[10]
		else: return conf[1],conf[8],conf[7],'Точка-точка',conf[6],conf[2].strftime('%d.%m.%Y %H:%M:%S'),conf[10]


	for serv in range(1,count_servers):
		response = get_req_to_db(serv,query_req_dict.format(date_from, date_to, serv))
		for id in response:
			app_id.append(set_type_conf(id))

	if request == False or isinstance(request, str):
		ws.append(['Владелец','ID','Тип', 'Публичная', 'Дата'])
		for row in app_id:
			ws.append([row[0], row[2], row[3], row[4], row[5]])
		wb.save("/var/www/VCS_Portal/static/Reports/Conferences_TrueConf "+ str(date_from.strftime('%d.%m.%Y')) + ".xlsx")
		wb.close()
	else:
		return JsonResponse(json.dumps(app_id), safe=False)


def report_count_confs(request):
	if request == False:
		date_to = datetime.date.today()
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	else:
		date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
		date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
	app_id = {}

	query_req_dict = "select id, start_time, named_conf_id, topic from stat.conferences where start_time between '{}' and '{}';"

	for serv in range(1,count_servers):
		response = get_req_to_db(serv,query_req_dict.format(date_from, date_to, serv))
		for id_conf in response:
			app_id.update({id_conf[0]:id_conf})

	if request == False:
		ws.append(['SSID','Время начала','Номер', 'Название'])
		for row in app_id:
			ws.append(row)
		wb.save("/var/www/VCS_Portal/static/Reports/Conferences_count_TrueConf "+ str(date_from.strftime('%d.%m.%Y')) + ".xlsx")
		wb.close()
	else:
		return JsonResponse(json.dumps(app_id.values()), safe=False)


def export_to_excel(request):
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="Poly '+request.POST.getlist('table')[0]+'.xlsx"'
	wb = openpyxl.Workbook()
	ws = wb.active
	start = request.POST.getlist('start')[0]
	length = request.POST.getlist('length')[0]
	order_col = request.POST.getlist('columns['+request.POST.getlist('order[0][column]')[0]+'][data]')[0].replace('fields.','').replace('.','__')
	order_dir = request.POST.getlist('order[0][dir]')[0]
	finaly_rows, count, filtered, columns, name = get_users(request, start, length, order_col, order_dir, xls=True)
	if request.POST.getlist('table')[0] == 'Endpoints':
		columns = ('Наименование терминала (из КСУИТ)', 'Модель', 'Производитель', 'Сетевой адрес', 'Серийный номер', 'ДО', 'Тип помещения', 'Фактический адрес установки', 'Номер площадки', 'Сервисная рабочая группа', 'Активность')
		ws.append(columns)
		for my_row in ExportEndpointSerializer(finaly_rows, many=True).data:
			row = []
			for elem in list(my_row.values()):
				if type(elem ) == type(OrderedDict()):
					row.extend(list(elem.values()))
				else:row.append(elem)
			if len(row) > 11:
				ws.append([row[7],row[2],row[1],row[8],row[3],row[11],row[4],row[9],row[5],row[10],row[13]])
			else:
				ws.append([row[2],'','',row[3],'',row[6],'',row[4],'',row[5], row[10]])
	elif request.POST.getlist('table')[0] == 'CDR':
		columns = ('SID', 'ДО', 'Дата', 'Имя', 'Инициатор', 'Number Digits', 'DialString', 'Адресат', 'Длительность','Тип Вызова','Конференция','IP источник','IP приемник')
		ws.append(columns)
		for my_row in maintableSerializer(finaly_rows, many=True).data:
			ws.append(list(my_row.values()))

	wb.save("/var/www/VCS_Portal/static/Reports/"+request.POST.getlist('table')[0]+".xlsx")
	wb.save(response)
	wb.close()
	return response



def get_users(request=None, start=0, length=10, order_col=None, order_dir=None, xls=False, table = False):
	my_filter = Q()
	name = ''
	if len(request.POST.getlist('searchBuilder[logic]')) > 0:
		logic = request.POST.getlist('searchBuilder[logic]')[0]
		for key, value in request.POST.items():
			if 'searchBuilder' in key and '[condition]' in key and 'fields' in request.POST.getlist(key.replace('condition','origData'))[0]:
				name = request.POST.getlist(key.replace('condition','origData'))[0][7:]
			elif 'searchBuilder' in key and '[condition]' in key and not 'fields' in request.POST.getlist(key.replace('condition','origData'))[0]:
				name = request.POST.getlist(key.replace('condition','origData'))[0]
				if name.find('.') != -1:
					if 'id_manufacturer' in name or 'id_model' in name or 'id_type_cabinet' in name:
						name = name.replace('.','__')+'__name'
					else:
						name = name.replace('.','__')
			if request.POST.getlist(key)[0] == '=' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__iexact':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__iexact':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '!=' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= ~Q(**{name+'__iexact':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= ~Q(**{name+'__iexact':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == 'starts' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__istartswith':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__istartswith':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '!starts' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= ~Q(**{name+'__istartswith':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= ~Q(**{name+'__istartswith':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == 'contains' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__icontains':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__icontains':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '!contains' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= ~Q(**{name+'__icontains':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= ~Q(**{name+'__icontains':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif value == 'boolean':
				logger.info(f'{request.POST.getlist(key)[0]}, {key}, {value}')
				if logic == 'OR':
					my_filter |= Q(**{name+'__iexact':request.POST.getlist(key.replace('type','condition'))[0]})
				else:
					my_filter &= Q(**{name+'__iexact':request.POST.getlist(key.replace('type','condition'))[0]})
			elif request.POST.getlist(key)[0] == 'null':
				if logic == 'OR':
					my_filter |= Q(**{name+'__isnull':True})
				else:
					my_filter &= Q(**{name+'__isnull':True})
			elif request.POST.getlist(key)[0] == '!null':
				if logic == 'OR':
					my_filter |= Q(**{name+'__isnull':False})
				else:
					my_filter &= Q(**{name+'__isnull':False})

			elif request.POST.getlist(key)[0] == 'ends' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__iendswith':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__iendswith':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '!ends' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= ~Q(**{name+'__iendswith':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= ~Q(**{name+'__iendswith':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '<' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__lt':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__lt':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '<=' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__lte':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__lte':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '>' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__gt':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__gt':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == '>=' and request.POST.getlist(key.replace('condition','value1')):
				if logic == 'OR':
					my_filter |= Q(**{name+'__gte':request.POST.getlist(key.replace('condition','value1'))[0]})
				else:
					my_filter &= Q(**{name+'__gte':request.POST.getlist(key.replace('condition','value1'))[0]})

			elif request.POST.getlist(key)[0] == 'between' and request.POST.getlist(key.replace('condition','value1'))[0] != '' and request.POST.getlist(key.replace('condition','value2'))[0] != '':
				if logic == 'OR':
					my_filter |= Q(**{name+'__range':(request.POST.getlist(key.replace('condition','value1'))[0],request.POST.getlist(key.replace('condition','value2'))[0])})
				else:
					my_filter &= Q(**{name+'__range':(request.POST.getlist(key.replace('condition','value1'))[0],request.POST.getlist(key.replace('condition','value2'))[0])})
			elif request.POST.getlist(key)[0] == '!between' and request.POST.getlist(key.replace('condition','value1'))[0] != '' and request.POST.getlist(key.replace('condition','value2'))[0] != '':
				if logic == 'OR':
					my_filter |= ~Q(**{name+'__range':(request.POST.getlist(key.replace('condition','value1'))[0],request.POST.getlist(key.replace('condition','value2'))[0])})
				else:
					my_filter &= ~Q(**{name+'__range':(request.POST.getlist(key.replace('condition','value1'))[0],request.POST.getlist(key.replace('condition','value2'))[0])})
			else:
				pass

		if request.POST.getlist('table')[0] == 'CDR':
			columns = ('callidentifier', 'callsignaling', 'conference', 'dest_ipaddress', 'destination', 'dialstring', 'do_name', 'duration', 'ksuit_name', 'numberdigits', 'originator', 'starttime')
			if order_dir == 'desc':
				if not xls:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).filter(my_filter ).order_by('-'+order_col )[int(start):int(start)+int(length)]
				else:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True) ).filter(my_filter ).order_by('-'+order_col)
			else:
				if not xls:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).filter(my_filter).order_by(order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).filter(my_filter).order_by(order_col)
			count = maintable.objects.filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).count()
			filtered = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).filter(my_filter).count()

		elif request.POST.getlist('table')[0] == 'Endpoints':
			columns = ('id', 'name', 'ip', 'address', 'wg', 'do_name', 'address2', 'active', 'reg_ip')
			if order_dir == 'desc':
				if not xls:
					filtered_rows = ksuit.objects.filter(my_filter).order_by('-'+order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = ksuit.objects.filter(my_filter).order_by('-'+order_col)
			else:
				if not xls:
					filtered_rows = ksuit.objects.filter(my_filter).order_by(order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = ksuit.objects.filter(my_filter).order_by(order_col)
			count = ksuit.objects.count()
			filtered = ksuit.objects.filter(my_filter).count()

		elif request.POST.getlist('table')[0] == 'Zeros':
			columns = ('',)
			filtered_rows = []
			count = 0
			filtered = 0
	else:

		if request.POST.getlist('table')[0] == 'CDR':
			columns = ('callidentifier', 'callsignaling', 'conference', 'dest_ipaddress', 'destination', 'dialstring', 'do_name', 'duration', 'ksuit_name', 'numberdigits', 'originator', 'starttime')
			if order_dir == 'desc':
				if not xls:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).order_by('-'+order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).order_by('-'+order_col)
			else:
				if not xls:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).order_by(order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).order_by(order_col)
			count = maintable.objects.filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).count()
			filtered = maintable.objects.only(*columns).filter(Q(duration__gte='00:10:00') | Q(duration__isnull=True)).filter(my_filter).count()

		elif request.POST.getlist('table')[0] == 'Endpoints':
			columns = ('id', 'name', 'ip', 'address', 'wg', 'do_name', 'address2', 'active', 'reg_ip')
			if order_dir == 'desc':
				if not xls:
					filtered_rows = ksuit.objects.order_by('-'+order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = ksuit.objects.order_by('-'+order_col)
			else:
				if not xls:
					filtered_rows = ksuit.objects.order_by(order_col)[int(start):int(start)+int(length)]
				else:
					filtered_rows = ksuit.objects.order_by(order_col)
			count = ksuit.objects.count()
			filtered = ksuit.objects.count()


		elif request.POST.getlist('table')[0] == 'EditEndpoints':
			filtered_rows = ksuit.objects.filter(id=request.POST.getlist('endpoint_id')[0])
			columns = ('',)
			count = 0
			filtered = 0

		elif request.POST.getlist('table')[0] == 'Zeros':
			columns = ('',)
			filtered_rows = []
			count = 0
			filtered = 0
	logger.info(f'{request.META["REMOTE_ADDR"]}, {request.META["REMOTE_USER"]}, {my_filter}')
	return filtered_rows, count, filtered, columns, name


def load_data(request):
	draw = request.POST.getlist('draw')[0]
	start = request.POST.getlist('start')[0]
	length = request.POST.getlist('length')[0]
	order_col = request.POST.getlist('columns['+request.POST.getlist('order[0][column]')[0]+'][data]')[0].replace('fields.','').replace('.','__')
	order_dir = request.POST.getlist('order[0][dir]')[0]

	finaly_rows, count, filtered, columns, name = get_users(request, start, length, order_col, order_dir)

	if request.POST.getlist('table')[0] == 'CDR':
		Json_data = json.dumps(maintableSerializer(finaly_rows, many=True).data)

	elif request.POST.getlist('table')[0] == 'Endpoints':
		Json_data = json.dumps(endpointSerializer(finaly_rows, many=True).data)

	elif request.POST.getlist('table')[0] == 'EditEndpoints':
		Json_data = json.dumps(EditEndpointSerializer(finaly_rows, many=True).data)

	elif request.POST.getlist('table')[0] == 'Zeros':
		Json_data = json.dumps(finaly_rows)

	json_var = '{"test":"'+str(name)+'","draw": '+draw+',"recordsTotal": '+str(count)+',"recordsFiltered": '+str(filtered)+',"data":'
	json_var += Json_data + '}'

	return HttpResponse(json_var, content_type='application/json')


def create_sample_tc(request):
	resp = HttpResponse(content_type='application/ms-excel')
	resp['Content-Disposition'] = 'attachment; filename="Доступы МСЭ для TrueConf.xlsx"'
	wb = openpyxl.load_workbook('/var/www/VCS_Portal/static/Reports/Доступы МСЭ для TrueConf 2023-08-22.xlsx', data_only=True)
	ws = wb.active
	deleting_rows = []
	count_rows = ws.max_row
	def get_index(cell):
		for i in range(len(cell)):
			if '#subnet' in cell[i]:
				return i
		
	if request.POST.getlist('arm')[0] != '':
		decription = ws['G3'].value.split('\n')
		index_desckript = get_index(decription)
		subnet_list = request.POST.getlist('arm')[0].split('\n')
		append_subnets = [x + ' - подсеть АРМ на площадке '+request.POST.getlist('location-arm')[0].split('\n')[subnet_list.index(x)]+', '+request.POST.getlist('do')[0]+' '+request.POST.getlist('address-arm')[0].split('\n')[subnet_list.index(x)]+'.' for x in request.POST.getlist('arm')[0].split('\n') if x != '']
		ws['C3'] = '\n'.join(x for x in request.POST.getlist('arm')[0].split('\n') if x != '')
		ws['G3'] = '\n'.join(decription[:index_desckript] + append_subnets + decription[index_desckript+1:])
		
	if request.POST.getlist('tel')[0] != '':
		subnet_list = request.POST.getlist('tel')[0].split('\n')
		append_subnets = [x + ' - подсеть ТА на площадке '+request.POST.getlist('location-tel')[0].split('\n')[subnet_list.index(x)]+', '+request.POST.getlist('do')[0]+' '+request.POST.getlist('address-tel')[0].split('\n')[subnet_list.index(x)]+'.' for x in request.POST.getlist('tel')[0].split('\n') if x != '']
		for row in [5,6]:
			decription = ws['G'+str(row)].value.split('\n')
			index_desckript = get_index(decription)
			ws['E'+str(row)] = '\n'.join(x for x in request.POST.getlist('tel')[0].split('\n') if x != '')
			ws['G'+str(row)] = '\n'.join(decription[:index_desckript] + append_subnets + decription[index_desckript+1:])
		decription = ws['G4'].value.split('\n')
		index_desckript = get_index(decription)
		ws['C4'] = '\n'.join(x for x in request.POST.getlist('tel')[0].split('\n') if x != '')
		ws['G4'] = '\n'.join(decription[:index_desckript] + append_subnets + decription[index_desckript+1:])
		
		
	if request.POST.getlist('VCS')[0] != '':
		subnet_list = request.POST.getlist('VCS')[0].split('\n')
		append_subnets = [x + ' - подсеть ВКС на площадке '+request.POST.getlist('location-vcs')[0].split('\n')[subnet_list.index(x)]+', '+request.POST.getlist('do')[0]+' '+request.POST.getlist('address-vcs')[0].split('\n')[subnet_list.index(x)]+'.' for x in request.POST.getlist('VCS')[0].split('\n') if x != '']
		for row in [7,8,12,14,15,16]:
			decription = ws['G'+str(row)].value.split('\n')
			index_desckript = get_index(decription)
			ws['C'+str(row)] = '\n'.join(x for x in request.POST.getlist('VCS')[0].split('\n') if x != '')
			ws['G'+str(row)] = '\n'.join(decription[:index_desckript] + append_subnets + decription[index_desckript+1:])
			
		for row in [9,10,11,13]:
			decription = ws['G'+str(row)].value.split('\n')
			index_desckript = get_index(decription)
			ws['E'+str(row)] = '\n'.join(x for x in request.POST.getlist('VCS')[0].split('\n') if x != '')
			ws['G'+str(row)] = '\n'.join(decription[:index_desckript] + append_subnets + decription[index_desckript+1:])
	
	if request.POST.getlist('arm')[0] == '':
		for row in ws['A3:G3']:
			for cell in row:
				cell.value = None 
	if request.POST.getlist('tel')[0] == '': 
		for row in ws['A4:G6']:
			for cell in row:
				cell.value = None 
	if request.POST.getlist('VCS')[0] == '': 
		for row in ws['A7:G16']:
			for cell in row:
				cell.value = None 
	
	for row in ws['A3:G'+str(count_rows)]:
		for cell in row:
			if cell.value == None:
				deleting_rows.append(str(cell.row))
				break
	for i in range(len(deleting_rows)):
		for row in ws['A3:G'+str(count_rows)]:
			for cell in row:
				if cell.value == None:
					for row in ws['A'+str(int(cell.row))+':G'+str(count_rows)]:
						for cell in row:
							cell.value = ws[cell.column+str(int(cell.row)+1)].value
	
	num_row = 1
	double = Side(border_style="thin")
	for row in ws['A1'':G'+str(count_rows-len(deleting_rows))]:
		for cell in row:
			cell.border = Border(top=double, left=double, right=double, bottom=double)
	for row in range(3,count_rows+1-len(deleting_rows)):
		ws.row_dimensions[row].height = None
		ws['A'+str(row)] = num_row
		num_row+=1
	for clear_row in range(count_rows-len(deleting_rows)+1, count_rows+1):
		ws.row_dimensions[clear_row].height = None
		for row in ws['A'+str(clear_row)+':G'+str(clear_row)]:
			for cell in row:
				cell.style = ws['A200'].style
	
	wb.save(resp) 
	wb.close()
	return resp




def create_report_vcs(request):
	resp = HttpResponse(content_type='application/ms-excel')
	resp['Content-Disposition'] = 'attachment; filename="ВКС '+str(request.POST.getlist('req_do')[0])+'.xlsx"'
	centerAlign = ['E','F','G','H','I','J','K']
	alpha=['A','B','C','D','E','F','G','H','I','J','K']
	def getmonth():
		month_list = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
		return(month_list[int(request.POST.getlist('to_date')[0].split('-')[1])-1])
	def format_Table(len_table,last_row_table, max_col_table, indent=0,merge=False,Table_italic=False,align='left',align_result='none'):
		if merge==False:
			ws.merge_cells('A' + str(last_row_table+indent) + ':' + alpha[max_col_table-1] + str(last_row_table+indent))
			ws['A' + str(last_row_table+indent)].fill = PatternFill('solid', fgColor="EEECE1")
			ws['B' + str(last_row_table+indent-1)].alignment = Alignment(horizontal='right')
			ws['B' + str(last_row_table+indent-1)].font = Font(bold=True,name='Arial', size=10)
			ws['C' + str(last_row_table+indent-1)].font = Font(bold=True,name='Arial', size=10)
			ws['D' + str(last_row_table+indent-1)].font = Font(bold=True,name='Arial', size=10)
		elif merge==True:
			ws.merge_cells('A' + str(last_row_table+indent+1) + ':' + alpha[max_col_table-2] + str(last_row_table+indent+1))
			ws['A' + str(last_row_table+indent+1)].fill = PatternFill('solid', fgColor="EEECE1")
			ws['A' + str(last_row_table+indent+1)].font = Font(bold=True, name='Arial')
			ws[alpha[max_col_table-1] + str(last_row_table+indent+1)].fill = PatternFill('solid', fgColor="EEECE1")
			ws[alpha[max_col_table-1] + str(last_row_table+indent+1)].font = Font(bold=True, name='Arial')
			ws['A' + str(last_row_table+indent+1)].font = Font(bold=True, name='Arial')
			if align_result != 'none':
				ws[alpha[max_col_table-1] + str(last_row_table+indent+1)].alignment = Alignment(horizontal=align_result)
		for rows in ws.iter_rows(min_row=last_row_table-len_table, max_row=last_row_table+indent+int(merge), min_col=None,max_col=max_col_table):
			for cell in rows:
				cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
				cell.alignment = Alignment(vertical="center")
				if (cell.column == 'A' or cell.column in centerAlign) and cell.row<=last_row_table:
					cell.alignment = Alignment(wrapText=True, horizontal="center", vertical="center")
					cell.font = Font(name='Arial',size=10,italic=Table_italic)
				if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column != 'B':
					cell.font = Font(name='Arial',size=10,italic=Table_italic)
					cell.alignment = Alignment(wrapText=True, horizontal="center", vertical="center")
				if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column == 'B':
					cell.font = Font(name='Arial',size=10,italic=Table_italic)
					cell.alignment = Alignment(wrapText=True, horizontal=align, vertical="center")
				if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column == 'K':
					cell.font = Font(name='Arial',size=10,italic=Table_italic,color='808080')
					cell.alignment = Alignment(wrapText=True, horizontal="center", vertical="center")
		for rows in ws.iter_rows(min_row=last_row_table-len_table, max_row=last_row_table-len_table, min_col=None,max_col=max_col_table):
			for cell in rows:
				cell.fill = PatternFill('solid', fgColor="F2F2F2")
				cell.alignment = Alignment(wrapText=True, horizontal="center", vertical="center")
				cell.font = Font(size=10, bold=True, name='Arial')
		ws['A'+str(last_row_table+1)].alignment = Alignment(horizontal='right')
		ws['C'+str(last_row_table+indent-1)].alignment = Alignment(horizontal='center',vertical="center")
		ws['D'+str(last_row_table-len_table)].alignment = Alignment(wrapText=True, horizontal="center", vertical="center")


	thin = Side(border_style="thin")
	month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
	report_date = 'с 1 по ' + str(calendar.monthrange(int(request.POST.getlist('to_date')[0].split('-')[0]),int(request.POST.getlist('to_date')[0].split('-')[1]))[1]) + ' ' + str(month_list[int(request.POST.getlist('to_date')[0].split('-')[1])-1]) + ' ' + str(request.POST.getlist('to_date')[0].split('-')[0]) + ' г.'
	mkday = datetime.date.today().strftime("%d.%m.%Y")
	count_oo_rows = 1
	date_from = request.POST.getlist('from_date')[0]
	date_to = request.POST.getlist('to_date')[0]
	
	base_users = get_active_user(request)
	
	
	do_filter = Q()
	do_name_dump_filter = Q()
	do_name_filter = Q()
	slave_do_filter = Q()
	do_name_list_short = do_name_list_full = do_name_list_space = re.split(' |-', request.POST.getlist('req_do')[0].replace('«','').replace('»','').replace('"',''))
	def remove_sm(do_list):
		to_remove = ['филиал', 'в', 'г.Омск' ]
		for item in to_remove:
			if item in do_list:
				do_list.remove(item)
		return do_list

	if "ГПН" in do_name_list_full:
		do_name_list_space = list(map(lambda x: x.replace('ГПН', 'Газпром нефть'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('ГПН', 'Газпромнефть'), do_name_list_short))
	elif "Газпромнефть" in do_name_list_full:
		do_name_list_space = list(map(lambda x: x.replace('Газпромнефть', 'Газпром нефть'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('Газпромнефть', 'ГПН'), do_name_list_short))
	elif "Газпром нефть" in do_name_list_full:
		do_name_list_space = list(map(lambda x: x.replace('Газпром нефть', 'Газпромнефть'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('Газпром нефть', 'ГПН'), do_name_list_short))
		
	if "БМ" in do_name_list_full:
		do_name_list_full = list(map(lambda x: x.replace('БМ', 'Битумные материалы'), do_name_list_full))
		do_name_list_space = list(map(lambda x: x.replace('БМ', 'Битумные материалы'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('БМ', 'Битумные материалы'), do_name_list_short))
	elif "Каталитические" in do_name_list_full:
		do_name_list_full.remove("системы")
		do_name_list_space.remove("системы")
		do_name_list_short.remove("системы")
		do_name_list_full = list(map(lambda x: x.replace('Каталитические', 'КС'), do_name_list_full))
		do_name_list_space = list(map(lambda x: x.replace('Каталитические', 'КС'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('Каталитические', 'КС'), do_name_list_short))
	elif "смазочные" in do_name_list_full:
		do_name_list_full.remove("материалы")
		do_name_list_space.remove("материалы")
		do_name_list_short.remove("материалы")
		do_name_list_full = list(map(lambda x: x.replace('смазочные', 'СМ'), do_name_list_full))
		do_name_list_space = list(map(lambda x: x.replace('смазочные', 'СМ'), do_name_list_space))
		do_name_list_short = list(map(lambda x: x.replace('смазочные', 'СМ'), do_name_list_short))
		do_name_list_full = remove_sm(do_name_list_full)
		do_name_list_short = remove_sm(do_name_list_short)
		do_name_list_space = remove_sm(do_name_list_space)
	elif "Лахта" in do_name_list_full:
		do_name_list_full = ['ООО', 'ЦИСК']
		do_name_list_space = ['ООО', 'ЦИСК']
		do_name_list_short = ['ООО', 'ЦИСК']
	elif "Рязанский" in do_name_list_full:
		do_name_list_full = ['ООО', 'ГПН', 'РЗБМ']
		do_name_list_space = ['ООО', 'ГПН', 'РЗБМ']
		do_name_list_short = ['ООО', 'ГПН', 'РЗБМ']
	
	for word in do_name_list_full:
		do_name_dump_filter &= Q(**{'company_master__icontains':word})
	do_name_filter |= do_name_dump_filter
	do_name_dump_filter = Q()
	for word in do_name_list_short:
		do_name_dump_filter &= Q(**{'company_master__icontains':word})
	do_name_filter |= do_name_dump_filter
	do_name_dump_filter = Q()
	for word in do_name_list_space:
		do_name_dump_filter &= Q(**{'company_master__icontains':word})
	do_name_filter |= do_name_dump_filter
	do_name_dump_filter = Q()
	logger.info(f'{do_name_filter} | {request.POST.dict()} | {request.META}')
	if suid_catalog.objects.filter(do_name_filter).first() == None:
		return HttpResponse('{"error":"Couldn\'t search this Company in Catalog. Update Catalog SUID"}', content_type='application/json', status=200)
	else:
		get_company_master = suid_catalog.objects.filter(do_name_filter).first().company_master
	slaves_companys = list((x[0]) for x in suid_catalog.objects.filter(company_master__iexact = get_company_master).values_list('company_slave'))
	
	for company in slaves_companys:
		slave_name_list  =re.split(' |-', company.replace('«','').replace('»','').replace('"',''))
		for word in slave_name_list:
			slave_do_filter &= Q(**{'company__icontains':word})
		do_filter |= slave_do_filter
		slave_do_filter = Q()
	
	suid_do_users = dict((x.lower(), y) for x, y in suid_users.objects.filter(do_filter).values_list('login', 'email'))
	local_do_users = dict((x.lower(), y) for x, y in User.objects.filter(do_filter).filter(visible__exact=True).values_list('login', 'email'))
	
	all_users_to_report={}
	all_users_to_report.update(suid_do_users)
	all_users_to_report.update(local_do_users)
	
	
	last_row =0
	MRH = 25
	LRH = 51
	extcountCalls = 0
#	ext =['ГПН-ЦР Москва Телемост', 'ГПН-ЦР СПб Телемост 02', 'ГПН-ЦР СПб Телемост', 'ГПН-ЦР Тюмень Телемост', 'ГПН-ЦР Уфа Телемост', 'ГПН-ЦР Екб Телемост']
	ext =[]
	extcount = 0
	for do in [request.POST.getlist('req_do')[0]]:
		if do == 'Газпромнефть НТЦ ООО':
			Json_data = endpointSerializer(ksuit.objects.filter(Q(do_name__istartswith='Газпромнефть НТЦ')).filter(active=True), many=True).data
		elif do == 'Газпромнефть-смазочные материалы ООО':
			Json_data = endpointSerializer(ksuit.objects.filter(Q(do_name__iexact='Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО') | Q(do_name__iexact='Газпромнефть-смазочные материалы ООО')).filter(active=True), many=True).data
		elif do == 'Газпромнефть-Ноябрьскнефтегаз АО':
			Json_data = endpointSerializer(ksuit.objects.filter(Q(do_name__iexact='Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО') | Q(do_name__iexact='Газпромнефть-Ноябрьскнефтегаз АО')).filter(active=True), many=True).data
		elif do =='Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО' or do == 'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО' or do == 'Газпромнефть НТЦ обособленное подразделение в г. Тюмень ООО' or do == 'Автоматика-сервис ООО':
			continue
		else:
			Json_data = endpointSerializer(ksuit.objects.filter(do_name__iexact=do).filter(active=True), many=True).data
		response = Json_data
		wb = openpyxl.Workbook()
		ws = wb.active

		HSO = ['№ п/п', 'Наименование терминала (из КСУИТ)', 'Производитель', 'Модель', 'Сетевой адрес', 'Серийный номер', 'Фактический адрес установки']

		ReportTable = [['№ п/п','Наименование услуги','Код операционной услуги','Единица измерения','Объем потребления','Стоимость услуги','Сумма','','','','','','','','',''],[1,'Обслуживание аппаратных абонентских терминалов','MEET.VKS-HARDTERMINAL@CORP','терминал','=count(Table1[№ П/П])',5530.77,'=F17*E17','','','','','','','','',''],[2,'Обслуживание программных абонентских терминалов','MEET.VKS-SOFTTERMINAL@CORP','терминал','=count(Table3[№ П/П])',1055.70,'=F18*E18','','','','','','','','',''],['Итого:','','','','','','=SUM(G17:G18)','','','','','','','','',''],['','','','','','','','','','','','','','','',''],['Таблица 1.2. – Перечень аппаратных абонентских терминалов ВКС за отчётный период','','','','','','','','','','','','','','','']]

		PSO = [['','','','','','','','','','','','','','','',''],['Таблица 1.3. – Перечень программных абонентских терминалов ВКС за отчётный период','','','','','','','','','','','','','','',''],['№ п/п','ФИО','Логин','Почта','Компания','Сервер','Время','','','','','','','',''],['Итого программных терминалов:','','','','','','=count(Table3[№ П/П])','','','','','','','',''],['','','','','','','','','','','','','','','']]

		tData = [ ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', 'Отчет за ', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Услуга:', '', '\"Предоставление доступа к платформе видеоконференций\"', '', '', '', '', '', '', '', '', ''], ['Номер Договора:', '', '_______________________________________', '', '', '', '', '', '', '', '', ''], ['Отчетный период:', '', report_date, '', '', '', '', '', '', '', '', ''], ['Дата формирования:', '', mkday , '', '', '', '', '', '', '', '', ''], ['Номер сделки для актирования:', '', 'SERV.VKS.23009' , '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Отчет по услуге №____ для '+ do, '', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Сервис-менеджер:', '', 'Колесник Георгий Вячеславович', '', '', '', '', '', '', '', '', ''], ['Период предоставления', '', 'Ежемесячно', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Таблица 1.1. – Отчет по потреблению услуги', '', '', '', '', '', '', '', '', '', '']]

		tfooter = [['','','',''],['Таблица 1.4 – Отчет по Инцидентам','','',''],['№ п/п','Номер','Краткое описание ','Статус'],[1,'Инцидентов за указанный период не зарегистрировано.','',''],['Итого инцидентов:','','',0],['','','',''],['','','',''],['Таблица 1.5 – Отчет по Проблемам','','',''],['№ п/п','Номер','Краткое описание ','Статус'],[1,'Проблем за указанный период не зарегистрировано.','',''],['Итого проблем:','','',0],['','','','']]
		tData[1][3] += getmonth() + ' ' + request.POST.getlist('to_date')[0].split('-')[0] + ' г.'
		for elem in tData:
			ws.append(elem)
			last_row += 1
		for elem in ReportTable:
			ws.append(elem)
			last_row += 1
		format_Table(2,ws.max_row-3,7,0,True)
		ws.append(HSO)
		last_row += 1
		ws['F17'].number_format = '''# ### ##0.00 \u20bd'''
		ws['F18'].number_format = '''# ### ##0.00 \u20bd'''
		ws['G17'].number_format = '''# ### ##0.00 \u20bd'''
		ws['G18'].number_format = '''# ### ##0.00 \u20bd'''
		ws['G19'].number_format = '''# ### ##0.00 \u20bd'''
		ws.column_dimensions['A'].width = 6
		ws.column_dimensions['B'].width = 75
		ws.column_dimensions['C'].width = 36
		ws.column_dimensions['D'].width = 32
		ws.column_dimensions['E'].width = 24
		ws.column_dimensions['F'].width = 24
		ws.column_dimensions['G'].width = 45
		ws.row_dimensions[2].height = 20.25 #Высота строки 12
		ws.row_dimensions[23].height = 30 #Высота строки 33
		ws['E17'].alignment = Alignment(horizontal='right')
		ws['E18'].alignment = Alignment(horizontal='right')
		ws['F17'].alignment = Alignment(horizontal='right')
		ws['F18'].alignment = Alignment(horizontal='right')
		ws['G17'].alignment = Alignment(horizontal='right')
		ws['G18'].alignment = Alignment(horizontal='right')
		ws['C17'].alignment = Alignment(horizontal='left')
		ws['C18'].alignment = Alignment(horizontal='left')
		ws['A21'].font = Font(size=11, bold=True, name='Arial')
		for elem in response:
			if elem['name'] not in ext:
				val_row1 = dict(elem.items())
				val_row2 = dict(val_row1['reg_ip'].items()) if val_row1['reg_ip'] != None else {'id_manufacturer':None, 'id_model':None, 'serial_number':None}
				row = [count_oo_rows, val_row1['name'], val_row2['id_manufacturer'], val_row2['id_model'], val_row1['ip'], val_row2['serial_number'], val_row1['address']]
				count_oo_rows += 1
				ws.append(row)
				if 'Требуется замена, т.к. оборудование официально признано устаревшим (EOL) и СПИ истёк' in row:
					ws.row_dimensions[ws.max_row].height = LRH
				else:
					ws.row_dimensions[ws.max_row].height = MRH
				last_row += 1
			else:
				extcount += 1
		count_oo_rows = 1
		ws.append(['Итого аппаратных терминалов: ','','','','','','=count(Table1[№ П/П])'])
		ws.append([''])
		ws.row_dimensions[len(response) + 38 - extcount].height = 55 #высота строки шапки 1.4
		last_row += 2
		for row in ws['A1:G16']:
			for cell in row:
				cell.font = Font(size=12, name='Arial')
				if cell.row == 10 or cell.row == 15:
					cell.font = Font(size=11, bold=True, name='Arial')
		ws['D2'].alignment = Alignment(horizontal='center',vertical='center')
		ws['D2'].font = Font(size=16, bold=True, name='Arial')

		format_Table(len(response)-extcount,ws.max_row-2,7,0,True,Table_italic=True, align_result='left')
		ws['G'+str(last_row-1)].alignment = Alignment(horizontal='left')
		ws['D'+str(last_row-1)].alignment = Alignment(horizontal='left')
		ws['B'+str(last_row-1)].alignment = Alignment(horizontal='right')
		ws['D2'].alignment = Alignment(horizontal='center')
		ws['D18'].alignment = Alignment(wrapText=True, horizontal='center',vertical='center')
		ws['D19'].alignment = Alignment(wrapText=True, horizontal='center',vertical='center')
		tab = Table(displayName="Table1", ref="A22:G"+str(len(response)+22 - extcount))
		ws.add_table(tab)

		tc_users_count = 0

		for user in all_users_to_report:
			if user.lower() in base_users:
				base_user = User.objects.filter(email=all_users_to_report.get(user)).values_list('fio', 'login', 'email', 'company', 'attribute', 'login_data')
				if bool(base_user):
					tc_users_count += 1
					PSO.insert(2+tc_users_count,[tc_users_count,base_user[0][0],base_user[0][1],base_user[0][2],base_user[0][3],base_users[user][0],base_users[user][1]])
		tc_users_header = last_row
		for elem in PSO:
			ws.append(elem)
			last_row += 1

		tab2 = Table(displayName="Table3", ref="A" + str(tc_users_header+3) + ":G" + str(last_row - 2))
		ws.add_table(tab2)

		for elem in tfooter:
			ws.append(elem)
			last_row += 1
		format_Table(1,ws.max_row-2,4,merge=True,align='center')
		format_Table(1,ws.max_row-8,4,merge=True,align='center')
		format_Table(len(PSO)-5,ws.max_row-14,7,merge=True,align='center',align_result='left')
		ws['A' + str(ws.max_row-4)].font = Font(size=11, bold=True, name='Arial')
		ws['A' + str(ws.max_row-10)].font = Font(size=11, bold=True, name='Arial')
		ws['A' + str(ws.max_row-15-tc_users_count)].font = Font(size=11, bold=True, name='Arial')
		ws['G' + str(ws.max_row-13)].alignment = Alignment(wrapText=True, horizontal='left',vertical='center')
		ws['D' + str(ws.max_row-7)].alignment = Alignment(wrapText=True, horizontal='left',vertical='center')
		ws['D' + str(ws.max_row-1)].alignment = Alignment(wrapText=True, horizontal='left',vertical='center')
		ws.title ='Отчет'
		count_oo_rows = 1
		last_row = 0
		extcount = 0
		extcountCalls = 0
		wb.save("/var/www/VCS_Portal/static/Reports/ВКС "+str(do)+".xlsx")
		wb.save(resp)
		wb.close()

		return resp



def get_update_time(request):
	app_row = {}

	def serialize_datetime(obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		raise TypeError("Type not serializable")

	response = get_req_to_db(0,"select * from times")
	for row in response:
		app_row.update({row[0]:row[1]})
	app_row.update({"SUID_Table":table_files.objects.order_by("-actualization").first().actualization})
	return HttpResponse(json.dumps(app_row, ensure_ascii=False,default=serialize_datetime).encode('utf-8').decode(), content_type='application/json')


def get_do(request):

	ret = ''
	response = get_req_to_db(0,'select DISTINCT do_name from "Poly_ksuit" where not (do_name = \'Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО\' or do_name = \'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО\' or do_name = \'Газпромнефть НТЦ обособленное подразделение в г. Тюмень ООО\' or do_name = \'Автоматика-сервис ООО\') order by do_name')
	for row in response:
		for cell in row:
			ret+='<option>'+cell+'</option>\n'
	return HttpResponse(ret, content_type="text/html")



def report_active_user(request):
	array = []
	users_dict = {}
	users_do_arr = {}
	count_users = 0
	if request == False:
		date_to = datetime.date.today()
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	elif isinstance(request, str):
		date_to = datetime.datetime.strptime(request, '%d.%m.%Y')
		date_from = date_to - datetime.timedelta(days=1)
		wb = openpyxl.Workbook()
		ws = wb.active
	else:
		date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
		date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')
		wb = openpyxl.Workbook()
		ws = wb.active
		array.append(['Дата','Сервер','Число польз.'])
	count_days = (date_to - date_from).days
	resp = HttpResponse(content_type='application/ms-excel')
	resp['Content-Disposition'] = 'attachment; filename="Active_users_TrueConf '+date_from.strftime('%d.%m.%Y')+'.xlsx"'

	for i in range(count_days):
		sel_day = (date_from + datetime.timedelta(days=i)).strftime('%d.%m.%Y')
		query_req = "select count(distinct t.user) from (select split_part(object_name, '@', 1) as user from log.events where created_at between '{}' and '{}' and payload->>'NewStatus' in ('1','2','5') and object_name not ilike '#%') as t".format(date_from + datetime.timedelta(days=i), date_from + datetime.timedelta(days=i+1))

		for serv in range(1,count_servers):
			response = get_req_to_db(serv,query_req)[0][0]
			array.append([sel_day,'Server TC%s'% serv,response])
			count_users += int(response)


	for elem in array:
		ws.append(elem)


	query_req_dict = " select t1.* from (SELECT split_part(object_name, '@', 1) as user, split_part(split_part(object_name, '@', 2), '/',1) as server, created_at AT TIME ZONE 'Europe/Moscow' AS created_at FROM log.events) t1 JOIN (SELECT split_part(object_name, '@', 1) as user, max(created_at AT TIME ZONE 'Europe/Moscow') max_created_at FROM log.events WHERE created_at AT TIME ZONE 'Europe/Moscow' BETWEEN '{}' AND '{}' AND payload->>'NewStatus' IN ('1','2','5') AND object_name NOT ILIKE '#%' GROUP BY split_part(object_name, '@', 1)) t2 ON t1.user = t2.user AND t1.created_at = t2.max_created_at ORDER BY user, t1.created_at DESC;".format(date_from, date_to)


	for serv in range(1,count_servers):
		response = get_req_to_db(serv,query_req_dict)
		for user in response:
			users_dict.update({user[0]:[user[1],user[2]]})
			users_do_arr.update({user[0]:None})

	users_do = User.objects.filter(login__in = list(users_dict.keys()))
	ws2 = wb.create_sheet(title="Пользователи")
	ws2.append(['Логин','Сервер', 'Дата последнего входа'])
	for user in users_dict:
		ws2.append([user,users_dict[user][0],users_dict[user][1]])

	for u in users_do:
		users_do_arr.update({u.login:[u.company, u.email, u.fio]})

	if request == False or isinstance(request, str):
		if request == False:
			report_chat_message_for_user(False)
			report_type_confs(False)
		else:
			report_chat_message_for_user(request)
			report_type_confs(request)

		if 'Sheet' in wb.sheetnames:
			wb.remove(wb['Sheet'])
		wb.save("/var/www/VCS_Portal/static/Reports/Active_Users_TrueConf "+ str(date_from.strftime('%d.%m.%Y')) + ".xlsx")

		wb.close()
		from mail import send_mail
		bodytext ='Уникальных пользователей за ' + str(date_from.strftime('%d.%m.%Y')) + ' - ' + str(len(users_dict)) + '.'

		send_mail('trueconf_push@gazprom-neft.ru', 'Uzenbaev.rm@gazprom-neft.ru,Vatutina.AI@gazprom-neft.ru,Lunina.OA@omsk.gazprom-neft.ru', 'Выгрузка активых пользователей TrueConf',bodytext,'trueconf_push', 'AsdfMovie123', 'asmtp.gazprom-neft.local','/var/www/VCS_Portal/static/Reports/Active_Users_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx,/var/www/VCS_Portal/static/Reports/Messages_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx,/var/www/VCS_Portal/static/Reports/Conferences_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx')
#		send_mail('trueconf_push@gazprom-neft.ru', 'Uzenbaev.rm@gazprom-neft.ru', 'Выгрузка активых пользователей TrueConf',bodytext,'trueconf_push', 'o5bUkxLFLO44h$ia4yx', 'asmtp.gazprom-neft.local','/var/www/VCS_Portal/static/Reports/Active_Users_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx,/var/www/VCS_Portal/static/Reports/Messages_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx,/var/www/VCS_Portal/static/Reports/Conferences_TrueConf '+ str(date_from.strftime('%d.%m.%Y')) + '.xlsx')
	else:
		wb.save(resp)
		wb.close()
		usr=[]
		for u in users_dict:
			usr.append([users_do_arr[u][2],u,users_do_arr[u][1],users_do_arr[u][0],users_dict[u][0],users_dict[u][1]])

		json_var = json.dumps(usr,default=str)

		return JsonResponse(json_var, safe=False)

def get_active_user(request):
	users_dict = {}
	date_from = datetime.datetime.strptime(request.POST.getlist('from_date')[0],'%Y-%m-%d')
	date_to = datetime.datetime.strptime(request.POST.getlist('to_date')[0],'%Y-%m-%d')

	query_req_dict = " select t1.* from (SELECT split_part(object_name, '@', 1) as user, split_part(split_part(object_name, '@', 2), '/',1) as server, created_at AT TIME ZONE 'Europe/Moscow' AS created_at FROM log.events) t1 JOIN (SELECT split_part(object_name, '@', 1) as user, max(created_at AT TIME ZONE 'Europe/Moscow') max_created_at FROM log.events WHERE created_at AT TIME ZONE 'Europe/Moscow' BETWEEN '{}' AND '{}' AND payload->>'NewStatus' IN ('1','2','5') AND object_name NOT ILIKE '#%' GROUP BY split_part(object_name, '@', 1)) t2 ON t1.user = t2.user AND t1.created_at = t2.max_created_at ORDER BY user, t1.created_at DESC;".format(date_from, date_to)

	for serv in range(1,count_servers):
		response = get_req_to_db(serv,query_req_dict)
		for user in response:
			users_dict.update({user[0].lower():[user[1],user[2]]})
	return users_dict

def edit_endpoint(request):
	auth, user = cred(request)
	id = request.POST.getlist('endpoint_id')[0]
	reg_id = ksuit.objects.filter(id=id).values_list('reg_ip_id')[0]
	def serialize_datetime(obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		return "Type not serializable"
	if auth != 'User':

		finaly_rows, count, filtered, columns, name = get_users(request=request)
		Json_data = json.dumps((EditEndpointSerializer(finaly_rows, many=True).data[0], list(terminal_model.objects.all().order_by("id").values()), list(manufacturer.objects.all().order_by("id").values()), list(subnet_mask.objects.order_by("id").all().values()), list(do_reg.objects.all().order_by("id").values()), list(type_cabinet.objects.all().order_by("id").values()), list(physical_address.objects.all().order_by("id").values()), list(group_networker.objects.all().order_by("id").values()), list(subnet_mask.objects.all().order_by("id").values()), list(service_wg.objects.all().order_by("id").values()), list(logs.objects.filter(reg_ip=reg_id[0]).order_by("date").values())), default=serialize_datetime)
		json_var = '{"data":'+ Json_data + '}'

		return HttpResponse(json_var, content_type='application/json')

	else: return JsonResponse(['Unauthorized'], safe=False)

def save_endpoint(request):
	auth, user = cred(request)
	id = request.POST.get('ksuit_key')
	not_same = ['id_do','id_manufacturer','id_model','id_networker','id_physical_address','id_service_wg','id_subnet_mask','id_type_cabinet']
	test = []
	def serialize_datetime(obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		return "Type not serializable"

	def ser_val(obj_arg, value, name_response, dict=False):
		if obj_arg == 'id_model':
			ret_val = terminal_model.objects.filter(id=value).get().name if name_response else terminal_model.objects.filter(id=value).get()
		elif obj_arg == 'id_do':
			ret_val = do_reg.objects.filter(id=value).get().name if name_response else do_reg.objects.filter(id=value).get()
		elif obj_arg == 'id_manufacturer':
			ret_val = manufacturer.objects.filter(id=value).get().name if name_response else manufacturer.objects.filter(id=value).get()
		elif obj_arg == 'id_networker':
			ret_val = group_networker.objects.filter(id=value).get().name if name_response else group_networker.objects.filter(id=value).get()
		elif obj_arg == 'id_physical_address':
			ret_val = physical_address.objects.filter(id=value).get().name if name_response else physical_address.objects.filter(id=value).get()
		elif obj_arg == 'id_service_wg':
			ret_val = service_wg.objects.filter(id=value).get().name if name_response else service_wg.objects.filter(id=value).get()
		elif obj_arg == 'id_subnet_mask':
			ret_val = subnet_mask.objects.filter(id=value).get().name if name_response else subnet_mask.objects.filter(id=value).get()
		elif obj_arg == 'id_subnet_vlan_vks':
			ret_val = subnet_mask.objects.filter(id=value).get().name if name_response else subnet_mask.objects.filter(id=value).get()
		elif obj_arg == 'id_type_cabinet':
			ret_val = type_cabinet.objects.filter(id=value).get().name if name_response else type_cabinet.objects.filter(id=value).get()
		elif obj_arg == 'registry_key':
			obj_arg = 'terminal_id'
			ret_val = value
		else:
			ret_val = value

		return {obj_arg : ret_val} if dict else ret_val

	if auth != 'User':
		change_date=datetime.datetime.now()
		if request.POST.get('registry_key') != '':
			for key, value in dict(request.POST.items()).items():
				try:
					original_value = registry.objects.filter(terminal_id=request.POST.get('registry_key')).values_list(key[3:], flat=True)[0]
					if original_value == None: original_value = ''
					if str(original_value).lower() != str(value).lower():
						value = True if value.lower() == 'true' else False if value.lower() == 'false' else value
						obj_arg = key.split('FT_')[1] if len(key.split('FT_')) > 1 else key
						test.append((f'{user} changed {key}',f'from {ser_val(obj_arg,original_value, True)} to {ser_val(obj_arg,value, True)} at {change_date}' ))
						logs.objects.create(name=user, cmd=obj_arg, reg_ip=registry.objects.filter(terminal_id=request.POST.get('registry_key')).get(),old_value=ser_val(obj_arg,original_value,True), new_value=ser_val(obj_arg,value,True), date=change_date, type='change')
						registry.objects.filter(terminal_id=request.POST.get('registry_key')).update(**{obj_arg:value})
				except FieldError:
					continue
			if len(test) > 0: registry.objects.filter(terminal_id=request.POST.get('registry_key')).update(actualization = datetime.datetime.now())
			Json_data = json.dumps(dict(test),default=serialize_datetime)
			return HttpResponse(Json_data, content_type='application/json')
		else:
			upd_args = {}
			multiple_except = {}
			for key, value in dict(request.POST.items()).items():
				if value != '':
					obj_arg = key.split('FT_')[1].lower() if len(key.split('FT_')) > 1 else key.lower()
					upd_args.update(ser_val(obj_arg,value, False, True))
					if obj_arg in ['serial_number','terminal_name','system_name','h323_name','mac_address','e164_number','ip_address','sip_address','service_key_update'] and registry.objects.filter(**{obj_arg:value}).exists():
						multiple_except.update({obj_arg : value})
			[upd_args.pop(key, None) for key in ['csrfmiddlewaretoken','ksuit_key']]
			if len(multiple_except) < 1:
				create_elem = registry.objects.create(**upd_args)
				for key, value in upd_args.items():
					logs.objects.create(name=user, cmd=key, reg_ip=registry.objects.filter(terminal_id=create_elem.terminal_id).get(),old_value=None, new_value=value, date=change_date, type='create')
				create_elem = {'success':create_elem.terminal_id}
			else:
				create_elem = {'error':multiple_except}
			return HttpResponse(json.dumps(create_elem), content_type='application/json')

	else: return JsonResponse(['Unauthorized'], safe=False)
