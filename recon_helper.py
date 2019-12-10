# coding=utf-8
# 
# Read the holdings section of the excel file from trustee.
#
# 
import argparse, sys
from datetime import datetime
from os import listdir
from os.path import isfile, isdir, join
from shutil import copy2
from functools import partial, reduce
from xlrd import open_workbook
from reconciliation_helper.utility import get_current_path, \
											get_output_directory, \
											get_input_directory
from reconciliation_helper.recon_utility import read_jpm_file, \
											get_filename_prefix
from reconciliation_helper.trustee import convert_trustee
from reconciliation_helper.greenblue import filter_greenblue, convert_CCB_cash, \
											convert_CCB_position
from reconciliation_helper.record import filter_files, save_result, \
											get_db_connection
from reconciliation_helper.sftp import upload
from reconciliation_helper.mail import send_notification
from jpm import open_jpm
from jpm_revised import jpm2
from bochk import open_bochk
from IB import ib, henghua, guangfa
# from DIF import open_dif, open_bal
from dif_revised.geneva import open_dif
from citi import open_citi
from hsbc_repo import hsbc
from cmbhk import cmb
from nomura.main import outputCsv as nomura_outputCsv
from cmbc.main import outputCsv as cmbc_outputCsv
from bochk_revised.main import outputCsv as bochk_outputCsv
from webservice_client.nav import upload_nav

import logging
logger = logging.getLogger(__name__)



class DirInaccessible(Exception):
	pass

class BasedirEmpty(Exception):
	pass

class HandlerNotFound(Exception):
	pass



def search_files(base_dir, output_dir):
	"""
	Search files to be converted.
	"""
	logger.debug('search_files(): base_dir={0}'.format(base_dir))
	try:
		sub_folders = listdir(base_dir)
	except:
		logger.error('search_files(): access to {0} failed'.format(base_dir))
		logger.exception('search_files()')
		raise DirInaccessible()

	if len(sub_folders) == 0:
		logger.error('search_files(): base dir empty:{0}'.format(base_dir))
		raise BasedirEmpty()

	files = {}
	for folder in sub_folders:
		if not isdir(join(base_dir, folder)):
			# print(folder)
			continue

		local_dir = join(base_dir, folder)
		if local_dir == output_dir:	# skip the output dir ("result")
			continue

		try:
			file_list = [join(local_dir, f) for f in listdir(local_dir) if isfile(join(local_dir, f))]
		except:
			logger.error('search_files(): access to {0} failed'.format(local_dir))
			logger.exception('search_files()')
			raise DirInaccessible()

		if len(file_list) > 0:
			files[folder] = file_list
			# print(folder)

	return files

	logger.debug('search_files() finish')



def convert(files, output_dir):
	"""
	Convert input files from different sources to Geneva format.

	files: {<sub_folder_name>:[list of files under that folder]}
	"""
	logger.debug('convert(): output to: {0}'.format(output_dir))
	func_map = {
		'listco equity': convert_jpm,
		'test listco equity': convert_jpm2,
		# 'concord': convert_bochk,
		'ffx': partial(converter, bochk_outputCsv),
		'greenblue': convert_greenblue,
		'dif': convert_dif,
		'macau balanced fund': convert_dif,
		'macau guarantee fund': convert_dif,
		'macau growth fund': convert_dif,
		'special event fund': partial(converter, bochk_outputCsv),
		'trustee': convert_trustee,
		'star helios': convert_citi,
		'in-house fund': partial( converter, bochk_outputCsv
								, filter_func=in_house_filter),
		'jic international': convert_bochk,
		'jic-repo': partial(convert_repo, '40002'),
		'global fixed income spc (cmbhk)': partial(convert_cmbhk, '40017'),
		'global fixed income spc (pb)': partial( converter, nomura_outputCsv
											   , filter_func=global_fixed_income_spc_filter),
		'first seafront fund': partial( converter, cmbc_outputCsv
									  , filter_func=first_seafront_fund_filter),
		'ib': convert_ib,
		'hgnh': convert_hgnh,
		'quant fund 40006 (cmbhk)': partial(convert_cmbhk, '40006'),
		'gf': convert_guangfa
	}
	result = {'pass':[], 'fail':[], 'output':[]}

	for sub_folder in files:
		try:
			handler = func_map[sub_folder.lower()]

			output = handler(filter_files(files[sub_folder]), output_dir, result['pass'], result['fail'])
			result['output'] = result['output'] + output

		except KeyError:
			# logger.error('convert(): no handler found for sub folder: {0}'.format(sub_folder))
			# raise HandlerNotFound()
			logger.warning('convert(): no handler found for sub folder: {0}'.format(sub_folder))

	return result



def convert_dummy(file_list, output_dir, pass_list, fail_list):
	return []



