# coding=utf-8
# 


from xlrd import open_workbook
from jpm import open_jpm
import logging
logger = logging.getLogger(__name__)



def read_jpm_file(filename, port_values, output_dir):
	"""
	Read a JPM broker statement file, return the two csv filenames.
	"""
	wb = open_workbook(filename=filename)
	ws = wb.sheet_by_index(0)
	open_jpm.read_jpm(ws, port_values)
	return open_jpm.write_csv(port_values, output_dir, get_filename_prefix(filename, 'jpm'))



def get_filename_prefix(filename, source):
	"""
	Work out a prefix for the filename depending on the input directory.
	"""
	folder_name = filename.split('\\')[-2]
	prefix = ''
	for token in folder_name.lower().split():
		prefix = prefix + token + '_'

	if source == '':
		return prefix
	else:
		return prefix + source + '_'	

