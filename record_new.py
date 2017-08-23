# coding=utf-8
# 
# Use a database to save the past file conversion records, which files
# are converted successfully.
# 

import sqlite3
import os
import datetime
import hashlib
from reconciliation_helper.utility import in_test_mode, enable_test_mode, \
											get_test_db_connection, get_db_file
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
		if file.split('\\')[-1].startswith('~') or not has_valid_extension(file):
			continue
			
		if not db_record_exists(file):
			process_list.append(file)

		else:
			logger.debug('filter_files(): {0} ignored'.format(file))
			
	return process_list



def save_result(result):
	"""
	Save the result to database.
	"""
	c = get_db_cursor()
	time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	c.executemany('INSERT INTO process_result (file_path, hash, result, time_stamp) VALUES (?, ?, ?, ?)', \
					create_process_records(result['pass'], 1, time_stamp))
	c.executemany('INSERT INTO process_result (file_path, hash, result, time_stamp) VALUES (?, ?, ?, ?)', \
					create_process_records(result['fail'], 0, time_stamp))
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
	# if 'conn' not in get_db_connection.__dict__:
	# 	get_db_connection.conn = None

	# if get_db_connection.conn is None:
	# 	if in_test_mode():
	# 		logger.info('get_db_connection(): connect to test database')
	# 		get_db_connection.conn = get_test_db_connection()
	# 	else:
	# 		logger.info('get_db_connection(): connect to database: records.db')
	# 		get_db_connection.conn = sqlite3.connect(os.path.join(get_current_path(), 'records.db'))

		# if 'conn' not in get_db_connection.__dict__:
	# 	get_db_connection.conn = None

	if 'conn' not in get_db_connection.__dict__:
		if in_test_mode():
			logger.info('get_db_connection(): connect to test database')
			get_db_connection.conn = get_test_db_connection()
		else:
			logger.info('get_db_connection(): connect to database: {0}'.format(get_db_file()))
			get_db_connection.conn = sqlite3.connect(get_db_file())
	
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



def create_process_records(file_list, process_result, time_stamp):
	"""
	create records to be populated into table file_status.
	"""
	records = []
	for file in file_list:
		records.append((file, get_sha256_hash(file), process_result, time_stamp))

	return records



def get_sha256_hash(file):
	"""
	workout the sha256 for a file.

	It may take a lot of memory if the file size is big. To handle large files, we
	need to read them into chunks and update the hash value per chunk. See:

	https://stackoverflow.com/a/22058673
	
	We use SHA256 as the hash function because it has better collission resistence
	then md5 or SHA1.
	"""
	logger.debug('get_sha256_hash(): {0}'.format(file))
	with open(file, 'rb') as f:
		return hashlib.sha256(f.read()).hexdigest()



def db_record_exists(file):
	"""
	Check whether the file has a process record in database.
	"""
	c = get_db_cursor()
	t = (file, get_sha256_hash(file))

	# test existence of a record, use the LIMIT clause
	c.execute('SELECT id FROM process_result WHERE file_path=? AND hash=? LIMIT 1', t)

	if c.fetchone() is None:
		return False
	else:
		return True