def converter( convert_func, file_list, output_dir, pass_list, fail_list
			 , filter_func = lambda x: True):
	"""
	[Function] convert_func ([String] file, [String] output_dir -> output),
	[Iterable] file_list (input file list),
	[String] output_dir,
	[List] pass_list,
	[List] fail_list,
	[Function] filter_func ([String] file -> [Bool]) 

	=> 

	[List] output_list (output csv files)

	Side effect: update pass_list and fail_list
	"""
	add_to_list = lambda L, el: \
		L + el if isinstance(el, list) else \
		L + list(el) if isinstance(el, tuple) else \
		L + [el]


	def build_output(output_list, file):
		try:
			logger.debug('converter(): processing {0}'.format(file))
			result = convert_func(file, output_dir)
			pass_list.append(file)
			return add_to_list(output_list, result)
		except:
			logger.exception('converter(): {0}'.format(file))
			fail_list.append(file)
			return output_list

	
	return reduce(build_output, filter(filter_func, file_list), [])



def convert_40006(file_list, output_dir, pass_list, fail_list,
					cashOrPosition, fileProcessor, msg):
	output_list = []
	for filename in filter(cashOrPosition, file_list):
		try:
			output_list.append(fileProcessor(filename, output_dir))
		except:
			logger.exception(msg)
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_ib(file_list, output_dir, pass_list, fail_list):
	return convert_40006(file_list, output_dir, pass_list, fail_list \
						 , ib.isCashOrPositionFile \
						 , ib.processCashPositionFile \
						 , 'convert_ib()')



def convert_hgnh(file_list, output_dir, pass_list, fail_list):
	return convert_40006(file_list, output_dir, pass_list, fail_list \
						 , henghua.isCashOrPositionFile \
						 , henghua.processCashPositionFile \
						 , 'convert_hgnh()')



def convert_guangfa(file_list, output_dir, pass_list, fail_list):
	return convert_40006(file_list, output_dir, pass_list, fail_list \
						 , guangfa.isCashOrPositionFile \
						 , guangfa.processCashPositionFile \
						 , 'convert_guangfa()')



