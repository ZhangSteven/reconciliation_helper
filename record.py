# coding=utf-8
# 
# Use a database to save the past file conversion records, which files
# are converted successfully.
# 

import sqlite3
import os, time
from datetime import datetime, timedelta
from reconciliation_helper.utility import logger, get_current_path



def filter_files(file_list, process_list, ignore_list):
	"""
	Pick the approapriate files from the file list based on the following
	criteria:

	1. Format: files must be in 'xls' or 'xlsx' format.
	2. Not successful before: files not found in the successful file list
	3. Last modified time stamp: if a file is in the successful file list,
		but its last modified time stamp is newer than that in the record.
	"""
	for file in file_list:
		if has_valid_extension(file):
			m_datetime = get_file_timestamp(file)
			if m_datetime is None:	# this file is not in record
				process_list.append(file)
			else:
				if modified_later_than_record(file, m_datetime):
					process_list.append(file)
				else:
					ignore_list.append(file)



def save_result(result):
	"""
	Save the result to database.
	"""
	c = get_db_connection().cursor()
	pass_records = create_pass_records(result['pass'])
	c.executemany('INSERT OR REPLACE INTO pass_files (file_fullpath, m_time) VALUES (?, ?)', \
					pass_records)

	c.execute('SELECT * FROM pass_files')
	print(c.fetchall())
	process_records = create_process_records(result['pass'], result['fail'], result['ignore'])
	c.executemany('INSERT INTO process_files (file_fullpath, m_time, record_time, result) VALUES (?, ?, ?, ?)', \
					process_records)
	c.execute('SELECT * FROM process_files')
	print(c.fetchall())



conn = None
def get_db_connection():
	global conn
	if conn is None:
		global test_mode
		if test_mode:
			logger.info('get_db_connection(): connect to test database')
			conn = get_test_db_connection()
		else:
			logger.info('get_db_connection(): connect to database: records.db')
			conn = sqlite3.connect('records.db')

	return conn



test_mode = False
test_conn = None
def enable_test_mode(db_conn):
	"""
	Only used for test cases, because test mode uses a different database.
	When test mode is enabled, the testing code creates the testing database,
	and pass connection to that database here.
	"""
	global test_mode
	test_mode = True

	global test_conn
	test_conn = db_conn



def get_test_db_connection():
	global test_conn
	return test_conn



def has_valid_extension(file):
	"""
	file: a full path file name, like C:\temp\sample.txt
	
	If the file extension is xls or xlsx, that extension is valid.
	"""
	filename = file.split('\\')[-1]
	if filename.split('.')[-1] in ['xls', 'xlsx']:
		return True

	return False



def create_pass_records(pass_files):
	records = []
	for file in pass_files:
		time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', 
									time.localtime(get_modified_time_stamp(file)))
		records.append((file, time_stamp))

	return records



def create_process_records(pass_list, fail_list, ignore_list):
	records = []
	record_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
									time.localtime(time.time()))
	create_process_records_detail(records, pass_list, record_timestamp, 'pass')
	create_process_records_detail(records, fail_list, record_timestamp, 'fail')
	create_process_records_detail(records, ignore_list, record_timestamp, 'ignore')
	return records



def create_process_records_detail(records, file_list, record_timestamp, status):
	for file in file_list:
		m_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
									time.localtime(get_modified_time_stamp(file)))
		records.append((file, m_timestamp, record_timestamp, status))



def get_modified_time_stamp(file):
	return os.path.getmtime(file)



def modified_later_than_record(file, m_datetime):
	"""
	Test whether a file's last modified time is later than that in the record.
	"""
	# when a file's last modified time is saved into database, its precision
	# is up to one second. E.g., its last modified time is 2012-7-8 2:15:10.999,
	# it is recored as 2012-7-8 2:15:10. The 0.999 second is gone. So only
	# when a file's last modified time is 1 seond newer than the record, we'll
	# consider it a newer file.
	if datetime.fromtimestamp(get_modified_time_stamp(file)) - m_datetime > \
		timedelta(seconds=1):
		return True
	else:
		return False



def get_file_timestamp(file):
	"""
	Read the file modified date and time from database and return a 
	datetime object to represent it.
	"""
	c = get_db_connection().cursor()
	t = (file, )
	c.execute('SELECT * FROM pass_files WHERE file_fullpath=?', t)
	result = c.fetchone()

	if result is None:
		return None
	else:
		return convert_string_to_datetime(result[1])



def convert_string_to_datetime(dt_string):
	"""
	convert a string in 'yyyy-mm-dd hh:mm:ss' format to a datetime
	object.
	"""
	dt_token = dt_string.split()[0]
	tm_token = dt_string.split()[1]
	year, month, day = parse_string(dt_token, '-')
	hour, minute, second = parse_string(tm_token, ':')
	return datetime(year, month, day, hour=hour, minute=minute, second=second)



def parse_string(a_string, separator):
	"""
	Convert string of form 'yyyy-mm-dd' or 'hh-mm-ss' into three
	integers.
	"""
	a_list = a_string.split(separator)
	return int(a_list[0]), int(a_list[1]), int(a_list[2])