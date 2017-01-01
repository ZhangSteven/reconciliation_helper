"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import isfile, isdir, join
import shutil, os
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
        # shutil.rmtree(get_base_dir())



    def setup_dir(self):
        pass



    def test_create_winscp_script(self):
        directory = join(get_current_path(), 'samples', 'winscp_script')
        file_list = [r'C:\temp\file1', r'C:\temp\file2']
        suffix = '2012T0100'
        create_winscp_script(file_list, suffix, directory)



    def test_create_winscp_log(self):
        directory = join(get_current_path(), 'samples', 'winscp_log')
        suffix = '2012T0100'
        create_winscp_log(suffix, directory)