def convert_jpm(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			# wb = open_workbook(filename=filename)
			# ws = wb.sheet_by_name('Sheet1')
			# open_jpm.read_jpm(ws, port_values)
			# output = open_jpm.write_csv(port_values, output_dir, get_filename_prefix(filename, 'jpm'))
			# output_list = output_list + output
			output_list.extend(read_jpm_file(filename, port_values, output_dir))
		except:
			logger.exception('convert_jpm()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_jpm2(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		try:
			output_list = output_list + \
							jpm2.toCsv(filename, output_dir, get_filename_prefix(filename, 'jpm'))
		except:
			logger.exception('convert_jpm2()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_bochk(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			open_bochk.read_file(filename, port_values)
			output = open_bochk.write_cash_or_holding_csv(port_values, output_dir, get_filename_prefix(filename, 'bochk'))
			output_list.append(output)
		except:
			logger.exception('convert_bochk()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_dif(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			output = open_dif(filename, port_values, output_dir, get_filename_prefix(filename, ''))
			validate_and_upload(port_values)
			output_list = output_list + output
		except:
			logger.exception('convert_dif()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_citi(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			output = open_citi.open_citi(filename, port_values, output_dir, get_filename_prefix(filename, 'citi'))
			output_list = output_list + output
		except:
			logger.exception('convert_citi()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_greenblue(file_list, output_dir, pass_list, fail_list):
	logger.debug('convert_greenblue(): {0} files'.format(len(file_list)))
	bochk_files, CCB_cash_files, CCB_position_files = filter_greenblue(file_list)
	output_list = convert_bochk(bochk_files, output_dir, pass_list, fail_list)
	output_list.extend(convert_CCB_cash(CCB_cash_files, output_dir, pass_list, fail_list))
	output_list.extend(convert_CCB_position(CCB_position_files, output_dir, pass_list, fail_list))
	
	return output_list



def convert_repo(portfolio, file_list, output_dir, pass_list, fail_list):
	logger.debug('convert_repo(): {0} files'.format(len(file_list)))

	def is_hsbc_repo(filename):
		# if filename_from_path(filename).split('.')[0].lower().startswith('repo exposure trades and collateral position'):
		# 	return True
		# else:
		# 	return False

		# so far there is only type of REPO report (HSBC)
		return True


	output_list = []
	for filename in file_list:
		try:
			if is_hsbc_repo(filename):
				output_list.append(hsbc.toCsv(portfolio, filename, output_dir, get_filename_prefix(filename, 'hsbc_repo')))

		except:
			logger.exception('convert_repo(): {0}'.format(filename))
			fail_list.append(filename)
		else:
			pass_list.append(filename)


	return output_list



def convert_cmbhk(portfolio, file_list, output_dir, pass_list, fail_list):
	logger.debug('convert_cmbhk(): {0} files'.format(len(file_list)))

	output_list = []
	for filename in file_list:
		try:
			output_list.append(cmb.toCsv(portfolio, filename, output_dir, get_filename_prefix(filename, '')))

		except:
			logger.exception('convert_cmbhk(): {0}'.format(filename))
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



filename_wo_path = lambda fn: \
	fn.split('\\')[-1]



first_seafront_fund_filter = lambda file: \
	(lambda fn: \
		fn[-4:] in ['.xls', 'xlsx'] and \
		(fn.split('.')[0].endswith('cash_pos') or fn.startswith('security holding'))
	)(filename_wo_path(file).lower())



global_fixed_income_spc_filter = lambda file: \
	(lambda fn: \
		fn[-5:] == '.xlsx' and (fn.startswith('cash stt') or fn.startswith('holding'))
	)(filename_wo_path(file).lower())
	


in_house_filter = lambda file: \
	(lambda fn: \
		not 'minsheng' in fn and (fn.startswith('cash stt') or fn.startswith('holding'))
	)(filename_wo_path(file).lower())



def filename_from_path(filepath):
	"""
	[String] filepath => [String] filename

	filepath: a string representing the full path of a file, like 
		"C:\\temp\\result.xlsx"

	filename: file name without the path, like "result.xlsx"
	"""
	return filepath.split('\\')[-1]



def copy_files(file_list, dstn_dir):
	"""
	Copy files to a predefined directory.
	"""
	for file in file_list:
		copy2(file, dstn_dir)



def show_result(result, upload_result):
	print('\n+++++++++++++++++++++++++++++++++++')
	print('Passed: {0}, Failed: {1}'.format(len(result['pass']), len(result['fail'])))
	# if len(upload_result['pass']) > 0 and len(upload_result['fail']) == 0:
	# 	print('All {0} csv files have been uploaded'.format(len(upload_result['pass'])))
	# elif len(upload_result['pass']) == 0 and len(upload_result['fail']) == 0:
	# 	print('No csv files to upload')
	# else:
	# 	print('{0} csv files are not uploaded'.format(len(upload_result['fail'])))
	print('')

	for file in result['pass']:
		# print('pass: {0}'.format(file))
		print('pass: {0}'.format(file.replace(u'\xa0', u' ')))

	print('')
	for file in result['fail']:
		# print('fail: {0}'.format(file))
		print('fail: {0}'.format(file.replace(u'\xa0', u' ')))

	print('\n\noutput files: {0}'.format(len(result['output'])))
	for file in result['output']:
		print(file)

	# if len(upload_result['fail']) > 0:
	# 	print('The following files have not been uploaded yet')
	# 	for file in upload_result['fail']:
	# 		print(file)



# def validate_and_upload(port_values):
# 	"""
# 	Validate the nav, num_units, unit price for the daily funds:
# 	19437, 30003, 30004
# 	"""
# 	logger.info('validate_and_upload(): portfolio {0}'.format(port_values['portfolio_id']))
# 	if abs(port_values['nav']/port_values['number_of_units'] - port_values['unit_price']) < 1.0e-4:
# 		if upload_nav(port_values['portfolio_id'], 
# 					port_values['nav'],
# 					'-'.join([str(port_values['date'].year), str(port_values['date'].month), str(port_values['date'].day)]),
# 					port_values['number_of_units'],
# 					port_values['unit_price']):

# 			logger.debug('validate_and_upload(): upload successful.')

# 		else:
# 			logger.error('validate_and_upload(): upload failed.')

# 	else:
# 		logger.error('validate_and_upload(): validation failed, nav={0}, units={1}, unit price={2}'.
# 						format(port_values['nav'], port_values['number_of_units'], port_values['unit_price']))

def validate_and_upload(port_values):
	"""
	Validate the nav, num_units, unit price for the daily funds:
	19437, 30003, 30004
	"""
	logger.info('validate_and_upload(): portfolio {0}'.format(port_values['portfolio']))

	if upload_nav(port_values['portfolio'], port_values['nav'],
				port_values['valuation_date'], port_values['number_of_units'],
				port_values['unit_price']):

		logger.debug('validate_and_upload(): upload successful.')

	else:
		logger.error('validate_and_upload(): upload failed.')




if __name__ == '__main__':
	"""
	Use the following to invoke the program if you don't want to save to 
	database, no upload and no notification email sending:

	python recon_helper.py

	Or if you want all of the functions to be there, then:

	python recon_helper.py --mode production

	"""
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', nargs='?', metavar='mode', default='test')
	args = parser.parse_args()

	try:
		output_dir = get_output_directory()
		files = search_files(get_input_directory(), output_dir)
		result = convert(files, output_dir)
		upload_result = {'pass':[], 'fail':[]}
		if len(result['pass']) == 0 and len(result['fail']) == 0:
			logger.info('recon_helper: no files to convert now.')
		
		elif args.mode == 'production':
			save_result(result)
			
			if len(result['output']) > 0:
				upload_result = upload(result['output'])
				# copy_files(upload_result['fail'], get_backup_directory())

			send_notification(result, upload_result)

		else:
			logger.info('Working in test mode, no database/ftp/email notification.')

		show_result(result, upload_result)			
		get_db_connection().close()

	except:
		logger.exception('recon_helper: errors occurred')

