# coding=utf-8
# 
# from config_logging package, provides a config object (from config file)
# and a logger object (logging to a file).
# 

import configparser, os



def get_current_path():
	"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
	"""
	return os.path.dirname(os.path.abspath(__file__))



def _load_config(filename='recon_helper.config'):
	"""
	Read the config file, convert it to a config object. The config file is 
	supposed to be located in the same directory as the py files, and the
	default name is "config".

	Caution: uncaught exceptions will happen if the config files are missing
	or named incorrectly.
	"""
	path = get_current_path()
	config_file = path + '\\' + filename
	# print(config_file)
	cfg = configparser.ConfigParser()
	cfg.read(config_file)
	return cfg



# initialized only once when this module is first imported by others
if not 'config' in globals():
	config = _load_config()



# def get_base_directory():
# 	"""
# 	The directory where the log file resides.
# 	"""
# 	global config
# 	directory = config['logging']['directory']
# 	if directory == '':
# 		directory = get_current_path()

# 	return directory



def in_test_mode():
	"""
	Determine whether the program runs in test mode. By default it is not.
	"""
	global config
	if config['test']['testmode']:
		return True
	else:
		return False



test_conn = None
def enable_test_mode(db_conn):
	"""
	Setup the test_mode flag to True, call this function only when doing unittest.
	"""
	global config
	config['test']['testmode'] = 'set'

	global test_conn
	test_conn = db_conn



def get_test_db_connection():
	global test_conn
	return test_conn



def get_input_directory():
	"""
	Read directory from the config object and return it.
	"""
	global config
	directory = config['directory']['input']
	if directory.strip() == '':
		directory = get_current_path()

	return directory



def get_output_directory():
	"""
	Read directory from the config object and return it.
	"""
	global config
	directory = config['directory']['output']
	if directory.strip() == '':
		directory = get_current_path()

	return directory



def get_backup_directory():
	global config
	return config['directory']['backup']

	

def get_winscp_path():
	global config
	return config['winscp']['application']



def get_winscp_script_directory():
	global config
	return config['winscp']['script_dir']



def get_winscp_log_directory():
	global config
	return config['winscp']['log_dir']



def get_timeout():
	global config
	return float(config['sftp']['timeout'])



def get_sftp_server():
	global config
	return config['sftp']['server']



def get_sftp_user():
	global config
	return config['sftp']['username']



def get_sftp_password():
	global config
	return config['sftp']['password']



def get_mail_sender():
	global config
	return config['email']['sender']



def get_mail_recipients():
	global config
	return config['email']['recipents']



def get_mail_server():
	global config
	return config['email']['server']



def get_mail_timeout():
	global config
	return float(config['email']['timeout'])



def get_db_file():
	global config
	return config['database']['db_file']