# coding=utf-8
# 
# Read JPM and BOCHK files from trustee.
#
# 

from reconciliation_helper.utility import logger
from datetime import datetime
from xlrd import open_workbook



def filter_greenblue(file_list):
	"""
	There are 6 files daily for Green Blue fund:

	2 files (Cash Stt, Holding) from BOCHK

	2 CCB China cash files for account 13000, 33000

	2 CCB China position files for account 13000, 33000
	
	The function filter them separately and return 3 lists to represent
	them.
	"""
	bochk_files = [] 
	CCB_cash_files = [] 
	CCB_position_files = []

	for filename in file_list:
		filename_no_path = filename.split('\\')[-1]
		if filename_no_path.startswith('Cash Stt') \
			or filename_no_path.startswith('Holding'):
			bochk_files.append(filename)
		
		elif filename_no_path.startswith('Cash Position'):
			CCB_cash_files.append(filename)
		
		elif filename_no_path.startswith('Security Holdings'):
			CCB_position_files.append(filename)

	return bochk_files, CCB_cash_files, CCB_position_files



def convert_CCB_cash(file_list, output_dir, pass_list, fail_list):
	return []



def convert_CCB_position(file_list, output_dir, pass_list, fail_list):
	return []



if __name__ == '__main__':
	"""
	Used to manually convert the files.

	"""
	from os.path import isfile, isdir, join
	from os import listdir
	input_dir = r'C:\temp\Reconciliation\greenblue'
	file_list = [join(input_dir, f) for f in listdir(input_dir) if isfile(join(input_dir, f))]
	output_dir = r'C:\temp\Reconciliation\result'

	pass_list = []
	fail_list = []
	try:
		output_list = convert_greenblue(file_list, output_dir, pass_list, fail_list)
	except:
		print('Something goes wrong, check log file.')
	else:
		if fail_list != []:
			print('Something goes wrong, check log file.')
		else:
			print('OK.')
