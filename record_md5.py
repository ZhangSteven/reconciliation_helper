# coding=utf-8
# 
# Use a database to save the past file conversion records, which files
# are converted successfully.
# 

import sqlite3
import os
import datetime
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
	time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	c.executemany('INSERT INTO process_result (file_name, md5, status, process_time) VALUES (?, ?, 1, time_stamp)', \
					create_process_records(result['pass']))
	c.executemany('INSERT INTO process_result (file_name, md5, status, process_time) VALUES (?, ?, 0, time_stamp)', \
					create_process_records(result['fail']))
	get_db_connection().commit()



def get_db_cursor():
	"""
	Use a function static variable to store something that needs to be
	initialized once, and reused later.

	Code example see:
	http://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function
	"""
	if 'cursor' not in get_db_cursor.__dict__:
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
	
	If the file extension is xls or xlsx, that extension is valid.
	"""
	filename = file.split('\\')[-1]
	if filename.split('.')[-1] in ['xls', 'xlsx']:
		return True

	return False



def create_process_records(file_list):
	"""
	create records to be populated into table file_status.
	"""
	records = []
	for file in file_list:
		records.append((get_file_name(file), get_md5(file)))

	return records



def get_file_name(file_full_path):
	"""
	from the file full path, like

	C:\Program Files\Git\git\reconciliation_helper\samples\abc.xls

	workout the file name abc.xls
	"""
	return file_full_path.split('\\')[-1]
