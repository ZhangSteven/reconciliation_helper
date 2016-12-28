"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import join
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.recon_helper import search_files, convert
from reconciliation_helper.record import enable_test_mode, save_result
from reconciliation_helper.test.test_record import setup_test_db



class TestRecon(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRecon, self).__init__(*args, **kwargs)
        conn = setup_test_db()
        enable_test_mode(conn)



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



    def test_search_file(self):
        """
        Use samples\base_dir1 to test.
        """
        base_dir = join(get_current_path(), 'samples', 'base_dir1')
        output_dir = join(get_current_path(), 'samples', 'base_dir1', 'result')
        files = search_files(base_dir, output_dir)
        self.assertTrue(self.verify_sub_folders(list(files.keys())))

        # sub folders under Concord is not counted, only files
        self.assertEqual(len(files['Concord']), 5)
        self.assertEqual(len(files['ListCo Equity']), 1)
        self.assertEqual(len(files['CLO Equity']), 2)
        self.assertEqual(files['ListCo Equity'][0], join(base_dir, 'ListCo Equity', 'Positions1219.xlsx'))



    def test_convert_jpm(self):
        files = {'ListCo Equity': [join(get_current_path(), 'samples', 'base_dir1', 'ListCo Equity', 'Positions1219.xlsx'), \
                                    join(get_current_path(), 'samples', 'base_dir1', 'CLO Equity', 'positions - 20161130.xls'), \
                                    join(get_current_path(), 'samples', 'base_dir1', 'CLO Equity', 'JP Morgan Broker Statement 2016-07-06.xls')]}
        output_dir = join(get_current_path(), 'samples', 'base_dir1', 'result')
        result = convert(files, output_dir)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result['fail']), 0)
        self.assertEqual(len(result['pass']), 3)
        self.assertEqual(result['pass'][0], files['ListCo Equity'][0])
        self.assertEqual(result['pass'][1], files['ListCo Equity'][1])
        self.assertEqual(result['pass'][2], files['ListCo Equity'][2])



    def test_convert_bochk(self):
        files = {'Concord': \
                    [join(get_current_path(), 'samples', 'base_dir1', 'Concord', 'Holding _ 19122016.xls'), \
                        join(get_current_path(), 'samples', 'base_dir1', 'Concord', 'Cash Stt _ 19122016.xls'), \
                        join(get_current_path(), 'samples', 'base_dir1', 'Concord', 'Cash Stt _ 13122016.xls'), \
                        join(get_current_path(), 'samples', 'base_dir1', 'Concord', 'sample.txt'), \
                        join(get_current_path(), 'samples', 'base_dir1', 'Concord', 'Holding _ 20122016.xls')]}
        
        output_dir = join(get_current_path(), 'samples', 'base_dir1', 'result')
        result = convert(files, output_dir)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result['pass']), 3)
        self.assertEqual(len(result['fail']), 1)
        self.assertEqual(result['pass'][0], files['Concord'][0])
        self.assertEqual(result['pass'][1], files['Concord'][1])
        self.assertEqual(result['pass'][2], files['Concord'][2])
        self.assertEqual(result['fail'][0], files['Concord'][4])
        save_result(result)



    def test_convert_trustee(self):
        files = {'DIF': \
                    [join(get_current_path(), 'samples', 'base_dir2', 'DIF', 'CL Franklin DIF 2016-12-12.xls'), \
                        join(get_current_path(), 'samples', 'base_dir2', 'DIF', 'CL Franklin DIF 2016-12-15.xls')]}
        output_dir = join(get_current_path(), 'samples', 'base_dir2', 'result')
        result = convert(files, output_dir)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result['fail']), 0)
        self.assertEqual(len(result['pass']), 2)
        self.assertEqual(result['pass'][0], files['DIF'][0])
        self.assertEqual(result['pass'][1], files['DIF'][1])
        save_result(result)
        


    def verify_sub_folders(self, sub_folders):
        self.assertEqual(len(sub_folders), 3)
        if sub_folders[0] == 'Concord' and sub_folders[1] == 'ListCo Equity' and sub_folders[2] == 'CLO Equity':
            return True

        if sub_folders[0] == 'Concord' and sub_folders[1] == 'CLO Equity' and sub_folders[2] == 'ListCo Equity':
            return True

        if sub_folders[0] == 'ListCo Equity' and sub_folders[1] == 'Concord' and sub_folders[2] == 'CLO Equity':
            return True

        if sub_folders[0] == 'ListCo Equity' and sub_folders[1] == 'CLO Equity' and sub_folders[2] == 'Concord':
            return True

        if sub_folders[0] == 'CLO Equity' and sub_folders[1] == 'Concord' and sub_folders[2] == 'ListCo Equity':
            return True

        if sub_folders[0] == 'CLO Equity' and sub_folders[1] == 'ListCo Equity' and sub_folders[2] == 'Concord':
            return True


        return False