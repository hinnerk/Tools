import unittest
from decimal import Decimal

import convert

# format: list of pairs, each pair consists of [raw, expected].
# It's a global var, because even without any superfluous indention it's barely readable.
TEST_DATA = [
    # Header
    [(u"Nummer;Buchungsdatum;Valutadatum;Waehrung;Betrag"
      u";Empfaengername;IBAN;BIC;Gläubiger ID;Mandatsreferenz;"
      u"Absender ID;SEPA-Referenz;Bankleitzahl;Kontonummer;"
      u"Referenz;Textschluessel;Kategorie;Kommentar;"
      u"Verwendungszweck_1;Verwendungszweck_2;Verwendungszweck_3;Verwendungszweck_4;Verwendungszweck_5;"
      u"Verwendungszweck_6;Verwendungszweck_7;Verwendungszweck_8;Verwendungszweck_9;Verwendungszweck_10;"
      u"Verwendungszweck_11;Verwendungszweck_12;Verwendungszweck_13;Verwendungszweck_14"),

     ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']],

    # Sepa transaction pos. value
    [(u'1;02.05.2016;02.05.2016;EUR;"1234,56";Sender mit Ümläut +- Sønderzeichen;'
      u'DE12345678901234567890;BICBICBICBI;;;;;;;SEPA Gutschrift;166/000;;;'
      u'Kømmentar des Senders'),

     ['02/05/2016', 'Sender mit Ümläut +- Sønderzeichen', None,
      'SEPA Gutschrift 166/000 Kømmentar des Senders', None,
      Decimal('1234.56')]],

    # Bank internal transaction - has no sender m( - with negavite value
    [(u'2;29.04.2016;01.05.2016;EUR;"-100,00";;;;;;;;;;'
      u'Aktion ohne Aktor;806/000;;;'),

     ['01/05/2016', None, None, 'Aktion ohne Aktor 806/000', Decimal('100.00'), None]],

    # international credit card transaction with negative value
    # We're not doing anything with the additional data yet
    [
        (u'9;03.05.2016;04.05.2016;EUR;"-1.40";;;;;;;;;;Belastung;;;;'
         u'Gringold Services Inc. ;gringold.muggle  USA ;VK-Betrag: 1.62 USD ;'
         u'Kurs: 1.1611003 ;Auslandseinsatzentgelt Faktor: 1.75% ;'
         u'Auslandseinsatzentgelt Wert: 0.02'),

        ['04/05/2016', 'Gringold Services Inc.', None,
         ('Belastung Gringold Services Inc. gringold.muggle  '
          'USA VK-Betrag: 1.62 USD Kurs: 1.1611003 '
          'Auslandseinsatzentgelt Faktor: 1.75% '
          'Auslandseinsatzentgelt Wert: 0.02'),
         Decimal('1.40'), None]
    ],
]


class GenericTestCase(unittest.TestCase):
    def test_outbank_success(self):
        src_data = '\n'.join(x[0] for x in TEST_DATA)
        expected = [x[1] for x in TEST_DATA]
        result = convert.convert(src_data)
        self.assertEqual(len(result), len(expected))
        for expected_row, result_row in zip(expected, result):
            self.assertEqual(result_row, expected_row)

    def test_outbank_defect_header(self):
        defects = [
            TEST_DATA[0][0][:-2],   # just one char missing
            "X" * 100               # total nonsense
        ]
        for raw_data in defects:
            with self.assertRaises(convert.ConverterNotFound):
                convert.convert(raw_data)
