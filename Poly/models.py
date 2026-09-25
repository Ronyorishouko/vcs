from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import datetime as dtm
from req_to_all_db import get_req_to_db
import subprocess, codecs, requests, re,sys, io, app_logger
sys.path.append("/var/www/VCS_Portal/static/scripts")

logger = app_logger.get_logger(__name__, '/var/log/VCS_portal/VCS_portal_Poly_Models.log')

list_do={}
list_name={}
Registry_SIP = {}
Registry_Name = {}
KSUIT=[]
other=[]

class table_files(models.Model):
	title = models.CharField(max_length=150)
	table_file = models.FileField(upload_to='suid_tables/')
	actualization = models.DateTimeField(blank=True, null=True)
	uploader = models.CharField(blank=True, null=True, max_length=150)

	def __str__(self):
		return str(self.table_file)

class catalog_do_file(models.Model):
	title = models.CharField(max_length=150)
	table_file = models.FileField(upload_to='suid_catalog/')
	actualization = models.DateTimeField(blank=True, null=True)
	uploader = models.CharField(max_length=150)

	def __str__(self):
		return str(self.table_file)
	
class suid_catalog(models.Model):
	company_master = models.CharField(max_length=200,blank=True, null=True)
	company_slave = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return f"{self.company_slave} -> {self.company_master}"
	
class suid_users(models.Model):
	company = models.CharField(max_length=200,blank=True, null=True)
	login  = models.CharField(max_length=200,unique=True)
	email = models.CharField(max_length=200,blank=True, null=True)
	user = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.login
	
class physical_address(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)

	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Physical_address_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Physical_address_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = physical_address(id = vcs[0], name = vcs[1])
			row_other.save()
			
