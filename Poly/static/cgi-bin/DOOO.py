#!/usr/bin/python3
# -*- coding: utf-8 -*-

import psycopg2
import sys
sys.path.insert(1, '/home/wa-rmuzenbaev@GAZPROM-NEFT.LOCAL/scripts/CDR2/')
sys.path.append("/var/www/html/")
print('Content-Type: application/json\n')
from Get_Endpoints_DMA import main
import openpyxl
from openpyxl.worksheet.table import Table
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
import datetime, calendar
from urllib.parse import parse_qs
import os
#import calendar

query = parse_qs(os.environ['QUERY_STRING'])
centerAlign = ['E','F','G','H','I','J','K']
alpha=['A','B','C','D','E','F','G','H','I','J','K']
def getmonth():
	month_list = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
	return(month_list[int(query["to_date"][0].split('-')[1])-1])
def format_Table(len_table,last_row_table, max_col_table, indent=0,merge=False,Table_italic=False,align='left'):
	if merge==False:
		ws.merge_cells('A' + str(last_row_table+indent) + ':' + alpha[max_col_table-1] + str(last_row_table+indent))
		ws['A' + str(last_row_table+indent)].fill  = PatternFill('solid', fgColor="EEECE1")
		ws['B' + str(last_row_table+indent-1)].alignment = Alignment(horizontal='right')
		ws['B' + str(last_row_table+indent-1)].font  = Font(bold=True,name='Arial', size=10)
		ws['C' + str(last_row_table+indent-1)].font  = Font(bold=True,name='Arial', size=10)
		ws['D' + str(last_row_table+indent-1)].font  = Font(bold=True,name='Arial', size=10)
	elif merge==True:
		ws.merge_cells('A' + str(last_row_table+indent+1) + ':' + alpha[max_col_table-2] + str(last_row_table+indent+1))
		ws['A' + str(last_row_table+indent+1)].fill  = PatternFill('solid', fgColor="EEECE1")
		ws['A' + str(last_row_table+indent+1)].font  = Font(bold=True, name='Arial')
		ws[alpha[max_col_table-1] + str(last_row_table+indent+1)].fill  = PatternFill('solid', fgColor="EEECE1")
		ws[alpha[max_col_table-1] + str(last_row_table+indent+1)].font = Font(bold=True, name='Arial')
		ws['A' + str(last_row_table+indent+1)].font = Font(bold=True, name='Arial')

	for rows in ws.iter_rows(min_row=last_row_table-len_table, max_row=last_row_table+indent+int(merge), min_col=None,max_col=max_col_table):
		for cell in rows:
			cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
			cell.alignment  = Alignment(vertical="center")
			if (cell.column == 'A' or cell.column in centerAlign) and cell.row<=last_row_table:
				cell.alignment  = Alignment(wrapText=True, horizontal="center", vertical="center")
				cell.font = Font(name='Arial',size=10,italic=Table_italic)
			if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column != 'B':
				cell.font = Font(name='Arial',size=10,italic=Table_italic)
				cell.alignment  = Alignment(wrapText=True, horizontal="center", vertical="center")
			if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column == 'B':
				cell.font = Font(name='Arial',size=10,italic=Table_italic)
				cell.alignment  = Alignment(wrapText=True, horizontal=align, vertical="center")
			if cell.row>last_row_table-len_table and cell.row<=last_row_table and cell.column == 'K':
				cell.font = Font(name='Arial',size=10,italic=Table_italic,color='808080')
				cell.alignment  = Alignment(wrapText=True, horizontal="center", vertical="center")
	for rows in ws.iter_rows(min_row=last_row_table-len_table, max_row=last_row_table-len_table, min_col=None,max_col=max_col_table):
		for cell in rows:
			cell.fill  = PatternFill('solid', fgColor="F2F2F2")
			cell.alignment  = Alignment(wrapText=True, horizontal="center", vertical="center")
			cell.font = Font(size=10, bold=True, name='Arial')
	ws['A'+str(last_row_table+1)].alignment = Alignment(horizontal='right')
	ws['C'+str(last_row_table+indent-1)].alignment = Alignment(horizontal='left')
	ws['D'+str(last_row_table-len_table)].alignment = Alignment(wrapText=True, horizontal="center", vertical="center")
	
			
