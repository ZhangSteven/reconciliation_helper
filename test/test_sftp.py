"""
Test the open_jpm.py
"""

import unittest2
from os.path import isfile, join
from glob import glob
import os
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.sftp import create_winscp_script, create_winscp_log


class TestSftp(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSftp, self).__init__(*args, **kwargs)

    def setUp(self):
        """
            Run before a test function.
            Just clear contents in a testing database.
        """
        pass

    def tearDown(self):
        """
            Run after a test finishes
        """
        pass



    def test_create_winscp_script(self):
        delete_test_script_files()
        file_list = [r'C:\temp\file1', r'C:\temp\file2']
        suffix = '2012T0100'
        script_file = create_winscp_script(file_list, suffix, \
						get_test_winscp_script_dir())
        self.assertTrue(isfile(script_file))	# file exists



    def test_create_winscp_log(self):
        delete_test_log_files()
        suffix = '2012T0100'
        log_file = create_winscp_log(suffix, get_test_winscp_log_dir())
        # print(log_file)
        self.assertTrue(isfile(log_file))	# file exists



def get_test_winscp_script_dir():
	return join(get_current_path(), 'samples', 'winscp_script')



def get_test_winscp_log_dir():
    return join(get_current_path(), 'samples', 'winscp_log')



def delete_test_log_files():
	for file in glob(join(get_test_winscp_log_dir(), '*.txt')):
		os.remove(file)



def delete_test_script_files():
	for file in glob(join(get_test_winscp_script_dir(), '*.txt')):
		os.remove(file)