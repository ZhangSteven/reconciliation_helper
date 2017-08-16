# coding=utf-8
# 
# Read JPM and BOCHK files from trustee.
#
# 

from reconciliation_helper.recon_utility import read_jpm_file
from jpm.open_jpm import get_portfolio_date_as_string
from bochk.open_bochk import read_cash_bochk, read_holdings_bochk, \
								write_holding_csv, write_cash_csv, \
								read_cash_fields, read_cash_bochk
from datetime import datetime
from xlrd import open_workbook
import shutil
from os.path import isfile, isdir, join
from os import listdir, remove
from shutil import copy2
import logging
logger = logging.getLogger(__name__)



class InconsistentStatementDate(Exception):
	pass



def convert_trustee(file_list, output_dir, pass_list, fail_list):
	logger.debug('convert_trustee(): {0} files'.format(len(file_list)))
	if len(file_list) == 0:
		return []

	bochk_cash_files = []
	for filename in file_list:
		filename_no_path = filename.split('\\')[-1]
		if filename_no_path.lower().startswith('boc bank statement') \
			and is_bochk_cash_file(filename):
			bochk_cash_files.append(filename)
		
		elif filename_no_path.lower().startswith('jp morgan broker statement'):
			jpm_file = filename
		
		elif filename_no_path.lower().startswith('boc broker statement') \
			and (filename_no_path.lower().endswith('(class a-mc).xls') or \
				filename_no_path.lower().endswith('(a-mc).xls')):
			bochk_mc_file = filename
		
		elif filename_no_path.lower().startswith('boc broker statement'):
			bochk_hk_file = filename
	# end of for loop

	try:
		jpm_date, jpm_csv_files = handle_jpm(jpm_file, output_dir)
		bochk_date, bochk_mc_csv = handle_bochk_position(bochk_mc_file, 'mc', output_dir)
		bochk_date, bochk_hk_csv = handle_bochk_position(bochk_hk_file, 'hk', output_dir)

		if bochk_date != jpm_date:
			logger.error('convert_trustee(): bochk date {0} is not the same as jpm date {1}'.
							format(bochk_date, jpm_date))
			raise InconsistentStatementDate()

		bochk_cash_csv = handle_bochk_cash(bochk_cash_files, bochk_date, output_dir)

	except:
		logger.exception('convert_trustee()')
		# if one of the variables does not exist, then this will fail:
		# fail_list.extend([jpm_file, bochk_mc_file, bochk_hk_file])
		# 
		# so, change into below:
		if 'jpm_file' in locals():
			fail_list.append(jpm_file)
		if 'bochk_mc_file' in locals():
			fail_list.append(bochk_mc_file)
		if 'bochk_hk_file' in locals():
			fail_list.append(bochk_hk_file)
		return []
	else:
		pass_list.extend([jpm_file, bochk_mc_file, bochk_hk_file])
		try:
			move_files(file_list)
		except:
			logger.exception('convert_trustee(): error occurred while moving files, still continue.')

		return jpm_csv_files + [bochk_mc_csv, bochk_hk_csv, bochk_cash_csv]



def is_bochk_cash_file(filename):
	"""
	Tell whether a file is a BOCHK Bank Statement cash position file.
	"""
	cash_fields = ['Account Name', 'Account Number', 'Account Type',
					'Currency', 'Hold Amount']
	wb = open_workbook(filename=filename)
	ws = wb.sheet_by_index(0)
	try:
		fields = read_cash_fields(ws, 0)
		if len(fields) == 18:
			for i in range(5):	# check the first 5 fields
				if fields[i] != cash_fields[i]:
					return False

			return True

		else:
			return False
	
	except:
		logger.info('is_bochk_cash_file(): treat file as non cash file, because error occurs while reading fields from it, {0}'.
					format(filename))
		return False



def handle_jpm(jpm_file, output_dir):
	port_values = {}
	csv_files = read_jpm_file(jpm_file, port_values, output_dir)
	return port_values['date'], csv_files



def handle_bochk_position(bochk_position_file, source, output_dir):
	"""
	source: 'hk' or 'mc' to indicate which accounts they contain
	"""
	port_values = {}
	read_holdings_bochk(bochk_position_file, port_values)
	return port_values['holding_date'], \
			write_holding_csv(port_values, output_dir, 'trustee_' + source + '_bochk_')



def handle_bochk_cash(bochk_cash_files, cash_date, output_dir):
	"""
	Read a list of BOC HK bank statement files, produce a csv file that reflects
	the cash holding of all accounts.

	Note: sometimes we have multiple bank statements for the same account,
	then the account with a later date overrides others for the same account.
	"""
	cash_entries = []
	for filename in bochk_cash_files:
		port_values = {}
		read_cash_bochk(filename, port_values)
		update_cash_entries(port_values, cash_entries)
	
	port_values = {}
	port_values['cash'] = cash_entries
	port_values['cash_date'] = cash_date
	return write_cash_csv(port_values, output_dir, 'trustee_bochk_')



def update_cash_entries(port_values, cash_entries):
	for cash_entry in port_values['cash']:
		cash_entry['date'] = port_values['cash_date']
		found_existing_entry = False

		for existing_entry in cash_entries:
			if cash_entry['Account Name'] == existing_entry['Account Name'] \
				and cash_entry['Currency'] == existing_entry['Currency']:

				if cash_entry['date'] > existing_entry['date']:
					overwrite_entry(existing_entry, cash_entry)

				found_existing_entry = True
				break
		# finish searching for existing entry

		if not found_existing_entry:
			cash_entries.append(cash_entry)



def overwrite_entry(old_cash_entry, new_entry):
	for fld in new_entry:
		old_cash_entry[fld] = new_entry[fld]



def move_files(file_list):
	"""
	Move all files except the BOC HK broker statement and JPM broker statement
	to the 'cash statement' folder under the folder containing the files.
	"""
	dest_dir = ''
	if len(file_list) > 0:
		filename_no_path = file_list[0].split('\\')[-1]
		dest_dir = file_list[0][:-len(filename_no_path)]
		print(dest_dir)

	for filename in file_list:
		filename_no_path = filename.split('\\')[-1]
		
		if filename_no_path.lower().startswith('jp morgan broker statement') \
			or filename_no_path.lower().startswith('boc broker statement'):
			continue

		copy2(filename, join(dest_dir, 'cash statement'))
		remove(filename)




if __name__ == '__main__':
	"""
	Used to manually convert the files.

	"""

	input_dir = r'C:\temp\Reconciliation\trustee'
	file_list = [join(input_dir, f) for f in listdir(input_dir) if isfile(join(input_dir, f))]
	output_dir = r'C:\temp\Reconciliation\result'

	pass_list = []
	fail_list = []
	if convert_trustee(file_list, output_dir, pass_list, fail_list) == []:
		print('something goes wrong, check log file')
	else:
		print('OK')