thin = Side(border_style="thin")
month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
report_date = 'с 1 по ' + str(calendar.monthrange(int(query["to_date"][0].split('-')[0]),int(query["to_date"][0].split('-')[1]))[1]) + ' ' + str(month_list[int(query["to_date"][0].split('-')[1])-1]) + ' ' + str(query["to_date"][0].split('-')[0]) + ' г.'
font = Font(name='Arial', size=12, bold=False, italic=False)
alignment=Alignment(wrapText=True, horizontal='center',vertical='center')
mkday = datetime.date.today().strftime("%d.%m.%Y")
count_oo_rows = 1
date_from = query["from_date"][0]
date_to = query["to_date"][0]


# Подключение к базе данных
conn = psycopg2.connect(
host="localhost",
database="PolyDB",
user="pusr",
password="Polycom12#$")

conn.autocommit = True

# Создание курсора
cur = conn.cursor()

do_name = {}
do_name_list = []
terminals = []
last_row =0
SRH = 15
MRH = 25
LRH = 51
extcountCalls = 0
ext =['ГПН-ЦР Москва Телемост', 'ГПН-ЦР СПб Телемост 02', 'ГПН-ЦР СПб Телемост', 'ГПН-ЦР Тюмень Телемост', 'ГПН-ЦР Уфа Телемост', 'ГПН-ЦР Екб Телемост', '[VIP] ЦУЭ С-Пб Зоологический 4 605', 'ЦУЭ С-Пб Зоологический 4 531', '[VIP] ЦУЭ С-Пб Зоологический 4 604 (Мартынова ИВ)', '[VIP] ЦУЭ С-Пб Зоологический 4 618']
extcount = 0
print ("\nstart script\n")

endpoints = main()

