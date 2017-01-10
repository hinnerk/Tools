#!/usr/bin/env python3.5
# coding=utf-8

"""
Converts »Outbank« style CSV to »YNAB« style CSV.
"""

import csv
import decimal
import os
import sys


class Error(Exception):
    pass


class UnknownCSVFormat(Error):
    pass


class ConverterNotFound(Error):
    pass


def parse_single_european_money_value(value):
    value = string_to_decimal(value)
    outflow = abs(value) if value.is_signed() else None
    inflow = value if outflow is None else None
    return outflow, inflow


def string_to_decimal(string):
    if '.' in string and ',' in string:
        if string.index(',') > string.index('.'):
            # German: '2.700,12'
            string = string.replace('.', '')
        else:
            # American: '2,700.12'
            string = string.replace(',', '')
    if ',' in string:
        string = string.replace(',', '.')
    return decimal.Decimal(string)


def reformat_euro_date(whatever):
    assert len(whatever) == 10
    day, month, year = whatever.split('.')
    return '/'.join([day, month, year])


def make_entry(data, date=None, payee=None, category=None, memo=None, outflow=None, inflow=None):
    """
    data: a dict containing raw raw_data
    everything else: string or list
    """
    return [
        _get_single(data, date),
        _get_single(data, payee),
        _get_single(data, category),
        _get_multi(data, memo),
        _get_single(data, outflow),
        _get_single(data, inflow)
    ]


def _get_single(data, keys):
    """
    Returns the first available truthy value yielded by key from data.
    :param data:
    :param keys:
    :return:
    """
    if keys is None:
        return None
    assert isinstance(keys, (list, tuple, str))
    if isinstance(keys, str):
        return data.get(keys)
    for key in keys:
        if data.get(key):
            return data.get(key).strip()
    return None


def _get_multi(data, keys):
    if keys is None:
        return None
    assert isinstance(keys, (list, tuple, str))
    if isinstance(keys, str):
        return data.get(keys, False)
    results = (data.get(key) for key in keys)
    return ' '.join(x.strip() for x in results if x)


def outbank_detect(data):
    test_line = (u"Nummer;Buchungsdatum;Valutadatum;Waehrung;Betrag"
                 u";Empfaengername;IBAN;BIC;Gläubiger ID;Mandatsreferenz;"
                 u"Absender ID;SEPA-Referenz;Bankleitzahl;Kontonummer;"
                 u"Referenz;Textschluessel;Kategorie;Kommentar;"
                 u"Verwendungszweck_1;Verwendungszweck_2;"
                 u"Verwendungszweck_3;Verwendungszweck_4;Verwendungszweck_5;"
                 u"Verwendungszweck_6;Verwendungszweck_7;Verwendungszweck_8;"
                 u"Verwendungszweck_9;Verwendungszweck_10;"
                 u"Verwendungszweck_11;Verwendungszweck_12;"
                 u"Verwendungszweck_13;Verwendungszweck_14")
    return data.split('\n')[0] == test_line


def outbank_convert(data):
    result = [['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']]
    data = csv.DictReader(data.split('\n'), delimiter=';')
    for row in data:
        assert row.get('Waehrung') == 'EUR'
        entry = make_entry(
            row,
            date=['Valutadatum', 'Buchungsdatum'],
            payee=['Empfaengername', 'Verwendungszweck_1'],
            category=None,
            memo=['Referenz', 'SEPA-Referenz', 'Textschluessel', 'Verwendungszweck_1', 'Verwendungszweck_2',
                  'Verwendungszweck_3',
                  'Verwendungszweck_4', 'Verwendungszweck_5',
                  'Verwendungszweck_6', 'Verwendungszweck_7', 'Verwendungszweck_8', 'Verwendungszweck_9',
                  'Verwendungszweck_10', 'Verwendungszweck_11', 'Verwendungszweck_12', 'Verwendungszweck_13',
                  'Verwendungszweck_14'],
            outflow=None,
            inflow=None
        )
        entry[0] = reformat_euro_date(entry[0])
        entry[4], entry[5] = parse_single_european_money_value(row.get('Betrag'))
        result.append(entry)
    return result


# TODO: more converters
# TODO: add M&M converter
DETECTORS = [
    [outbank_detect, outbank_convert]
]


def get_converter(data):
    for detector, converter in DETECTORS:
        if detector(data):
            return converter


def convert(data):
    converter = get_converter(data)
    if not converter:
        raise ConverterNotFound
    return converter(data)


def write_result(result, result_file):
    writer = csv.writer(result_file, delimiter=',')
    # , quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in result:
        writer.writerow(row)


def convert_unicode(data):
    if b'\0' in data:
        return data.decode('utf-16')
    return data.decode('utf-8')


def cmdline():
    source = sys.argv[1]
    target = source[:-4] if source.lower().endswith('.csv') else source
    target += '-ynab.csv'
    try:
        raw_data = open(source, 'rb').read()
        raw_data = convert_unicode(raw_data)
        raw_data = raw_data.strip()
        converted_data = convert(raw_data)
        if not os.path.isfile(target):
            with open(target, 'w', newline='') as result_file:
                write_result(converted_data, result_file)
        else:
            print('File "{}" exists, exiting w/o doing anything.'.format(target))
            sys.exit(23)
    except FileNotFoundError:
        print('No such file: "{}"'.format(source))
        sys.exit(42)
    except ConverterNotFound:
        print('File type detection failed :(')
        sys.exit(110)
    else:
        sys.exit(0)

def ios_clip():
    # TODO: does not work because implicit unicode conversions    
    raw_data = clipboard.get()
    data = convert_unicode(raw_data).strip()
    clipboard.set(convert(data))
    
    
if __name__ == '__main__':
    cmdline()
