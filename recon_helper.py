# coding=utf-8
# 
# Read the holdings section of the excel file from trustee.
#
# 

from datetime import datetime
from os import listdir
from os.path import isfile, isdir, join
from shutil import copy2
from xlrd import open_workbook
from reconciliation_helper.utility import logger, get_current_path, \
											get_output_directory, \
											get_input_directory
from reconciliation_helper.record import filter_files, save_result, \
											get_db_connection
from reconciliation_helper.sftp import upload
from reconciliation_helper.mail import send_notification
from jpm import open_jpm
from bochk import open_bochk
from DIF import open_dif



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
		if local_dir == output_dir:
			continue

		try:
			file_list = [join(local_dir, f) for f in listdir(local_dir) if isfile(join(local_dir, f))]
		except:
			logger.error('search_files(): access to {0} failed'.format(local_dir))
			logger.exception('search_files()')
			raise DirInaccessible()

		if len(file_list) > 0:
			files[folder] = file_list

	return files

	logger.debug('search_files() finish')



def convert(files, output_dir):
	"""
	Convert input files from different sources to Geneva format.

	files: {<sub_folder_name>:[list of files under that folder]}
	"""
	logger.debug('convert(): output to: {0}'.format(output_dir))
	func_map = {
		'clo equity': convert_jpm,
		'listco equity': convert_jpm,
		'concord': convert_bochk,
		'greenblue': convert_bochk,
		'clo bond': convert_bochk,
		'dif': convert_trustee,
		'special event fund': convert_bochk
	}
	result = {'pass':[], 'fail':[], 'output':[]}

	for sub_folder in files:
		try:
			handler = func_map[sub_folder.lower()]
		except KeyError:
			logger.error('convert(): no handler found for sub folder: {0}'.format(sub_folder))
			raise HandlerNotFound()
		
		output = handler(filter_files(files[sub_folder]), output_dir, result['pass'], result['fail'])
		result['output'] = result['output'] + output

	return result



def convert_jpm(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			wb = open_workbook(filename=filename)
			ws = wb.sheet_by_name('Sheet1')
			open_jpm.read_jpm(ws, port_values)
			output = open_jpm.write_csv(port_values, output_dir, get_filename_prefix(filename, 'jpm'))
			output_list = output_list + output
		except:
			logger.exception('convert_jpm()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_bochk(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:

		filename_no_path = filename.split('\\')[-1]
		if filename_no_path.startswith('Cash Stt'):
			read_handler = open_bochk.read_cash_bochk
			csv_handler = open_bochk.write_cash_csv
		elif filename_no_path.startswith('Holding'):
			read_handler = open_bochk.read_holdings_bochk
			csv_handler = open_bochk.write_holding_csv
		else:
			logger.warning('convert_bochk(): cannot tell whether it is a cash or holdings file: {0}'.
							format(filename))
			fail_list.append(filename)
			continue

		port_values = {}
		try:
			read_handler(filename, port_values)
			output = csv_handler(port_values, output_dir, get_filename_prefix(filename, 'bochk'))
			output_list.append(output)
		except:
			logger.exception('convert_bochk()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def convert_trustee(file_list, output_dir, pass_list, fail_list):
	output_list = []
	for filename in file_list:
		port_values = {}
		try:
			output = open_dif.open_dif(filename, port_values, output_dir)
			output_list = output_list + output
		except:
			logger.exception('convert_trustee()')
			fail_list.append(filename)
		else:
			pass_list.append(filename)

	return output_list



def get_filename_prefix(filename, source):
	"""
	Work out a prefix for the filename depending on the input directory.
	"""
	folder_name = filename.split('\\')[-2]
	prefix = ''
	for token in folder_name.lower().split():
		prefix = prefix + token + '_'

	return prefix + source + '_'



def copy_files(file_list, dstn_dir):
	"""
	Copy files to a predefined directory.
	"""
	for file in file_list:
		copy2(file, dstn_dir)



def show_result(result, upload_result):
	print('\n+++++++++++++++++++++++++++++++++++')
	print('Passed: {0}, Failed: {1}'.format(len(result['pass']), len(result['fail'])))
	if len(upload_result['fail']) == 0:
		print('All csv files have been uploaded')
	else:
		print('{0} csv files are not uploaded'.format(len(upload_result['fail'])))
	print('')

	for file in result['pass']:
		print('pass: {0}'.format(file))

	print('')
	for file in result['fail']:
		print('fail: {0}'.format(file))

	print('output files: {0}'.format(len(result['output'])))
	for file in result['output']:
		print(file)

	if len(upload_result['fail']) > 0:
		print('The following files have not been uploaded yet')
		for file in upload_result['fail']:
			print(file)




if __name__ == '__main__':
	try:
		output_dir = get_output_directory()
		files = search_files(get_input_directory(), output_dir)
		result = convert(files, output_dir)
		if result['pass'] == 0 and result['fail'] == 0:
			logger.info('recon_helper: no files to convert now.')
		else:
			save_result(result)
			get_db_connection().close()
			upload_result = upload(result['output'])
			# copy_files(upload_result['fail'], get_backup_directory())
			show_result(result, upload_result)
			send_notification(result, upload_result)

	except:
		logger.error('recon_helper: errors occurred')
		logger.exception('recon_helper:')
