# coding=utf-8
# 
# Populate process results into the new sqlite3_records.db
#
# 

from reconciliation_helper.recon_helper import search_files
from reconciliation_helper.utility import get_input_directory, get_output_directory
from reconciliation_helper.record_new import save_result, get_db_connection, filter_files
import logging
logger = logging.getLogger(__name__)



def create_result(files):
	"""
	Create a list of successful records.
	"""
	result = {'pass':[], 'fail':[], 'output':[]}

	for sub_folder in files:
		result['pass'] = result['pass'] + filter_files(files[sub_folder])

	return result




if __name__ == '__main__':
	"""
	Search and filter files from the input directory, create a list of successful
	process results. Used to populate the sqlite3_records.db database before we
	put it into production.
	"""
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	try:
		files = search_files(get_input_directory(), get_output_directory())
		save_result(create_result(files))
		get_db_connection().close()

	except:
		logger.exception('recon_helper: errors occurred')