class type_cabinet(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Type_cabinet_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Type_cabinet_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = type_cabinet(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class service_wg(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Service_WG_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Service_WG_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = service_wg(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []
	
class do_reg(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Do_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Do_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = do_reg(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class manufacturer(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Manufacturer_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Manufacturer_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = manufacturer(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class terminal_model(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','Model_Reg'])
		file = io.open('/var/www/VCS_Portal/media/Model_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = terminal_model(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class subnet_mask(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','SubnetMask_Reg'])
		file = io.open('/var/www/VCS_Portal/media/SubnetMask_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = subnet_mask(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class group_networker(models.Model):
	id = models.IntegerField(primary_key=True)
	name  = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	def update():
		other=[]
#		subprocess.call(['./Poly/SQL_other.sh','GroupNetworker_Reg'])
		file = io.open('/var/www/VCS_Portal/media/GroupNetworker_Reg.txt', mode = 'r', encoding='utf-8')
		lines = file.readlines()
		for row in range(9, len(lines)-1):
			termInfo = lines[row].split('|')
			other.append([termInfo[0],termInfo[1][:-1]])
		file.close()
		for vcs in other:
			row_other = group_networker(id = vcs[0], name = vcs[1])
			row_other.save()
		other = []

class registry(models.Model):
	terminal_name = models.CharField(max_length=200,blank=True, null=True)
	system_name = models.CharField(max_length=200,blank=True, null=True)
	h323_name = models.CharField(max_length=200,blank=True, null=True)
	software_version = models.CharField(max_length=200,blank=True, null=True)
	hardware_version = models.CharField(max_length=200,blank=True, null=True)
	serial_number = models.CharField(max_length=200,blank=True, null=True)
	mac_address = models.CharField(max_length=200,blank=True, null=True)
	registration_gatekeeper = models.CharField(max_length=200,blank=True, null=True)
	e164_number = models.CharField(max_length=200,blank=True, null=True)
	ip_address = models.CharField(max_length=200,blank=True, null=True)
	dhcp = models.BooleanField(default=False)
	sip_address = models.CharField(max_length=200,blank=True, null=True)
	default_gateway = models.CharField(max_length=200,blank=True, null=True)
	snmp_version = models.CharField(max_length=200,blank=True, null=True)
	account_ad = models.CharField(max_length=200,blank=True, null=True)
	provisioning = models.BooleanField(default=False)
	snmp_monitoring = models.BooleanField(default=False)
	qos = models.BooleanField(default=False)
	sip_registrar = models.CharField(max_length=200,blank=True, null=True)
	sip_proxy = models.CharField(max_length=200,blank=True, null=True)
	site = models.CharField(max_length=200,blank=True, null=True)
	field_notes = models.CharField(max_length=200,blank=True, null=True)
	id_manufacturer = models.ForeignKey(manufacturer, on_delete = models.CASCADE,blank=True, null=True)
	id_model = models.ForeignKey(terminal_model, on_delete = models.CASCADE,blank=True, null=True)
	id_physical_address = models.ForeignKey(physical_address, on_delete = models.CASCADE,blank=True, null=True)
	id_type_cabinet = models.ForeignKey(type_cabinet, on_delete = models.CASCADE,blank=True, null=True)
	id_do = models.ForeignKey(do_reg, on_delete = models.CASCADE,blank=True, null=True)
	id_log = models.CharField(max_length=200,blank=True, null=True)
	id_subnet_mask = models.ForeignKey(subnet_mask, on_delete = models.CASCADE,blank=True, null=True)
	id_subnet_vlan_vks = models.CharField(max_length=200,blank=True, null=True)
	id_networker = models.ForeignKey(group_networker, on_delete = models.CASCADE,blank=True, null=True)
	id_service_wg = models.ForeignKey(service_wg, on_delete = models.CASCADE,blank=True, null=True)
	id_service_manager = models.CharField(max_length=200,blank=True, null=True)
	number_vlan = models.CharField(max_length=200,blank=True, null=True)
	vlan_vks = models.CharField(max_length=200,blank=True, null=True)
	service_number_contract_ito = models.CharField(max_length=200,blank=True, null=True)
	service_number_contract_cr = models.CharField(max_length=200,blank=True, null=True)
	service_term_contract_ito = models.CharField(max_length=200,blank=True, null=True)
	service_term_contract_cr = models.CharField(max_length=200,blank=True, null=True)
	service_number_deal_ito = models.CharField(max_length=200,blank=True, null=True)
	service_number_deal_cr = models.CharField(max_length=200,blank=True, null=True)
	service_distr_number = models.CharField(max_length=200,blank=True, null=True)
	service_distr_contract_start = models.DateField(blank=True, null=True)
	service_date_contract_end = models.DateField(blank=True, null=True)
	service_key_update = models.CharField(max_length=200,blank=True, null=True)
	actualization = models.DateField(blank=True, null=True)
#	terminal_id = models.IntegerField(primary_key=True)
	terminal_id = models.AutoField(primary_key=True)
	
	def __str__(self):
		return self.terminal_name
	
	def update():
		logger.info("Start update Registry")
		
		physical_address.update()
		type_cabinet.update()
		service_wg.update()
		do_reg.update()
		manufacturer.update()
		terminal_model.update()
		group_networker.update()
		subnet_mask.update()
		Registry_array=[]
#		subprocess.call(['./Poly/SQL_Registry.sh'])
		file = codecs.open('/var/www/VCS_Portal/media/Registry.txt', 'r')
		lines = file.readlines()
		for row in range(1, len(lines)):
			termInfo = [row.strip() if row.strip() != '' else None for row in lines[row].split('|')]
			Registry_array.append(termInfo)
		file.close()
#		Registry_array
		for registry_row in Registry_array:
			snmp = registry_row[16] if registry_row[16] != None else False
			qos = registry_row[17] if registry_row[17] != None else False
			dhcp = registry_row[10] if registry_row[10] != None else False
			provisioning = registry_row[15] if registry_row[15] != None else False
			id_manufacturer = manufacturer.objects.get(id=registry_row[22])
			id_model = terminal_model.objects.get(id=registry_row[23])
			id_physical_address = physical_address.objects.get(id=registry_row[24])
			id_type_cabinet = type_cabinet.objects.get(id=registry_row[25])
			id_do = do_reg.objects.get(id=registry_row[26])
			id_subnet_mask = subnet_mask.objects.get(id=registry_row[29])
			id_networker = group_networker.objects.get(id=registry_row[31])
			id_service_wg = service_wg.objects.get(id=registry_row[32])
			registry_elem, create_reg_elem = registry.objects.update_or_create(terminal_id = registry_row[28], defaults={'terminal_name' : registry_row[0], 'system_name' : registry_row[1], 'h323_name' : registry_row[2], 'software_version' : registry_row[3], 'hardware_version' : registry_row[4], 'serial_number' : registry_row[5], 'mac_address' : registry_row[6], 'registration_gatekeeper' : registry_row[7], 'e164_number' : registry_row[8], 'ip_address' : registry_row[9], 'dhcp' : dhcp, 'sip_address' : registry_row[11], 'default_gateway' : registry_row[12], 'snmp_version' : registry_row[13], 'account_ad' : registry_row[14], 'provisioning' : provisioning, 'snmp_monitoring' : snmp, 'qos' : qos, 'sip_registrar' : registry_row[18], 'sip_proxy' : registry_row[19], 'site' : registry_row[20], 'field_notes' : registry_row[21], 'id_manufacturer' : id_manufacturer, 'id_model' : id_model, 'id_physical_address' : id_physical_address, 'id_type_cabinet' : id_type_cabinet, 'id_do' : id_do, 'id_log' : registry_row[27], 'id_subnet_mask' : id_subnet_mask, 'id_subnet_vlan_vks' : registry_row[30], 'id_networker' : id_networker, 'id_service_wg' : id_service_wg, 'id_service_manager' : registry_row[33], 'number_vlan' : registry_row[34], 'vlan_vks' : registry_row[35], 'service_number_contract_ito' : registry_row[36], 'service_number_contract_cr' : registry_row[37], 'service_term_contract_ito' : registry_row[38], 'service_term_contract_cr' : registry_row[39], 'service_number_deal_ito' : registry_row[40], 'service_number_deal_cr' : registry_row[41], 'service_distr_number' : registry_row[42], 'service_distr_contract_start' : registry_row[43], 'service_date_contract_end' : registry_row[44], 'service_key_update' : registry_row[45], 'actualization' : registry_row[46]})
			registry_elem.save()
		logger.info("DONE update Registry sub catalogs")

class ksuit(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200,blank=True, null=True)
	ip = models.CharField(max_length=200,blank=True, null=True)
	address = models.CharField(max_length=200,blank=True, null=True)
	wg = models.CharField(max_length=200,blank=True, null=True)
	do_name = models.CharField(max_length=200,blank=True, null=True)
	address2 = models.CharField(max_length=200,blank=True, null=True)
	active = models.BooleanField(default=True)
	lastUsr  = models.CharField(max_length=200,blank=True, null=True)
	reg_ip = models.ForeignKey(registry, on_delete = models.CASCADE,blank=True, null=True,default=1143)
#	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def update():
		logger.info("Start update ksuit")
		file = codecs.open('/var/www/VCS_Portal/media/KSUIT.txt', 'r')
		ksuit_terminals = 0
		KSUIT = []
		while True:
			line = file.readline()
			if not line:
				break
			KSUIT.append(line.strip().split('\\'))
			ksuit_terminals += 1

		file.close()
		KSUIT.pop(0)

#		ksuit.objects.all().delete()
		for vcs in range(0, len(KSUIT)):
			reg_ip = None
			if KSUIT[vcs][7] == 'Да':
				val_active = True
			else:
				val_active = False

			try:
				reg_ip = registry.objects.get(ip_address=KSUIT[vcs][2])
			except ObjectDoesNotExist:
				reg_ip = registry.objects.get(terminal_id=1143)
				pass
			except MultipleObjectsReturned:
				reg_ip = registry.objects.get(terminal_id=1143)
				pass
			ksuit_elem, create_ksuit_elem = ksuit.objects.update_or_create(id = KSUIT[vcs][0], defaults={'name' : KSUIT[vcs][1], 'ip' : KSUIT[vcs][2], 'address' : KSUIT[vcs][3], 'wg' : KSUIT[vcs][4], 'do_name' : KSUIT[vcs][5], 'address2' : KSUIT[vcs][6], 'active' : val_active, 'lastUsr' : KSUIT[vcs][8], 'reg_ip':reg_ip})

		logger.info("DONE update ksuit")

	def update_registry():
		logger.info("Start update Registry")
		for ksuit_term in ksuit.objects.all():
			try:
				terminal = registry.objects.get(ip_address=ksuit_term.ip)
				ksuit_term.reg_ip=terminal
				ksuit_term.save()
			except ObjectDoesNotExist:
				if ksuit_term.ip[0] != '0':
					logger.info('Not Find in Registry: '+ksuit_term.ip)
				pass
			except MultipleObjectsReturned:
				logger.info('Dublicate in Registry: '+ksuit_term.ip)
				pass
		logger.info("DONE update Registry")

class maintable(models.Model):
	callidentifier = models.CharField(max_length=200,primary_key=True)
	originator = models.CharField(max_length=200,blank=True, null=True)
	sharedlicensed = models.BooleanField(default=True)
	callsignaling = models.CharField(max_length=200,blank=True, null=True)
	fullyexternal = models.BooleanField(default=True)
	destination = models.CharField(max_length=200,blank=True, null=True)
	nodeid = models.CharField(max_length=200,blank=True, null=True)
	cluster = models.CharField(max_length=200,blank=True, null=True)
	dialstring = models.CharField(max_length=200,blank=True, null=True)
	starttime = models.DateTimeField(blank=True, null=True)
	endtime = models.DateTimeField(blank=True, null=True)
	callstatus = models.CharField(max_length=200,blank=True, null=True)
	conference = models.CharField(max_length=200,blank=True, null=True)
	participant = models.CharField(max_length=200,blank=True, null=True)
	duration = models.DurationField(blank=True, null=True)
	numberdigits = models.CharField(max_length=200,blank=True, null=True)
	do_name = models.CharField(max_length=200,blank=True, null=True)
	ksuit_name = models.CharField(max_length=200,blank=True, null=True)
	orig_devicename = models.CharField(max_length=200,blank=True, null=True)
	orig_deviceidentifier = models.CharField(max_length=200,blank=True, null=True)
	orig_devicemodel = models.CharField(max_length=200,blank=True, null=True)
	orig_aliases = models.CharField(max_length=200,blank=True, null=True)
	orig_site = models.CharField(max_length=200,blank=True, null=True)
	orig_registrationstatus = models.CharField(max_length=200,blank=True, null=True)
	orig_territory = models.CharField(max_length=200,blank=True, null=True)
	orig_ipaddress = models.CharField(max_length=200,blank=True, null=True)
	orig_deviceversion = models.CharField(max_length=200,blank=True, null=True)
	dest_devicename = models.CharField(max_length=200,blank=True, null=True)
	dest_deviceidentifier = models.CharField(max_length=200,blank=True, null=True)
	dest_devicemodel = models.CharField(max_length=200,blank=True, null=True)
	dest_aliases = models.CharField(max_length=200,blank=True, null=True)
	dest_site = models.CharField(max_length=200,blank=True, null=True)
	dest_authenticationstatus = models.CharField(max_length=200,blank=True, null=True)
	dest_registrationstatus = models.CharField(max_length=200,blank=True, null=True)
	dest_territory = models.CharField(max_length=200,blank=True, null=True)
	dest_ipaddress = models.CharField(max_length=200,blank=True, null=True)
	dest_deviceversion = models.CharField(max_length=200,blank=True, null=True)
	
	def __str__(self):
		return self.callidentifier
	
	def update():
		logger.info("Start update CDR")
		prev = get_req_to_db(0,"select time from times where table_name = 'cdr'")[0][0].isoformat(sep='T')
		timenow = (get_req_to_db(0,"select time from times where table_name = 'cdr'")[0][0] + dtm.timedelta(days=4)).isoformat(sep='T')
		to_datetime = get_req_to_db(0,"select time from times where table_name = 'cdr'")[0][0] + dtm.timedelta(days=4)
		if (get_req_to_db(0,"select time from times where table_name = 'cdr'")[0][0] + dtm.timedelta(days=4)) > dtm.datetime.today().astimezone():
			timenow = dtm.datetime.today().astimezone().isoformat(sep='T')
			to_datetime = dtm.datetime.today().astimezone()
		logger.info(f'{prev}, {timenow}')
		get_req_to_db(0,"update times set time = '{}' where table_name = 'cdr'".format(to_datetime),False)
		global call_ID
		counting = 1
		while True:
			duration = None;
			url = 'https://spb99-vcsdm.gazprom-neft.local/api/rest/reports/calls?start-after={}&start-before={}&page={}'.format(prev,timenow,counting)
			req = requests.get(url, headers={'dataType': 'json',"Authorization": "Basic ",'Accept': 'application/vnd.plcm.plcm-call-list+json','contentType': 'application/json'})
			data1 = req.json()
			counting += 1
			if data1['plcmPage']['currentPage'] == 0:
				break;
			for row in range(len(data1['plcmCallList'])):
				callIdentifier = data1['plcmCallList'][row]['callIdentifier']
				originator = data1['plcmCallList'][row]['originator']
				dialString = data1['plcmCallList'][row]['dialString']
				destination = data1['plcmCallList'][row]['destination']
				nodeId = data1['plcmCallList'][row]['nodeId']
				callStatus = data1['plcmCallList'][row]['callStatus']
				callSignaling = data1['plcmCallList'][row]['callSignaling']
				cluster = data1['plcmCallList'][row]['cluster']
				fullyExternal = data1['plcmCallList'][row]['fullyExternal']
				sharedLicensed = data1['plcmCallList'][row]['sharedLicensed']
				startTime = data1['plcmCallList'][row]['startTime']
				endTime = data1['plcmCallList'][row]['endTime']if 'endTime' in data1['plcmCallList'][row] else None
				destinationDetails = data1['plcmCallList'][row]['destinationDetails']
				originatorDetails =  data1['plcmCallList'][row]['originatorDetails']
				orig_devicename = originatorDetails['deviceName'] if 'deviceName' in originatorDetails else None
				orig_deviceidentifier = originatorDetails['deviceIdentifier'] if 'deviceIdentifier' in originatorDetails else None
				orig_devicemodel = originatorDetails['deviceModel'] if 'deviceModel' in originatorDetails else None
				orig_aliases = originatorDetails['aliases'] if 'aliases' in originatorDetails else None
				orig_site = originatorDetails['site'] if 'site' in originatorDetails else None
				orig_registrationstatus = originatorDetails['registrationStatus'] if 'registrationStatus' in originatorDetails else None
				orig_territory = originatorDetails['territory'] if 'territory' in originatorDetails else None
				orig_ipaddress = originatorDetails['ipAddress'] if 'ipAddress' in originatorDetails else None
				orig_deviceversion = originatorDetails['deviceVersion'] if 'deviceVersion' in originatorDetails else None
				dest_devicename = destinationDetails['deviceName'] if 'deviceName' in destinationDetails else None
				dest_deviceidentifier = destinationDetails['deviceIdentifier'] if 'deviceIdentifier' in destinationDetails else None
				dest_devicemodel = destinationDetails['deviceModel'] if 'deviceModel' in destinationDetails else None
				dest_aliases = destinationDetails['aliases'] if 'aliases' in destinationDetails else None
				dest_site = destinationDetails['site'] if 'site' in destinationDetails else None
				dest_authenticationstatus = destinationDetails['authenticationStatus'] if 'authenticationStatus' in destinationDetails else None
				dest_registrationstatus = destinationDetails['registrationStatus'] if 'registrationStatus' in destinationDetails else None
				dest_territory = destinationDetails['territory'] if 'territory' in destinationDetails else None
				dest_ipaddress = destinationDetails['ipAddress'] if 'ipAddress' in destinationDetails else None
				dest_deviceversion = destinationDetails['deviceVersion'] if 'deviceVersion' in destinationDetails else None
				if originator.find(';') > 0:
					origSip = originator[4:originator.find(';')]
				else: origSip = originator[4:]
				call_ID = None
				
				if callStatus == "Ended" and startTime != None and endTime != None:
					dte = dtm.datetime.fromisoformat(endTime)
					dts = dtm.datetime.fromisoformat(startTime)
					duration = dte-dts
				else:
					duration = None
					
				if 'ipAddress' in originatorDetails and ksuit.objects.filter(ip=originatorDetails['ipAddress']).exists():
					orig_ksuit_elem = ksuit.objects.filter(ip=originatorDetails['ipAddress']).get()
					do_name = do_reg.objects.get(name=orig_ksuit_elem.do_name).name if do_reg.objects.filter(name=orig_ksuit_elem.do_name).exists() else None
					ksuit_name = orig_ksuit_elem.name
				elif 'ipAddress' in destinationDetails and ksuit.objects.filter(ip=destinationDetails['ipAddress']).exists():
					dest_ksuit_elem = ksuit.objects.filter(ip=destinationDetails['ipAddress']).get()
					do_name = do_reg.objects.get(name=dest_ksuit_elem.do_name).name if do_reg.objects.filter(name=dest_ksuit_elem.do_name).exists() else None
					ksuit_name = dest_ksuit_elem.name
				elif registry.objects.filter(sip_address=origSip).exists():
					registry_elem = registry.objects.filter(sip_address=origSip)[0]
					do_name = registry_elem.id_do.name
					ksuit_name = registry_elem.terminal_name
				elif registry.objects.filter(h323_name=origSip[4:originator.find('@')]).exists():
					registry_elem = registry.objects.filter(h323_name=origSip[4:originator.find('@')]).get()
					do_name = registry_elem.id_do.name
					ksuit_name = registry_elem.terminal_name
				else:
					do_name = None
					ksuit_name = None
					
				callID_url = 'https://spb99-vcsdm.gazprom-neft.local/api/rest/reports/calls/{}/call-events'.format(callIdentifier)
				callID_req = requests.get(callID_url, headers={'dataType': 'json',"Authorization": "Basic ",'Accept': 'application/vnd.plcm.plcm-audit-event-list+json','contentType': 'application/json'})
				callID_elem = callID_req.json()
				if "plcmAuditEventList" in callID_elem:
					for event in callID_elem["plcmAuditEventList"]:
						if "plcmAttributeList" in event:
							for attr in event["plcmAttributeList"]:
								if ("attributeKey" in attr and "attributeValue" in attr) and "numberDigits:" in attr["attributeValue"] and callSignaling == 'h323':
									call_ID = attr["attributeValue"][attr["attributeValue"].index("numberDigits:")+13:attr["attributeValue"].index("\"",attr["attributeValue"].index("numberDigits:"))]
									break
								elif ("attributeKey" in attr and "attributeValue" in attr) and callSignaling == 'SIP'and "INVITE sip:" in attr["attributeValue"]:
									find_result = re.search(r'INVITE sip:\d{1,20}@10',attr["attributeValue"])
									find_VMR = re.search(r'DMA_VMR.\d{1,20}@10',attr["attributeValue"])
									if find_result != None:
										call_ID = find_result.group(0)[11:len(find_result.group(0))-3]
									elif find_VMR != None:
										call_ID = 'VMR: '+ find_VMR.group(0)[8:len(find_VMR.group(0))-3]
									else: call_ID = None
				Call_url = "https://spb99-vcsdm.gazprom-neft.local/api/rest/reports/calls/" + callIdentifier
				Call_req = requests.get(Call_url, headers={'dataType': 'json',"Authorization": "Basic ",'Accept': 'application/vnd.plcm.plcm-call+json','contentType': 'application/json'})
				call_elem = Call_req.json()

				elem_maintable = maintable(callidentifier = callIdentifier, originator = originator, sharedlicensed = sharedLicensed, callsignaling = callSignaling, fullyexternal = fullyExternal, destination = destination, nodeid = nodeId, cluster = cluster, dialstring = dialString, starttime = startTime, endtime = endTime, callstatus = callStatus, conference = call_elem['originator'], participant = call_elem['destination'], duration = duration, numberdigits = call_ID, do_name = do_name, ksuit_name = ksuit_name, orig_devicename = orig_devicename, orig_deviceidentifier = orig_deviceidentifier, orig_devicemodel = orig_devicemodel, orig_aliases = orig_aliases, orig_site = orig_site, orig_registrationstatus = orig_registrationstatus, orig_territory = orig_territory, orig_ipaddress = orig_ipaddress, orig_deviceversion = orig_deviceversion, dest_devicename = dest_devicename, dest_deviceidentifier = dest_deviceidentifier, dest_devicemodel = dest_devicemodel, dest_aliases = dest_aliases, dest_site = dest_site, dest_authenticationstatus = dest_authenticationstatus, dest_registrationstatus = dest_registrationstatus, dest_territory = dest_territory, dest_ipaddress = dest_ipaddress, dest_deviceversion = dest_deviceversion)
				elem_maintable.save()
#		get_req_to_db(0,"update times set time = '{}' where table_name = 'cdr'".format(to_datetime),False)
		logger.info("DONE update CDR!")


	def update_active_call():
		logger.info("Start update active CDR")
		updated_calls = get_req_to_db(0,"select callidentifier from \"Poly_maintable\" where callstatus = 'Active'")
		for callIdentifier in updated_calls:
			Call_url = "https://spb99-vcsdm.gazprom-neft.local/api/rest/reports/calls/" + callIdentifier[0]
			Call_req = requests.get(Call_url, headers={'dataType': 'json',"Authorization": "Basic ",'Accept': 'application/vnd.plcm.plcm-call+json','contentType': 'application/json'})
			if Call_req.status_code != 404:
				call_elem = Call_req.json()
				if call_elem['callStatus']!= 'Active':
					dte = dtm.datetime.fromisoformat(call_elem['endTime'])
					dts = dtm.datetime.fromisoformat(call_elem['startTime'])
					duration = dte-dts
				else:
					duration = None
				maintable.objects.filter(callidentifier=callIdentifier[0]).update(endtime = call_elem['endTime'] if call_elem['callStatus'] != 'Active' else None, callstatus = call_elem['callStatus'],duration = duration)
			elif Call_req.status_code == 404:
				updated_call = maintable.objects.filter(callidentifier=callIdentifier[0])
				updated_call.update(endtime=updated_call[0].starttime+dtm.timedelta(hours=1), duration = (updated_call[0].starttime + dtm.timedelta(hours=1))-updated_call[0].starttime, callstatus = 'Ended')
		logger.info("DONE update active CDR!")


	def update_name_terminals_in_call():
		logger.info("Start update name terminals in call")
		updated_calls = get_req_to_db(0,"select callidentifier from \"Poly_maintable\" where not (originator ilike '%s4b01.gazprom-neft.local%' or originator ilike 'sip:gatewayRMX-%'or originator ilike 'sip:0%') and originator ilike 'sip:%' and ksuit_name isnull")
		for callIdentifier in updated_calls:
			call = maintable.objects.filter(callidentifier=callIdentifier[0]).order_by("-starttime").first()
			if registry.objects.filter(sip_address=call.originator[4:]).exclude(terminal_name__icontains='демонт').exists():
				registry_elem = registry.objects.filter(sip_address=call.originator[4:]).exclude(terminal_name__icontains='демонт').get()
				call.ksuit_name = registry_elem.terminal_name
				if call.do_name == None or call.do_name == '':
					call.do_name=registry_elem.id_do.name
				call.save()
			elif registry.objects.filter(h323_name=call.originator[4:call.originator.find('@')]).exclude(terminal_name__icontains='демонт').exists():
				registry_elem = registry.objects.filter(h323_name=call.originator[4:call.originator.find('@')]).exclude(terminal_name__icontains='демонт').first()
				call.ksuit_name = registry_elem.terminal_name
				if call.do_name == None or call.do_name == '':
					call.do_name=registry_elem.id_do.name
				call.save()

		logger.info("DONE update name terminals in call")

class logs(models.Model):
	name = models.CharField(max_length=150)
	cmd = models.CharField(blank=True, null=True, max_length=150)
	reg_ip = models.ForeignKey(registry, on_delete = models.CASCADE,blank=True, null=True)
	old_value = models.CharField(blank=True, null=True, max_length=250)
	new_value = models.CharField(blank=True, null=True, max_length=250)
	date = models.DateTimeField()
	type = models.CharField(blank=True, null=True, max_length=150)

	def __str__(self):
		return f"{self.name} {self.type} {self.reg_ip.terminal_name}"

class registry_logs(models.Model):
	name = models.CharField(max_length=150)
	request = models.CharField(blank=True, null=True, max_length=150)
	date = models.DateTimeField(blank=True, null=True)
	type = models.CharField(blank=True, null=True, max_length=150)

	def __str__(self):
		return self.table_file
