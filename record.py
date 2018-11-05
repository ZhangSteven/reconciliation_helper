# coding=utf-8
# 
# Use a database to save the past file conversion records, which files
# are converted successfully.
# 

import sqlite3
import os, time
from datetime import datetime, timedelta
from reconciliation_helper.utility import get_current_path, in_test_mode, \
											enable_test_mode, get_test_db_connection
import logging
logger = logging.getLogger(__name__)



def filter_files(file_list):
	"""
	Pick the approapriate files from the file list based on the following
	criteria:

	1. Format: files must be in 'xls' or 'xlsx' format.
	2. Not processed before: files not found in the file_status table.
	3. Updated since last processed: if a file was processed before, i.e.,
		in the file_status table, but its last modified time stamp is newer 
		than that in the record.
	"""
	process_list = []
	for file in file_list:
		if file.split('\\')[-1].startswith('~'):
			continue
			
		if has_valid_extension(file):
			m_datetime = get_file_timestamp(file)
			if m_datetime is None:	# not processed before
				process_list.append(file)
			elif modified_later_than_record(file, m_datetime):
				process_list.append(file)
			# else:
			# 	logger.debug('filter_files(): {0} ignored'.format(file))
		else:
			logger.debug('filter_files(): {0} does not have valid extension'.
							format(file))
			
	return process_list



def save_result(result):
	"""
	Save the result to database.
	"""
	c = get_db_cursor()
	pass_records = create_status_records(result['pass'], 'pass')
	fail_records = create_status_records(result['fail'], 'fail')
	c.executemany('INSERT OR REPLACE INTO file_status (file_fullpath, m_time, status) VALUES (?, ?, ?)', \
					pass_records+fail_records)

	process_records = create_process_records(result['pass'], result['fail'])
	c.executemany('INSERT INTO process_result (file_fullpath, m_time, record_time, result) VALUES (?, ?, ?, ?)', \
					process_records)

	get_db_connection().commit()



def get_db_cursor():
	"""
	Use a function static variable to store something that needs to be
	initialized once, and reused later.

	Code example see:
	http://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function
	"""
	if 'cursor' not in get_db_cursor.__dict__:
		get_db_cursor.cursor = None

	if get_db_cursor.cursor is None:
		get_db_cursor.cursor = get_db_connection().cursor()

	return get_db_cursor.cursor



def get_db_connection():
	if 'conn' not in get_db_connection.__dict__:
		get_db_connection.conn = None

	if get_db_connection.conn is None:
		if in_test_mode():
			logger.info('get_db_connection(): connect to test database')
			get_db_connection.conn = get_test_db_connection()
		else:
			logger.info('get_db_connection(): connect to database: records.db')
			get_db_connection.conn = sqlite3.connect(os.path.join(get_current_path(), 'records.db'))

	return get_db_connection.conn



def has_valid_extension(file):
	"""
	file: a full path file name, like C:\temp\sample.txt
	
	If the file extension is xls or xlsx or csv, that extension is valid.
	"""
	filename = file.split('\\')[-1]
	if filename.split('.')[-1] in ['xls', 'xlsx', 'csv']:
		return True

	return False



def create_status_records(file_list, status):
	"""
	create records to be populated into table file_status.
	"""
	records = []
	for file in file_list:
		time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', 
									time.localtime(get_modified_time_stamp(file)))
		records.append((file, time_stamp, status))

	return records



def create_process_records(pass_list, fail_list):
	records = []
	record_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
									time.localtime(time.time()))
	create_process_records_detail(records, pass_list, record_timestamp, 'pass')
	create_process_records_detail(records, fail_list, record_timestamp, 'fail')
	# create_process_records_detail(records, ignore_list, record_timestamp, 'ignore')
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
	Test whether a file is updated since the last time it was processed and
	recorded in the database file_status table.
	"""
	# when a file's last modified time is saved into database, its precision
	# is up to one second. E.g., its last modified time is 2012-7-8 2:15:10.999,
	# it is recored as 2012-7-8 2:15:10. The 0.999 second is gone. So unless
	# a file's last modified time is at least 1 seond newer than the record, 
	# we won't consider the file is newer.
	if datetime.fromtimestamp(get_modified_time_stamp(file)) - m_datetime > \
		timedelta(seconds=1):
		return True
	else:
		return False



def get_file_timestamp(file):
	"""
	From the "file_status" table read the last modified datetime for the file,
	if the file does not exist (not processed before), then return None.
	"""
	c = get_db_cursor()
	t = (file, )
	c.execute('SELECT * FROM file_status WHERE file_fullpath=?', t)
	result = c.fetchone()

	if result is None:
		return None
	else:
		return dt_string_to_datetime(result[1])



def dt_string_to_datetime(dt_string):
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