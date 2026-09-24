#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio, psycopg2, sys, os
sys.path.append("/var/www/VCS_Portal")
from psycopg2.extras import RealDictCursor
import db_settings
status_req = True
this_serv = None

access_users = [user.lower() for user in db_settings.access_users.split(',')]
operators = [user.lower() for user in db_settings.operators.split(',')]
admins = [user.lower() for user in db_settings.admins.split(',')]
count_servers = ['_DBHOST' in x for x in list(os.environ.keys())].count(True) + 1
count_ai_servers = ['TC_AI_HOST_' in x for x in list(os.environ.keys())].count(True)
ai_servers = [os.environ[x] for x in os.environ if 'TC_AI_HOST' in x]

if sys.version_info >= (3,7,0):
	get_running_loop = asyncio.get_running_loop
else:
	def get_running_loop() -> asyncio.AbstractEventLoop:
		loop = asyncio.get_event_loop()
		if not loop.is_running():
			raise RuntimeError('no running event loop')
		return loop

def ready(conn, waiter):
	global this_serv, status_req
	try:
		loop = get_running_loop()
		fileno = conn.fileno()
		state = conn.poll()
		if state == psycopg2.extensions.POLL_OK:
			loop.remove_writer(fileno)
			loop.remove_reader(fileno)
			waiter.set_result(None)
		elif state == psycopg2.extensions.POLL_WRITE:
			loop.add_writer(fileno,ready,conn,waiter)
		elif state == psycopg2.extensions.POLL_READ:
			loop.remove_writer(fileno)
			loop.add_reader(fileno,ready,conn,waiter)
		else:
			print(state)
			raise psycopg2.OperationalError("pool()returned %s" % state)
		status_req = True
	except Exception as err:
		from VCS import celery_app
		print(str(err)+'. error,break.')
		all_tasks = celery_app.control.inspect()
		task_id = all_tasks.active()['celery@SPB99-VCSFS1'][0]['id']
		celery_app.control.terminate(task_id, signal='SIGKILL')
		
	
async def wait(conn):
	waiter = get_running_loop().create_future()
	try:
		ready(conn, waiter)
	except Exception as err:
		return(err)
	await asyncio.wait_for(waiter, None)
	
async def ainsert(server, query, select, var_host, var_database, var_user, var_passwd, var_port):
	response = 'No data to return'
	aconn = psycopg2.connect(database=var_database, user=var_user, password=var_passwd, host=var_host, port=var_port, async_=1)
	try:
		await wait(aconn)
	except Exception as err:
		return(server, query, err)
	acurs = aconn.cursor()
	acurs.execute(query)
	try:
		await wait(acurs.connection)
	except Exception as err:
		return(server, query, err)
	if select:
		response = acurs.fetchall()
	acurs.close()
	aconn.close()
	return response


def get_req_to_db(server,query,select=True,sync_req=False):
	try:
		global this_serv, status_req
		if isinstance(server, str):
			server = int(server)
		this_serv = server
		if this_serv == 0:
			var_host = os.environ.get('DBHOST')
			var_database = db_settings.DBNAME
			var_user = db_settings.DBUSER
			var_passwd = db_settings.DBPASS
			var_port = 5432
		elif server > 410:
			var_host = os.environ.get(f'TC_AI_HOST_{server-410}')
			var_database = os.environ.get('TC_AI_DBNAME')
			var_user = os.environ.get('TC_DBUSER')
			var_passwd = os.environ.get('TC_DBPASS')
			var_port = os.environ.get('5432')
		else:
			var_host = os.environ.get('TC'+str(this_serv)+'_DBHOST')
			var_database = db_settings.TC_DBNAME
			var_user = db_settings.TC_DBUSER
			var_passwd = db_settings.TC_DBPASS
			var_port = db_settings.TC_DBPORT
		if sync_req == False:
			while status_req == True:
				loop = asyncio.new_event_loop()
				asyncio.set_event_loop(loop)
				future = asyncio.ensure_future(ainsert(server,query,select, var_host,var_database,var_user,var_passwd,var_port))
				loop.run_until_complete(future)
				responses = future.result()
				return(responses)
		else:
			conn = psycopg2.connect(database=var_database, user=var_user, password=var_passwd, host=var_host, port=var_port)
			conn.autocommit = True
			if server > 410:
				conn_cur = conn.cursor(cursor_factory=RealDictCursor)
				conn_cur.execute(query)
				response = [dict(row) for row in conn_cur.fetchall()]
			else:
				conn_cur = conn.cursor()
				conn_cur.execute(query)
				response = conn_cur.fetchall()
			conn_cur.close()
			conn.close()

			return(response)
	except Exception as err:
		print (f'error connection from req_to_all_db.py {err}')
