import csv
import os
import unittest
import unittest.mock

import convert


class OutbankDETestCase(unittest.TestCase):
    @unittest.mock.patch('sys.exit')
    def setUp(self, exit_mock):
        self.exit_mock = exit_mock
        convert.cmdline('outbank_de_test1.csv')
        self.data = list(csv.reader(open('outbank_de_test1-ynab.csv').read().split('\n'), delimiter=','))

    def tearDown(self):
        if os.path.isfile('outbank_de_test1-ynab.csv'):
            os.remove('outbank_de_test1-ynab.csv')

    def test_ynab_format(self):
        self.assertListEqual(self.data[0], ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])

    def test_sepa(self):
        # Sepa transaction pos. value
        self.assertListEqual(self.data[1], ['02/05/2016', 'Sender mit Ümläut +- Sønderzeichen', '',
                                            'SEPA Gutschrift 166/000 Kømmentar des Senders', '', '1234.56'])

    def test_bank_internal(self):
        # Bank internal transaction - has no sender m( - with negavite value
        self.assertListEqual(self.data[2], ['01/05/2016', '', '', 'Aktion ohne Aktor 806/000', '100.00', ''])

    def test_international_CC(self):
        # international credit card transaction with negative value
        # We're not doing anything with the additional data yet
        self.assertListEqual(self.data[3], ['04/05/2016', 'Gringold Services Inc.', '',
                                            'Belastung Gringold Services Inc. gringold.muggle  USA VK-Betrag: 1.62 USD Kurs: 1.1611003 Auslandseinsatzentgelt Faktor: 1.75% Auslandseinsatzentgelt Wert: 0.02',
                                            '1.40', ''])


class FailureTestCase(unittest.TestCase):
    @unittest.mock.patch('sys.exit')
    def test_outbank_defect_header(self, exit_mock):
        convert.cmdline('outbank_de_defect_1.csv')
        exit_mock.assert_called_with(110)


if __name__ == '__main__':
    unittest.main()
