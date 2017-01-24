# coding=utf-8
# 
# Read JPM and BOCHK files from trustee.
#
# 

from reconciliation_helper.recon_helper import read_jpm_file
from reconciliation_helper.utility import logger
from jpm.open_jpm import get_portfolio_date_as_string
from bochk.open_bochk import read_file, write_holding_csv, write_cash_csv
from datetime import datetime



class InconsistentStatementDate(Exception):
	pass



def convert_trustee(file_list, output_dir, pass_list, fail_list):
	output_list = []
	bochk_cash_files = []

	for filename in file_list:

		filename_no_path = filename.split('\\')[-1]
		if filename_no_path.startswith('BOC Bank Statement') \
			and is_cash_file(filename):
			bochk_cash_files.append(filename)
		
		elif filename_no_path.startswith('JP Morgan Broker Statement'):
			jpm_file = filename
		
		elif filename_no_path.startswith('BOC Broker Statement') \
			and filename_no_path.endswith('(Class A-MC).xls'):
			bochk_mc_file = filename
		
		elif filename_no_path.startswith('BOC Broker Statement'):
			bochk_hk_file = filename
	# end of for loop

	try:
		jpm_date = handle_jpm(jpm_file, output_dir, output_list)
		bochk_date = handle_bochk_position(bochk_mc_file, bochk_hk_file, output_dir, output_list)

		if bochk_date != jpm_date:
			logger.error('convert_trustee(): bochk date {0} is not the same as jpm date {1}'.
							format(bochk_date, jpm_date))
			raise InconsistentStatementDate()

		handle_bochk_cash(bochk_cash_files, bochk_date, output_dir, output_list)

	except:
		logger.exception('convert_trustee()')
		# fail_list.append(filename)
	else:
		pass_list + [jpm_file, bochk_mc_file, bochk_hk_file, ]

	return output_list



def handle_jpm(jpm_file, output_dir, output_list):
	port_values = {}
	output_list = output_list + read_jpm_file(jpm_file, port_values, output_dir)
	return port_values['date']



def handle_bochk_position(bochk_mc_file, bochk_hk_file, output_dir, output_list):
	port_values = {}
	read_file(bochk_mc_file, port_values)
	output_list.append(write_holding_csv(port_values, output_dir, 'trustee_mc_bochk'))

	port_values = {}
	read_file(bochk_hk_file, port_values)
	output_list.append(write_holding_csv(port_values, output_dir, 'trustee_hk_bochk'))
	return port_values['holding_date']



def handle_bochk_cash(bochk_cash_files, cash_date, output_dir, output_list):
	port_values = {}
	read_bochk_cash_files(bochk_cash_files, port_values)
	port_values['cash_date'] = cash_date
	output_list.append(write_cash_csv(port_values, output_dir, 'trustee_bochk'))




if __name__ == '__main__':
	"""
	Use the following to invoke the program if you don't want to save to 
	database, no upload and no notification email sending:

	python recon_helper.py --mode simple

	Or if you want all of the functions to be there, then:

	python recon_helper.py

	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', nargs='?', metavar='mode', default='normal')
	args = parser.parse_args()

	try:
		output_dir = get_output_directory()
		files = search_files(get_input_directory(), output_dir)
		result = convert(files, output_dir)
		upload_result = {'pass':[], 'fail':[]}
		if len(result['pass']) == 0 and len(result['fail']) == 0:
			print('no files to convert now.')
			logger.info('recon_helper: no files to convert now.')
		
		elif args.mode == 'normal':
			save_result(result)
			
			if len(result['output']) > 0:
				upload_result = upload(result['output'])
				# copy_files(upload_result['fail'], get_backup_directory())

			send_notification(result, upload_result)

		else:
			print('Working in simple mode, no database saving, no upload, no notification.')

		show_result(result, upload_result)			
		get_db_connection().close()
	except:
		print('Something goes wrong, check log file.')
		logger.error('recon_helper: errors occurred')
		logger.exception('recon_helper:')
	else:
		print('OK')
