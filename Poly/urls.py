from django.urls import path
from Poly import views

urlpatterns = [
	path('CDR', views.cdr,name='cdr'),
	path('tasks/', views.tasks, name='tasks'),
	path('get_do/', views.get_do, name='get_do'),
	path('Reports', views.reports,name='reports'),
	path('illegal/', views.illegal,name='illegal'),
	path('Endpoints', views.endpoints,name='endpoints'),
	path('load_data/', views.load_data,name='load_data'),
	path('upload_page/', views.upload_page,name='upload_page'),
	path('report_channels/', views.report_channels,name='report_channels'),
	path('export/', views.export_to_excel, name='export_to_excel'),
	path('update_ksuit', views.update_KSUIT, name='update_ksuit'),
	path('edit_endpoint', views.edit_endpoint,name='edit_endpoint'),
	path('get_update_time/', views.get_update_time,name='get_update_time'),
	path('create_sample_tc/', views.create_sample_tc,name='create_sample_tc'),
	path('illegal_endpoints/', views.illegal_endpoints,name='illegal_endpoints'),
	path('report_active_app/', views.report_active_app, name='report_active_app'),
	path('report_type_confs/', views.report_type_confs, name='report_type_confs'),
	path('create_report_vcs/', views.create_report_vcs, name='create_report_vcs'),
	path('report_count_confs/', views.report_count_confs, name='report_count_confs'),
	path('report_active_user/', views.report_active_user, name='report_active_user'),
	path('report_chat_message/', views.report_chat_message, name='report_chat_message'),
	path('report_chat_message_for_user/', views.report_chat_message_for_user, name='report_chat_message_for_user'),
]
