"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.recon_helper import search_files



class TestRecon(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRecon, self).__init__(*args, **kwargs)

    def setUp(self):
        """
            Run before a test function
        """
        pass

    def tearDown(self):
        """
            Run after a test finishes
        """
        pass



    def test_retrieve_date_from_filename(self):
        base_dir = get_current_path() + '\\samples'
        search_files(base_dir)
