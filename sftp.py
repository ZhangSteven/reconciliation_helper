# coding=utf-8
# 
# Upload files to a sftp site. The basic code comes from subproc package,
# sub.py module.
# 

import time, os
from os.path import join
from subprocess import run, TimeoutExpired, CalledProcessError
from reconciliation_helper.utility import logger, get_winscp_script_directory, \
											get_winscp_log_directory, \
											get_winscp_path, get_timeout



def upload(file_list):
	"""
	Call winscp.com to execute the sftp upload job.
	"""
	winscp_script, winscp_log = create_winscp_files(file_list)
	try:
		args = [get_winscp_path(), '/script={0}'.format(winscp_script), \
				'/log={0}'.format(winscp_log)]

		result = run(args, timeout=get_timeout(), check=True)
	except TimeoutExpired:
		logger.error('upload(): timeout {0} expired'.format(get_timeout()))
	except CalledProcessError:
		logger.error('upload(): upload job did not complete successfully')
	except:
		logger.error('upload(): some other error occurred')
		logger.exception('upload():')

	result = {}
	result['pass'] = read_log(winscp_log)
	result['fail'] = get_fail_list(file_list, result['pass'])
	return result



def create_winscp_files(file_list):
	time_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	tokens = time_string.split()[1].split(':')
	suffix = time_string.split()[0] + 'T' + tokens[0] + tokens[1] + tokens[2]
	
	return create_winscp_script(file_list, suffix), \
			create_winscp_log(suffix)



def create_winscp_script(file_list, suffix, directory=None):
	"""
	Create a script file to be loaded by WinSCP.com, a sample file looks like:

	open sftp://demo:password@test.rebex.net/
	cd pub/example
	get ConsoleClient.png
	exit

	Parameter directory is mainly for test purpose, so the test code
	can put in a different test directory.
	"""
	if directory is None:
		directory = get_winscp_script_directory()

	script_file = join(directory, 'run-sftp_{0}.txt'.format(suffix))
	with open(script_file, 'w') as f:
		f.write(r'open sftp://demo:password@test.rebex.net/'+'\n')
		f.write(r'cd pub/example'+'\n')
		for file in file_list:
			f.write('get {0}\n'.format(file))

		f.write('exit')

	return script_file



def create_winscp_log(suffix, directory=None):
	"""
	Create an empty log file, because winscp.com needs an existing log
	file to start logging.

	Parameter directory is mainly for test purpose, so the test code
	can put in a different test directory.
	"""
	if directory is None:
		directory = get_winscp_log_directory()

	log_file = join(directory, 'log_{0}.txt'.format(suffix))
	with open(log_file, 'w') as f:	# just create an empty file
		pass

	return log_file



def read_log(winscp_log):
	"""
	Look for successful transfer records in the winscp logfile, then report
	which files are successfully transferred, and the date and time those
	transfers are completed.

	The successful transfer records are in the following format (get and put)

	> 2016-12-29 17:20:40.652 Transfer done: '<file full path>' [xxxx]

	The starting symbol can be '>', '<', '.', '!', depending on the type of
	the record.

	If it is a get, then 'file full path' will be the remote directory's
	file path. If it is a put, then 'file full path' will be the local
	directory's file path.
	"""
	successful_list = []
	with open(winscp_log) as f:
		for line in f:
			tokens = line.split()
			# print(tokens)
			if len(tokens) < 6:
				continue

			if tokens[3] == 'Transfer' and tokens[4] == 'done:':
				successful_list.append([tokens[5][1:-1]])

	return successful_list



def get_fail_list(file_list, pass_list):
	fail_list = []

	return fail_list



if __name__ == '__main__':
	file_list = ['ConsoleClient.png', 'FtpDownloader.png', 'mail-editor.png']
	upload(file_list)