#!/usr/bin/env python3
# coding=utf-8

import unittest
from decimal import Decimal as D

import sys


# TODO: Partnerabo (Monatl. kündbar, 3 Mon. Mindestlaufzeit, 2 Personen, 1 Konto) 85,00€


class Base:
    title = ''
    visits = []
    monthly = []
    value = None
    constraints = None

    def __init__(self, visits_per_month):
        # a list of integers describing visits per month
        assert (isinstance(visits_per_month, list))
        # max 12 months yet
        assert (len(visits_per_month) <= 12)
        self.visits = [D(x) for x in visits_per_month]
        self.monthly = self.calculate()

    @property
    def total(self):
        return sum(self.monthly)

    @property
    def average(self):
        return self.total / sum(self.visits)

    def details(self):
        result = ''
        count = 0
        for m in self.visits:
            result += '{:2d}. Monat: {:2d} Besuche, {:3.2f} €\n'.format(count + 1, int(m), self.monthly[count])
            count += 1
        result += '\nTotal: {s.total:3.2f}€\nDurchschnitt {s.average:3.2f} € pro Karte.\n'.format(s=self)
        return result

    def __repr__(self):
        return self.title + ', Gesamt: ' + str(self.total) + '€'

    def calculate(self):
        raise NotImplemented


class Elf(Base):
    title = '11er Karte'

    def calculate(self):
        card = D(11)
        card_value = D(105)
        monthly = []
        cards = D(0)
        payments_total = D(0)
        for month in self.visits:
            payments_monthly = D(0)
            while cards < month:
                cards += card
                payments_total += 1
                payments_monthly += 1
            cards -= month
            monthly.append(payments_monthly * card_value)
        return monthly


class TageskarteTestCase(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(Tageskarte([0]).monthly, [0])

    def test_double(self):
        self.assertEqual(Tageskarte([1, 4]).monthly, [D('10.5'), D(42)])


class Tageskarte(Base):
    title = 'Tageskarte'
    preis = D('10.5')

    def calculate(self):
        return [x * self.preis for x in self.visits]


class Abendkarte(Tageskarte):
    title = 'Abendkarte'
    preis = D('5.5')
    description = 'Abendkarte (Mo bis Fr ab 21:00 Uhr, nicht an Feiertagen) für 5,50€'
    constraints = 'Mo bis Fr ab 21:00 Uhr, nicht an Feiertagen'


class HappyDayKarte(Tageskarte):
    title = 'Happy Day Karte'
    description = 'Happy Day Karten (gültig Mo bis Fr bei Eintritt bis 15:00 Uhr, nicht an Feiertagen) für € 7,50'
    preis = D('7.5')
    constraints = 'Mo bis Fr bei Eintritt bis 15:00 Uhr, nicht an Feiertagen'


class TageskarteMitgliederTestCase(unittest.TestCase):
    def test_ein_tag(self):
        self.assertEqual(TageskarteMitglied([1]).monthly, [D('105.5')])

    def test_zwei_monate(self):
        self.assertEqual(TageskarteMitglied([3, 7]).monthly, [D('116.5'), D('38.5')])

    def test_null(self):
        self.assertEqual(TageskarteMitglied([0]).monthly, [100])


class TageskarteMitglied(Base):
    title = 'Tageskarte Mitglied'
    preis_einmalig = D(100)
    preis_karte = D('5.5')
    description = 'Mitgliedskarte (1 Jahr vergünstigter Eintritt) 100,00€\nBouldertageskarte für Mitglieder: 5,50€'

    def calculate(self):
        result = [x * self.preis_karte for x in self.visits]
        result[0] += self.preis_einmalig
        return result


class AbendkarteMitglied(TageskarteMitglied):
    title = 'Abendkarte Mitglied'
    description = 'Abendkarte (Mo bis Fr ab 21:00 Uhr, nicht an Feiertagen) für Mitglieder 3,50€'
    preis_karte = D('3.5')
    constraints = 'Mo bis Fr ab 21:00 Uhr, nicht an Feiertagen'


class HappyDayMitglied(TageskarteMitglied):
    title = 'Happy Day Mitglieder'
    description = 'Happy Day Karten (gültig Mo bis Fr bei Eintritt bis 15:00 Uhr, nicht an Feiertagen) für Mitglieder ' \
                  '4,50€ '
    preis_karte = D('4.5')
    constraints = 'Mo bis Fr bei Eintritt bis 15:00 Uhr, nicht an Feiertagen'


class MonatsaboTestCase(unittest.TestCase):
    def test_null(self):
        self.assertEqual(Monatsabo([0]).monthly, [117])

    def test_drei_monate(self):
        self.assertEqual(Monatsabo([1, 0, 17]).monthly, [39, 39, 39])

    def test_zwei_monate(self):
        self.assertEqual(Monatsabo([1, 17]).monthly, [39, 78])

    def test_ein_monat(self):
        self.assertEqual(Monatsabo([23]).monthly, [117])


class Monatsabo(Base):
    title = 'Monatsabo'
    description = 'Boulderabo (Monatl. kündbar, 3 Mon. Mindestlaufzeit) 39,00€'
    preis = D(39)

    def calculate(self):
        if len(self.visits) == 1:
            return [self.preis * 3]
        if len(self.visits) == 2:
            return [self.preis, self.preis * 2]
        return [self.preis for x in self.visits]


class JahreskarteTestCase(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(Jahreskarte([0]).monthly, [0])

    def test_sechs_monate(self):
        self.assertEqual(Jahreskarte([1, 0, 0, 0, 23, 0]).monthly, [380, 0, 0, 0, 0, 0])


class Jahreskarte(Base):
    title = 'Jahreskarte'
    description = 'Jahreskarte Bouldern 380,00€'
    preis = D(380)

    def calculate(self):
        if sum(self.visits) == 0:
            return [D(0) for x in self.visits]
        return [self.preis] + [0] * (len(self.visits) - 1)


def compare():
    results = [c(sys.argv[1:]) for c in [Elf, Tageskarte, TageskarteMitglied, Abendkarte,
                                         AbendkarteMitglied, HappyDayKarte, HappyDayMitglied, Monatsabo, Jahreskarte]]
    results.sort(key=lambda x: x.total)
    text = 'Ergebnis für {} Besuche:\n'.format(sum(results[0].visits))
    text_len = max([len(x.title) for x in results])
    format_string = '{r.title:' + '{}'.format(text_len) + '}: {r.total:3.2f} €\n'
    for result in results:
        text += format_string.format(r=result)
    text += '\n'
    unconstrained = [x for x in results if not x.constraints]
    text += 'Preiswertestes Vollangebot: {}\n\n{}'.format(unconstrained[0].title, unconstrained[0].details())
    return text


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Jemand müßte mal eine Anleitung schreiben...')
    elif sys.argv[1].lower() == 'test':
        print('Running unit tests...')
        unittest.main()
    else:
        print(compare())
