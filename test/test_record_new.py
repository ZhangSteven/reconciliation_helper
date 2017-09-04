"""
Test the open_jpm.py
"""

import unittest2
import sqlite3
from datetime import datetime
from os.path import join
from reconciliation_helper.utility import get_current_path, enable_test_mode
from reconciliation_helper.record_new import save_result, get_db_connection, \
                                                get_db_cursor, filter_files, \
                                                db_record_exists



class TestRecordsNew(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRecordsNew, self).__init__(*args, **kwargs)
        conn = setup_test_db()
        enable_test_mode(conn)

    def setUp(self):
        """
            Run before a test function.
            Just clear contents in a testing database.
        """
        c = get_db_cursor()
        c.execute('DELETE FROM process_result')
        
    def tearDown(self):
        """
            Run after a test finishes
        """
        pass



    def test_db_record_exists(self):
        concord_holding_file = join(get_current_path(), 'samples', 'Reconciliation', 'Concord', 'Holding _ 15082017.xlsx')
        self.assertFalse(db_record_exists(concord_holding_file))    # the database is empty

        concord_cash_file = join(get_current_path(), 'samples', 'Reconciliation', 'Concord', 'Cash Stt _ 15082017.xlsx')        
        result = {
            'pass': [concord_holding_file],
            'fail': [concord_cash_file]
        }
        save_result(result)
        self.assertTrue(db_record_exists(concord_holding_file))
        self.assertTrue(db_record_exists(concord_cash_file))

        c = get_db_cursor()
        sql = '''SELECT * FROM process_result'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 2)

        sql = '''SELECT * FROM process_result WHERE result=0'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], concord_cash_file)
        self.assertEqual(len(result[0][2]), 64) # the SHA256 hash
        self.assertEqual(result[0][3], 0)       # process result is fail
        self.assertEqual(result[0][4].split()[0], datetime.today().strftime('%Y-%m-%d'))

        sql = '''SELECT * FROM process_result WHERE result=1'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], concord_holding_file)
        self.assertEqual(len(result[0][2]), 64) # the SHA256 hash
        self.assertEqual(result[0][3], 1)       # process result is pass
        self.assertEqual(result[0][4].split()[0], datetime.today().strftime('%Y-%m-%d'))

        ffx_cash_file = join(get_current_path(), 'samples', 'Reconciliation', 'FFX', 'Cash Stt _ 21082017.xlsx')
        ffx_holding_file = join(get_current_path(), 'samples', 'Reconciliation', 'FFX', 'Holding _ 21082017.xlsx')
        sample_txt_file = join(get_current_path(), 'samples', 'Reconciliation', 'FFX', 'sample.txt')
        files = [concord_holding_file, concord_cash_file, ffx_holding_file, ffx_cash_file, sample_txt_file]
        result_files = filter_files(files)
        self.assertEqual(len(result_files), 2)
        self.assertEqual(result_files[0], ffx_holding_file)
        self.assertEqual(result_files[1], ffx_cash_file)

        result = {
            'pass': [ffx_holding_file],
            'fail': [ffx_cash_file]
        }
        save_result(result)
        self.assertTrue(db_record_exists(ffx_holding_file))
        self.assertTrue(db_record_exists(ffx_cash_file))

        sql = '''SELECT * FROM process_result WHERE result=1'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 2)

        sql = '''SELECT * FROM process_result WHERE result=0'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 2)



def setup_test_db():
    """
    Create an in memory sqlite3 database. For testing only.
    """
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    sql = '''CREATE TABLE process_result \
                (id INTEGER PRIMARY KEY, \
                file_path VARCHAR(150), \
                hash CHAR(64), \
                result BOOLEAN, \
                time_stamp VARCHAR(25))'''
    c.execute(sql)

    return conn