response = [query["req_do"]]
for do in response:
	print(do[0])
	if do[0] == 'Газпромнефть НТЦ ООО':
		cur.execute("select name, manufacturer_name, model_name, ip, serial_number, software_version, type_cab_name, address, site from viev1 where do_name like \'Газпромнефть НТЦ%\' order by address")
	elif do[0] == 'Газпромнефть-смазочные материалы ООО':
		cur.execute("select name, manufacturer_name, model_name, ip, serial_number, software_version, type_cab_name, address, site from viev1 where do_name= \'Газпромнефть-смазочные материалы ООО\' or do_name= \'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО\' order by address")
	elif do[0] == 'Газпромнефть-Ноябрьскнефтегаз АО':
		cur.execute("select name, manufacturer_name, model_name, ip, serial_number, software_version, type_cab_name, address, site from viev1 where do_name= \'Газпромнефть-Ноябрьскнефтегаз АО\' or do_name= \'Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО\' order by address")
	elif do[0] =='Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО' or do[0] == 'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО' or do[0] == 'Газпромнефть НТЦ обособленное подразделение в г. Тюмень ООО' or do[0] == 'Автоматика-сервис ООО':
		continue
	else:
		cur.execute("select name, manufacturer_name, model_name, ip, serial_number, software_version, type_cab_name, address, site from viev1 where do_name ilike \'%"+ do[0] +"%\' order by address")
	response = cur.fetchall()
	wb = openpyxl.Workbook()
	ws = wb.active
	
	HSO = ['№ п/п', 'Наименование терминала (из КСУИТ)', 'Производитель', 'Модель', 'Сетевой адрес', 'Серийный номер', 'Версия ПО', 'Тип помещения', 'Фактический адрес установки', 'Номер площадки', 'Комментарий']
	
	ReportConnect = [['','','','','','','','','','','','','','','',''],['Таблица 1.3. – Отчёт об организации сеансов видеоконференций','','','','','','','','','','','','','','',''],['№ п/п','Наименование терминала (из КСУИТ)','Количество подключений терминала ВКС к сеансам видеоконференций, выполненных специалистами Исполнителя за период', ' ','','','','','','','','','','','','']]
	
	ReportTable = [['№ п/п','Наименование услуги','Код операционной услуги','Единица измерения','Объем потребления','Стоимость услуги','Сумма','','','','','','','','',''],[1,'Обслуживание аппаратных абонентских терминалов','MEET.VKS-HARDTERMINAL@CORP','терминал','=count(Table1[№ П/П])',6341.68,'=F27*E27','','','','','','','','',''],[2,'Организация сеанов ВКС','U.MEET.ORGVKS@CORP','подключение','=SUM(Table2[Количество подключений терминала ВКС к сеансам видеоконференций, выполненных специалистами Исполнителя за период])',1100.25,'=F28*E28','','','','','','','','',''],['Итого:','','','','','','=SUM(G27:G28)','','','','','','','','',''],['','','','','','','','','','','','','','','',''],['Таблица 1.2. – Перечень аппаратных абонентских терминалов ВКС за отчётный период','','','','','','','','','','','','','','','']]
	
	PSO = [['','','','','','','','','','','','','','','',''],['Таблица 1.3. – Перечень программных абонентских терминалов ВКС за отчётный период','','','','','','','','','','','','','','',''],['№ п/п','Учётная запись','','E-mail','','','','','','','','','','','','']]
	
	tData = [ ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', ''],  ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', 'Приложение № 2.7.7', '', '', '', '', '', ''],  ['', '', '', '', 'к Соглашению об уровне обслуживания ', '', '', '', '', '', ''], ['', '', '', '', 'в рамках ИТ Услуги Предоставление доступа к платформе видеоконференций', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', 'Отчет (Форма)', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', ''], ['', '', '', 'Отчет за ', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Услуга:', '', '\"Предоставление доступа к платформе видеоконференций\"', '', '', '', '', '', '', '', '', ''], ['Номер Договора:', '', '_______________________________________', '', '', '', '', '', '', '', '', ''], ['Отчетный период:', '', report_date, '', '', '', '', '', '', '', '', ''], ['Дата формирования:', '', mkday , '', '', '', '', '', '', '', '', ''], ['Номер сделки для актирования:', '', 'SERV.VKS.23009' , '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Отчет по услуге  №____  для '+ do[0], '', '', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Сервис-менеджер:', '', 'Колесник Георгий Вячеславович', '', '', '', '', '', '', '', '', ''], ['Период предоставления', '', 'Ежемесячно', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '', '', ''], ['Таблица 1.1. – Отчет по потреблению услуги', '', '', '', '', '', '', '', '', '', '']]
	
	tfooter = [['','','',''],['Таблица 1.4 – Отчет по Инцидентам','','',''],['№ п/п','Номер','Краткое описание ','Статус'],[1,'Инцидентов за указанный период не зарегистрировано.','',''],['Итого инцидентов:','','',0],['','','',''],['','','',''],['Таблица 1.5 – Отчет по Проблемам','','',''],['№ п/п','Номер','Краткое описание ','Статус'],[1,'Проблем за указанный период не зарегистрировано.','',''],['Итого проблем:','','',0],['','','','']]
	tData[11][3] += getmonth()+" 2023 г."
	for elem in tData:
		ws.append(elem)
		last_row += 1
	for elem in ReportTable:
		ws.append(elem)
		last_row += 1
	format_Table(2,ws.max_row-3,7,0,True)
	ws.append(HSO)
	last_row += 1
	ws['F27'].number_format = '''# ### ##0.00 \u20bd'''
	ws['F28'].number_format = '''# ### ##0.00 \u20bd'''
	ws['G27'].number_format = '''# ### ##0.00 \u20bd'''
	ws['G28'].number_format = '''# ### ##0.00 \u20bd'''
	ws['G29'].number_format = '''# ### ##0.00 \u20bd'''
	ws.column_dimensions['A'].width = 6
	ws.column_dimensions['B'].width = 75
	ws.column_dimensions['C'].width = 36
	ws.column_dimensions['D'].width = 32
	ws.column_dimensions['E'].width = 24
	ws.column_dimensions['F'].width = 24
	ws.column_dimensions['G'].width = 26
	ws.column_dimensions['H'].width = 24
	ws.column_dimensions['I'].width = 45
	ws.column_dimensions['J'].width = 15
	ws.column_dimensions['K'].width = 31
	ws.column_dimensions['Q'].width = 23
	ws.row_dimensions[10].height = 20.25 #Высота строки 10
	ws.row_dimensions[12].height = 20.25 #Высота строки 12
	ws.row_dimensions[26].height = 30 #Высота строки 26
	ws.row_dimensions[32].height = 30 #Высота строки 33
	ws.cell(row=1, column=11, value='Приложение № 16').font = Font(italic=True, name='Arial')
	ws.cell(row=2, column=11, value='к Распоряжению ПАО «Газпром нефть»').font = Font(italic=True, name='Arial')
	ws.cell(row=3, column=11, value='от «__» декабря 2022 г.').font = Font(italic=True, name='Arial')
	ws.cell(row=4, column=11, value='№ ___').font = Font(italic=True, name='Arial')
	ws['K1'].alignment = Alignment(horizontal='right')
	ws['K2'].alignment = Alignment(horizontal='right')
	ws['K3'].alignment = Alignment(horizontal='right')
	ws['K4'].alignment = Alignment(horizontal='right')
	ws['E27'].alignment = Alignment(horizontal='right')
	ws['E28'].alignment = Alignment(horizontal='right')
	ws['F27'].alignment = Alignment(horizontal='right')
	ws['F28'].alignment = Alignment(horizontal='right')
	ws['G27'].alignment = Alignment(horizontal='right')
	ws['G28'].alignment = Alignment(horizontal='right')
	ws['C28'].alignment = Alignment(horizontal='left')
	ws['A31'].font = Font(size=11, bold=True, name='Arial')
	for elem in response:
		if elem[0] not in ext:
			row = []
			row.append(count_oo_rows)
			row.extend(elem)
			count_oo_rows += 1
			if row[3] == None:
				row[3] = None
			elif 'HDX' in row[3] or 'TANDBERG' in row[3] or 'Trio' in row[3] or 'VSX' in row[3] or 'QDX' in row[3] or 'EVC' in row[3] or 'Edge' in row[3]:
				row.extend(['Требуется замена, т.к. оборудование официально признано устаревшим (EOL) и  СПИ истёк'])
			ws.append(row)
			if 'Требуется замена, т.к. оборудование официально признано устаревшим (EOL) и  СПИ истёк' in row:
				ws.row_dimensions[ws.max_row].height = LRH
			else:
				ws.row_dimensions[ws.max_row].height = MRH
			last_row += 1
		else:
			extcount += 1
	count_oo_rows = 1
	ws.append(['','Итого аппаратных терминалов: ','=count(Table1[№ П/П])'])
	ws.append([''])
	ws.row_dimensions[len(response) + 37 - extcount].height = 55 #высота строки шапки 1.4
	last_row += 2
	for row in ws['A1:E25']:
		for cell in row:
			if cell.row < 14:
				cell.font = Font(bold=True, name='Arial')
				cell.alignment  = Alignment(horizontal='center',vertical='center')
				if cell.row == 10 or cell.row == 12:
					cell.font = Font(size=16, bold=True, name='Arial')
			else:
				cell.font = Font(size=12, name='Arial')
				if cell.row == 20 or cell.row == 25:
					cell.font = Font(size=11, bold=True, name='Arial')
	
	format_Table(len(response)-extcount,ws.max_row-2,11,2,Table_italic=True)
	ws['D'+str(last_row-1)].alignment = Alignment(horizontal='left')
	ws['B'+str(last_row-1)].alignment = Alignment(horizontal='right')
	ws['D12'].alignment = Alignment(horizontal='left')
	ws['D27'].alignment = Alignment(wrapText=True, horizontal='center',vertical='center')
	ws['D28'].alignment = Alignment(wrapText=True, horizontal='center',vertical='center')
	tab = Table(displayName="Table1", ref="A32:K"+str(len(response)+33 - extcount))
	rowlen = str(len(response) + 32)
	ws.add_table(tab)
			
	for elem in ReportConnect:
		ws.append(elem)
		last_row += 1

	if do[0] == 'Газпромнефть НТЦ ООО':
		cur.execute("select ksuit_name, count(*) as connect_count from calls_view where starttime between '{}' and '{}' and do_name like \'Газпромнефть НТЦ%\' and originator ilike '%rmx%' group by ksuit_name".format(date_from, date_to))
	elif do[0] == 'Газпромнефть-смазочные материалы ООО':
		cur.execute("select ksuit_name, count(*) as connect_count from calls_view where starttime between '{}' and '{}' and (do_name= \'Газпромнефть-смазочные материалы ООО\' or do_name= \'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО\') and originator ilike '%rmx%' group by ksuit_name".format(date_from, date_to))
	elif do[0] == 'Газпромнефть-Ноябрьскнефтегаз АО':
		cur.execute("select ksuit_name, count(*) as connect_count from calls_view where starttime between '{}' and '{}' and (do_name= \'Газпромнефть-Ноябрьскнефтегаз АО\' or do_name= \'Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО\') and originator ilike '%rmx%' group by ksuit_name".format(date_from, date_to))
	elif do[0] =='Газпромнефть-Ноябрьскнефтегаз филиал Газпромнефть-Муравленко АО' or do[0] == 'Газпромнефть-смазочные материалы филиал в г. Санкт-Петербург ООО' or do[0] == 'Газпромнефть НТЦ обособленное подразделение в г. Тюмень ООО' or do[0] == 'Автоматика-сервис ООО':
		continue
	else:
		cur.execute("select ksuit_name, count(*) as connect_count from calls_view where starttime between '{}' and '{}' and do_name ilike '%{}%' and originator ilike '%rmx%' group by ksuit_name".format(date_from, date_to, do[0]))
		
	response = cur.fetchall()
	if len(response) == 0:
		ws.append(['','Итого количество подключений:',0])
		ws['E28'].value = 0
		ws.append([''])
		last_row += 2
	else:
		for elem in response:
			if elem[0] not in ext:
				row = []
				row.append(count_oo_rows)
				row.extend([elem[0],elem[1]])
				count_oo_rows += 1
				ws.append(row)
				last_row += 1
			else:
				extcountCalls += 1
		count_oo_rows = 1
		ws.append(['','Итого количество подключений:','=SUM(Table2[Количество подключений терминала ВКС к сеансам видеоконференций, выполненных специалистами Исполнителя за период])'])
		ws.append([''])
		last_row += 2
	ws['A' + str(ws.max_row-len(response)-3)].font = Font(size=11, bold=True, name='Arial')
	if len(response) != 0:
		tab = Table(displayName="Table2", ref="A" + str((last_row - 2 - len(response) + extcountCalls)) + ":C" + str(last_row - 2))
		ws.add_table(tab)
	format_Table(len(response)-extcountCalls,ws.max_row-2,3,2)
	ws['C'+str(last_row-1)].alignment = Alignment(horizontal='left')
	ws['B'+str(last_row-1)].alignment = Alignment(horizontal='right')
	for i in range(last_row-2, last_row-len(response)-4, -1):
		ws['C'+str(i)].alignment = Alignment(wrapText=True, horizontal='center',vertical='center')
	
	for elem in tfooter:
		ws.append(elem)
		last_row += 1
	ws.merge_cells('A14:B14')
	ws.merge_cells('A15:B15')
	ws.merge_cells('A16:B16')
	ws.merge_cells('A17:B17')
	ws.merge_cells('A18:B18')
	ws.merge_cells('A22:B22')
	ws.merge_cells('A23:B23')
	ws.merge_cells('C15:E15')
	ws.merge_cells('C16:E16')
	ws.merge_cells('C17:E17')
	ws.merge_cells('C18:E18')
	ws.merge_cells('C22:E22')
	ws.merge_cells('C23:E23')
	ws.merge_cells('C23:E23')
		
	format_Table(1,ws.max_row-2,4,merge=True,align='center')
	format_Table(1,ws.max_row-8,4,merge=True,align='center')
	ws['A' + str(ws.max_row-4)].font = Font(size=11, bold=True, name='Arial')
	ws['A' + str(ws.max_row-10)].font = Font(size=11, bold=True, name='Arial')
	ws['D' + str(ws.max_row-7)].alignment = Alignment(wrapText=True, horizontal='left',vertical='center')
	ws['D' + str(ws.max_row-1)].alignment = Alignment(wrapText=True, horizontal='left',vertical='center')
	
	
	last_row = 0
	extcount = 0
	extcountCalls = 0
#	wb.save("dwnld/" + do[0]+".xlsx")
	wb.save("/var/www/html/Reports/" + do[0]+".xlsx")
	print("DONE " + do[0]+".xlsx")