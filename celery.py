import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VCS.settings')
app = Celery('VCS',task_send_sent_event=True,worker_send_task_events=True)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.task_track_started = True
app.conf.task_send_sent_event = True
app.conf.result_backend = 'redis://localhost:6379/1'
m = 0
eh = '*'
app.conf.beat_schedule = {
    'Update_CDR_every_hour': {
        'task': 'Poly.tasks.update_CDR',
        'schedule': crontab(minute = m, hour=eh),
    },
    'Update_KSUIT_every_hour': {
        'task': 'Poly.tasks.update_KSUIT',
        'schedule': crontab(minute = m, hour=eh),
    },
    'Update_TC_confs_and_calls_every_hour': {
        'task': 'TrueConf.tasks.update_tc_calls_confs',
        'schedule': crontab(minute = m, hour=eh),
    },
    'Update_TC_AI_every_hour': {
        'task': 'TrueConf.tasks.update_tc_ai',
        'schedule': crontab(minute = m, hour=eh),
    },
    'Update_inactive_confs_every_night': {
        'task': 'TrueConf.tasks.update_active_calls',
        'schedule': crontab(minute = m, hour=1),
    },
    'Update_TC_users_every_day': {
        'task': 'TrueConf.tasks.update_tc_users',
        'schedule': crontab(minute = m, hour=4),
    },
    'Update_TC_versions_every_hour': {
        'task': 'TrueConf.tasks.update_tc_versions',
        'schedule': crontab(minute = m, hour=eh),
    },
    'task_tc_active_calls': {
        'task': 'TrueConf.tasks.update_active_calls',
        'schedule': crontab(minute = m, hour='5', day_of_week='sunday'),
    },
    'task_tc_conf_from file': {
        'task': 'TrueConf.tasks.update_tc_calls_confs_from_file',
        'schedule': crontab(minute = m, hour='*/4'),
    },

}
app.conf.timezone = 'UTC'
