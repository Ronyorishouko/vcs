#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, django, re, datetime
sys.path.append('/var/www/VCS_Portal/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'VCS.settings'
django.setup()

from Poly.tasks import update_KSUIT
from django.db.models import Q
from TrueConf.models import User, Conference, tc_versions,db_connections
from Poly.models import registry, physical_address, ksuit, maintable,manufacturer,do_reg,group_networker,service_wg,terminal_model,type_cabinet
from Poly.views import report_active_user, report_type_confs, report_chat_message_for_user, illegal_endpoints, suid_users,suid_catalog
from req_to_all_db import get_req_to_db, count_servers

def update_ksuit():
	ksuit.update()
	registry.update()
	return ksuit.update_registry()

update_ksuit()
