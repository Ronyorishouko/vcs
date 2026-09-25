# -*- coding: utf-8 -*-
from .models import maintable, registry, ksuit
from VCS.celery import app
from .views import report_active_user
#from mail import send_mail

@app.task(bind=True, track_started=True) #регистриуем таску
def update_CDR(self):
	try:
		maintable.update()
		maintable.update_active_call()
		maintable.update_name_terminals_in_call()
		return True
	except Exception:
		print(f'TEST LOG - {Exception}')

@app.task(bind=True, track_started=True) #регистриуем таску
def update_KSUIT(self):
	try:
		ksuit.update()
		registry.update()
		ksuit.update_registry()
		return True
	except Exception:
		print(f'TEST LOG - {Exception}')

@app.task(bind=True, track_started=True)
def send_active_users(self):
	try:
		report_active_user(False)
		return True
	except Exception:
		print(f'TEST LOG - {Exception}')
