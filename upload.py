# coding=utf-8
# 
# Upload files to a sftp site. The basic code comes from subproc package,
# sub.py module.
# 


from os.path import join
from subprocess import run, TimeoutExpired, CalledProcessError



def upload(file_list):
	"""

	"""
	try:
		args = [get_winscp_path(), '/script={0}'.format(create_winscp_script(file_list)), \
				'/log={0}'.format(get_winscp_log())]

		result = run(args, timeout=get_timeout(), check=True)
	except TimeoutExpired:

	except CalledProcessError:

	except:

	finally:
		pass_list = read_log(winscp_log)

	fail_list = create_fail_list(file_list, pass_list)
	return pass_list, fail_list	# which files got uploaded, which not