"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import join
from reconciliation_helper.utility import get_current_path
from reconciliation_helper.trustee import is_bochk_cash_file, update_cash_entries
from bochk.open_bochk import read_cash_bochk



class TestTrustee(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTrustee, self).__init__(*args, **kwargs)

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



    def test_is_bochk_cash_file(self):
        file1 = join(get_current_path(), 'samples', 'BOC Bank Statement 2012-06-30 (OVERSEAS (CAPITAL) SUB FUND BOND)-HKD.xls')
        file2 = join(get_current_path(), 'samples', 'BOC Bank Statement 2016-11-30 (CLASS A-HK SUB FUND I) -HKD.xls')
        self.assertFalse(is_bochk_cash_file(file1))
        self.assertTrue(is_bochk_cash_file(file2))



    def test_update_cash_entries(self):
        file1 = join(get_current_path(), 'samples', 'BOC Bank Statement 2016-11-30 (CLASS A-HK SUB FUND I) -HKD.xls')
        file2 = join(get_current_path(), 'samples', 'BOC Bank Statement 2016-12-13 (CLASS A-HK SUB FUND I) (HKD).xls')
        file3 = join(get_current_path(), 'samples', 'BOC Bank Statement 2016-12-15 (CLASS A-HK SUB FUND I) (USD).xls')
        file4 = join(get_current_path(), 'samples', 'BOC Bank Statement 2013-12-31 (CLASS A-HK) -HKD.xls')
        cash_entries = []

        file_list = [file1, file2, file3, file4]
        cash_entries = []
        for filename in file_list:
            port_values = {}
            read_cash_bochk(filename, port_values)
            update_cash_entries(port_values, cash_entries)

        self.assertTrue(len(cash_entries), 3)
        matched = 0
        for cash_entry in cash_entries:
            if cash_entry['Account Name'] == 'CLT-CLI HK BR (CLASS A- HK) TRUST FUND - SUB FUND I' \
                and cash_entry['Currency'] == 'HKD':
                self.verify_cash1(cash_entry)
                matched = matched + 1
            elif cash_entry['Account Name'] == 'CLT-CLI HK BR (CLASS A- HK) TRUST FUND - SUB FUND I' \
                and cash_entry['Currency'] == 'USD':
                self.verify_cash2(cash_entry)
                matched = matched + 1
            elif cash_entry['Account Name'] == 'CLT-CLI HK BR (CLASS A- HK) TRUST FUND' \
                and cash_entry['Currency'] == 'HKD':
                self.verify_cash3(cash_entry)
                matched = matched + 1

        self.assertEqual(matched, 3)



    def verify_cash1(self, cash_entry):
        """
        for BOC Bank Statement 2016-12-13 (CLASS A-HK SUB FUND I) (HKD)
        """
        self.assertAlmostEqual(cash_entry['Current Ledger Balance'], 794861956.69)
        self.assertAlmostEqual(cash_entry['Ledger Balance'], 794861956.69)



    def verify_cash2(self, cash_entry):
        """
        for BOC Bank Statement 2016-12-15 (CLASS A-HK SUB FUND I) (USD)
        """
        self.assertAlmostEqual(cash_entry['Current Ledger Balance'], 9840155.96)
        self.assertAlmostEqual(cash_entry['Ledger Balance'], 8625250.58)



    def verify_cash3(self, cash_entry):
        """
        for BOC Bank Statement 2013-12-31 (CLASS A-HK) -HKD
        """
        self.assertAlmostEqual(cash_entry['Current Ledger Balance'], 292.95)
        self.assertAlmostEqual(cash_entry['Ledger Balance'], 62.95)