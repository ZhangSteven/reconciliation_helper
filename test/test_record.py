"""
Test the open_jpm.py
"""

import unittest2
import sqlite3
from datetime import datetime
from os.path import join
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.record import enable_test_mode, save_result



class TestRecords(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRecords, self).__init__(*args, **kwargs)

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



    def test_is_successful(self):
        """
        Use in memory database to test.
        """
        conn = setup_test_db()
        enable_test_mode(conn)



def setup_test_db():
    """
    Create an in memory sqlite3 database for testing only.
    """
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    sql = '''CREATE TABLE pass_files \
                (file_fullpath TEXT PRIMARY KEY NOT NULL, \
                m_time TEXT NOT NULL)'''
    c.execute(sql)

    sql = '''CREATE TABLE process_files \
                (id INTEGER PRIMARY KEY NOT NULL, \
                    file_fullpath TEXT NOT NULL, \
                    m_time TEXT NOT NULL, \
                    record_time TEXT NOT NULL, \
                    result TEXT NOT NULL)'''
    c.execute(sql)
    return conn