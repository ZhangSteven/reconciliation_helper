# coding=utf-8
# 
# Use a database to save the past file conversion records, which files
# are converted successfully.
# 

from reconciliation_helper.utility import logger, get_current_path



def filter_files(file_list):
	"""
	Pick the approapriate files from the file list based on the following
	criteria:

	1. Format: files must be in 'xls' or 'xlsx' format.
	2. Not successful before: files not found in the successful file list
	3. Last modified time stamp: if a file is in the successful file list,
		but its last modified time stamp is newer than that in the record.
	"""
	new_file_list = []
	for file in file_list:
		if has_valid_extension(file):
			if is_successful(file):
				if get_modified_time_stamp(file) > get_successful_modified_time_stamp(file):
					new_file_list.append(file)
			else:
				new_file_list.append(file)

	return new_file_list



def save_result(result):
	"""
	Save the successful and failed file list to database.

	result = {'pass':[list of passed files], 'fail':[list of failed files]}
	"""
	pass



def is_successful(file):
	"""
	Search the database and determine whether it is a successful file.
	"""
	return False



def has_valid_extension(file):
	"""
	file: a full path file name, like C:\temp\sample.txt
	
	If the file extension is xls or xlsx, that extension is valid.
	"""
	filename = file.split('\\')[-1]
	if filename.split('.')[-1] in ['xls', 'xlsx']:
		return True

	return False



def get_modified_time_stamp(file):
	return 0



def get_successful_modified_time_stamp(file):
	return 0