# coding=utf-8
# 
# Read the holdings section of the excel file from trustee.
#
# 

import datetime, os
from reconciliation_helper.utility import logger



def search_files(base_dir=None):
	"""
	Search files to be converted.
	"""
	logger.debug('search_files(): base_dir={0}'.format(base_dir))
	
	files = []
	return files

	logger.debug('search_files() finish')



if __name__ == '__main__':
	
	# filename = get_input_directory() + '\\' + sys.argv[1]
	# if not os.path.exists(filename):
	# 	print('{0} does not exist'.format(filename))
	# 	sys.exit(1)

	base_dir = 'C:\\Users\\steven.zhang\\AppData\\Local\\Programs\\Git\\git\\reconciliation_helper\\samples'
	search_files(base_dir)
