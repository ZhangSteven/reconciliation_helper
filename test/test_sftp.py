"""
Test the open_jpm.py
"""

import unittest2
from os.path import isfile, join
from glob import glob
import os
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.sftp import create_winscp_script, create_winscp_log, \
                                        read_log, get_fail_list, InvalidPassList
from reconciliation_helper.recon_helper import copy_files



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



    def test_read_log(self):
        pass_list = read_log(join(get_current_path(), 'samples', 'log_0file.txt'))
        self.assertEqual(len(pass_list), 0)

        pass_list = read_log(join(get_current_path(), 'samples', 'log_1file_then_timeout.txt'))
        self.assertEqual(len(pass_list), 1)
        # print(pass_list)
        self.assertEqual(pass_list[0], '/pub/example/ConsoleClient.png')

        pass_list = read_log(join(get_current_path(), 'samples', 'log_3files.txt'))
        self.assertEqual(len(pass_list), 3)
        self.assertEqual(pass_list[0], '/pub/example/ConsoleClient.png')
        self.assertEqual(pass_list[1], '/pub/example/FtpDownloader.png')
        self.assertEqual(pass_list[2], '/pub/example/mail-editor.png')



    def test_get_fail_list(self):
        file_list = ['a', 'b', 'c']
        pass_list = ['b']
        self.assertTrue(compare_list(get_fail_list(file_list, pass_list), ['a', 'c']))

        file_list = ['a', 'b', 'c']
        pass_list = ['c', 'a']
        self.assertEqual(get_fail_list(file_list, pass_list), ['b'])

        file_list = ['a', 'b', 'c']
        pass_list = ['b', 'a', 'c']
        self.assertEqual(get_fail_list(file_list, pass_list), [])

        file_list = ['a', 'b', 'c']
        pass_list = []
        self.assertTrue(compare_list(get_fail_list(file_list, pass_list), ['a', 'b', 'c']))

        file_list = ['a', 'b', 'c']
        pass_list = ['b', 'd']
        with self.assertRaises(InvalidPassList):
            get_fail_list(file_list, pass_list)



    def test_copy_files(self):
        delete_test_temp_files()
        self.assertEqual(len(glob(join(get_test_temp_dir(), '*.txt'))), 0)
        file_list = [join(get_current_path(), 'samples', 'log_0file.txt'), \
                        join(get_current_path(), 'samples', 'log_3files.txt')]
        copy_files(file_list, get_test_temp_dir())
        self.assertEqual(len(glob(join(get_test_temp_dir(), '*.txt'))), 2)



def get_test_winscp_script_dir():
	return join(get_current_path(), 'samples', 'winscp_script')



def get_test_winscp_log_dir():
    return join(get_current_path(), 'samples', 'winscp_log')



def get_test_temp_dir():
    return join(get_current_path(), 'samples', 'temp')



def delete_test_log_files():
	for file in glob(join(get_test_winscp_log_dir(), '*.txt')):
		os.remove(file)



def delete_test_script_files():
	for file in glob(join(get_test_winscp_script_dir(), '*.txt')):
		os.remove(file)



def delete_test_temp_files():
    for file in glob(join(get_test_temp_dir(), '*.txt')):
        os.remove(file)



def compare_list(list_a, list_b):
    """
    Assume list_a contain no duplicate items.
    """
    if len(list_a) != len(list_b):
        return False

    for item in list_a:
        if not item in list_b:
            return False

    return True