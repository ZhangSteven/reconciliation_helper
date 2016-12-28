"""
Test the open_jpm.py
"""

import unittest2
import sqlite3
from datetime import datetime
from os.path import isfile, isdir, join
import shutil, os
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.recon_helper import search_files, convert, \
												filter_files
from reconciliation_helper.record import enable_test_mode, save_result, \
											get_db_connection, get_db_cursor



class TestRecords(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRecords, self).__init__(*args, **kwargs)
        conn = setup_test_db()
        enable_test_mode(conn)

    def setUp(self):
        """
            Run before a test function.
            Just clear contents in a testing database.
        """
        c = get_db_cursor()
        c.execute('DELETE FROM file_status')
        c.execute('DELETE FROM process_result')
        

    def tearDown(self):
        """
            Run after a test finishes
        """
        shutil.rmtree(get_base_dir())



    def setup_dir(self):
    	shutil.copytree(get_source_dir(), get_base_dir())
    	os.mkdir(get_output_dir())	# create the output dir



    def overwrite_file(self):
    	shutil.copy2(join(get_source_dir2(), 'Holding _ 20122016.xls'), \
        				join(get_base_dir(), 'Concord', 'Holding _ 20122016.xls'))



    def copy_more_files(self):
    	shutil.copytree(join(get_source_dir2(), 'DIF'), join(get_base_dir(), 'DIF'))



    def delete_files(self):
        shutil.rmtree(join(get_base_dir(), 'Concord'))
        os.remove(join(get_base_dir(), 'DIF', 'CL Franklin DIF 2016-12-15.xls'))



    def test_filter_files(self):
        self.setup_dir()
        files = search_files(get_base_dir(), get_output_dir())
        save_result(convert(files, get_output_dir()))

        self.overwrite_file()
        files = search_files(get_base_dir(), get_output_dir())

        for sub_folder in files:
            file_list = filter_files(files[sub_folder])
            if sub_folder == 'Concord':
            	self.assertEqual(len(file_list), 1)
            else:
            	self.assertEqual(len(file_list), 0)
        save_result(convert(files, get_output_dir()))

        self.copy_more_files()
        files = search_files(get_base_dir(), get_output_dir())
        for sub_folder in files:
            file_list = filter_files(files[sub_folder])
            if sub_folder == 'DIF':
                self.assertEqual(len(file_list), 2)
            else:
                self.assertEqual(len(file_list), 0)
        save_result(convert(files, get_output_dir()))

        self.delete_files()
        files = search_files(get_base_dir(), get_output_dir())
        for sub_folder in files:
            file_list = filter_files(files[sub_folder])
            self.assertEqual(len(file_list), 0)



    def test_result(self):
    	#
    	# copy some files to test
    	#
        self.setup_dir()
        files = search_files(get_base_dir(), get_output_dir())
        result = convert(files, get_output_dir())
        save_result(result)

        c = get_db_cursor()
        sql = '''SELECT * FROM file_status'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 4)

        sql = '''SELECT * FROM process_result'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 4)

        sql = '''SELECT * FROM file_status where status="fail"'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 1)
        # print(result[0])
        self.assertEqual(result[0][0], join(get_base_dir(), 'Concord', 'Holding _ 20122016.xls'))
        self.assertEqual(result[0][1], '2016-12-28 17:19:48')


        #
        # now overwrite one file with a newer file.
        #
        self.overwrite_file()
        files = search_files(get_base_dir(), get_output_dir())
        save_result(convert(files, get_output_dir()))

        c = get_db_cursor()
        sql = '''SELECT * FROM file_status'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 4)

        sql = '''SELECT * FROM file_status where status="fail"'''
        c.execute(sql)
        result = c.fetchall()
        self.assertEqual(len(result), 0)	# should have no fails

        # previously failed file now should be OK
        sql = '''SELECT * FROM file_status where file_fullpath="{0}"'''.\
        		format(join(get_base_dir(), 'Concord', 'Holding _ 20122016.xls'))
        c.execute(sql)
        result = c.fetchone()
        self.assertEqual(result[1], '2016-12-28 17:43:16')
        self.assertEqual(result[2], 'pass')

        sql = '''SELECT * FROM process_result'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 5)	# one more record added

        sql = '''SELECT * FROM process_result where file_fullpath="{0}" and m_time="{1}"'''.\
        		format(join(get_base_dir(), 'Concord', 'Holding _ 20122016.xls'), \
        				'2016-12-28 17:43:16')
        c.execute(sql)
        result = c.fetchone()
        # print(result)
        self.assertNotEqual(result, None)	# the record should exist


        #
        # some more files come in
        #
        self.copy_more_files()
        files = search_files(get_base_dir(), get_output_dir())
        save_result(convert(files, get_output_dir()))

        c = get_db_cursor()
        sql = '''SELECT * FROM file_status'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 6)

        sql = '''SELECT * FROM file_status where file_fullpath="{0}"'''.\
        		format(join(get_base_dir(), 'DIF', 'CL Franklin DIF 2016-12-12.xls'))
        c.execute(sql)
        result = c.fetchone()
        self.assertEqual(result[1], '2016-12-13 18:11:27')
        self.assertEqual(result[2], 'pass')

        sql = '''SELECT * FROM process_result'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 7)

        sql = '''SELECT m_time,result FROM process_result where file_fullpath="{0}"'''.\
        		format(join(get_base_dir(), 'DIF', 'CL Franklin DIF 2016-12-15.xls'))
        c.execute(sql)
        result = c.fetchall()
        # print(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '2016-12-16 18:22:51')
        self.assertEqual(result[0][1], 'pass')


        #
        # now delete some files
        #
        self.delete_files()
        files = search_files(get_base_dir(), get_output_dir())
        save_result(convert(files, get_output_dir()))

        c = get_db_cursor()
        sql = '''SELECT * FROM file_status'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 6)	# should have no change

        sql = '''SELECT * FROM file_status where file_fullpath="{0}"'''.\
        		format(join(get_base_dir(), 'Concord', 'Holding _ 20122016.xls'))
        c.execute(sql)
        result = c.fetchone()
        self.assertEqual(result[1], '2016-12-28 17:43:16')
        self.assertEqual(result[2], 'pass')

        sql = '''SELECT * FROM process_result'''
        c.execute(sql)
        self.assertEqual(len(c.fetchall()), 7)	# should have no change

        sql = '''SELECT m_time,result FROM process_result where file_fullpath="{0}"'''.\
        		format(join(get_base_dir(), 'DIF', 'CL Franklin DIF 2016-12-15.xls'))
        c.execute(sql)
        result = c.fetchall()
        # print(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '2016-12-16 18:22:51')
        self.assertEqual(result[0][1], 'pass')



def setup_test_db():
    """
    Create an in memory sqlite3 database. For testing only.
    """
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    sql = '''CREATE TABLE file_status \
                (file_fullpath TEXT PRIMARY KEY NOT NULL, \
                m_time TEXT NOT NULL, \
                status TEXT NOT NULL)'''
    c.execute(sql)

    sql = '''CREATE TABLE process_result \
                (id INTEGER PRIMARY KEY NOT NULL, \
                    file_fullpath TEXT NOT NULL, \
                    m_time TEXT NOT NULL, \
                    record_time TEXT NOT NULL, \
                    result TEXT NOT NULL)'''
    c.execute(sql)
    return conn



def get_base_dir():
	return r'C:\Users\steven.zhang\AppData\Local\Programs\Git\git\reconciliation_helper\samples\base_dir'



def get_source_dir():
	return r'C:\Users\STEVEN~1.ZHA\AppData\Local\Programs\Git\git\reconciliation_helper\samples\source'



def get_source_dir2():
	return r'C:\Users\STEVEN~1.ZHA\AppData\Local\Programs\Git\git\reconciliation_helper\samples\source2'



def get_output_dir():
	return join(get_base_dir(), 'result')