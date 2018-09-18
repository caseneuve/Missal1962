# -*- coding: utf-8 -*-

"""
Rules for solving conflicts between liturgical days occurring at same date.

Each rule accepts the date for which calculations are being made (`datetime.date`), a list containing `LiturgicalDay`
representing this day's "tempora" and a list of `LiturgicalDay`s falling on given date.

Each rule returns a tuple consisting of three lists:
1. Celebration - main `LiturgicalDay` celebrated in given day
2. Commemoration - a list of `LiturgicalDay`s commemorated next to the main feast
3. Shift - a list of two-element tuples, each consisting of a `datetime.date` pointing to a day to which given
   `LiturgicalDay` should be moved and the `LiturgicalDay` itself.
"""

import datetime
from calendar import isleap

from .blocks import FEASTS_OF_JESUS_CLASS_1_AND_2, EMBER_DAYS
from .constants import SANCTI_12_08, SANCTI_01_13, SANCTI_12_24, TEMPORA_EPI1_0, SANCTI_11_02, SANCTI_02_24, \
    SANCTI_02_27, PATTERN_TEMPORA, PATTERN_TEMPORA_SUNDAY, PATTERN_SANCTI_CLASS_2, TEMPORA_QUADP3_3, TEMPORA_QUAD6_1, \
    TEMPORA_QUAD6_2, TEMPORA_QUAD6_3, TEMPORA_QUAD6_4, TEMPORA_QUAD6_5, TEMPORA_QUAD6_6, TEMPORA_PASC0_0, \
    PATTERN_ADVENT_FERIA_BETWEEN_17_AND_23, PATTERN_CLASS_1, PATTERN_TEMPORA_SUNDAY_CLASS_2, PATTERN_SANCTI_CLASS_1_OR_2
from . import match


def rule_immaculate_coneption(day, tempora, lit_days):
    # Immaculate Conception of BMV takes precedence before encountered Advent Sunday.
    if match(lit_days, SANCTI_12_08) and day.weekday() == 6:
        return [match(lit_days, SANCTI_12_08)], [], []


def rule_nativity(day, tempora, lit_days):
    # Nativity Vigil takes place of 4th Advent Sunday.
    if match(lit_days, SANCTI_12_24) and day.weekday() == 6:
        return [match(lit_days, SANCTI_12_24)], [], []


def rule_st_matthias(day, tempora, lit_days):
    # St. Matthias the Apostle, normally on Feb 24, but in leap year on Feb 25
    if match(lit_days, SANCTI_02_24) and isleap(day.year) and day.day == 24:
        return [match(lit_days, PATTERN_TEMPORA)], [], [[datetime.date(day.year, 2, 25), [match(lit_days, SANCTI_02_24)]]]


def rule_feb27(day, tempora, lit_days):
    # Feb 27, normally on Feb 27 but in leap year on Feb 28
    if match(lit_days, SANCTI_02_27) and isleap(day.year) and day.day == 27:
        return [match(lit_days, PATTERN_TEMPORA)], [], [[datetime.date(day.year, 2, 28), [match(lit_days, SANCTI_02_27)]]]


def rule_all_souls(day, tempora, lit_days):
    # All Souls Day; if not Sunday - Nov 2, else Nov 3
    if match(lit_days, SANCTI_11_02) and day.weekday() == 6:
        return [match(lit_days, PATTERN_TEMPORA_SUNDAY)], [], [[datetime.date(day.year, 11, 3), [match(lit_days, SANCTI_11_02)]]]


def rule_lord_feast1(day, tempora, lit_days):
    # A 1st class feast of the Lord occurring on a Sunday or Feria
    # takes the place of that day with all rights and privileges;
    # hence there is no commemoration of the day.
    if match(lit_days, SANCTI_01_13) and match(lit_days, TEMPORA_EPI1_0):
        return [match(lit_days, TEMPORA_EPI1_0)], [], []


def rule_lord_feast2(day, tempora, lit_days):
    if match(lit_days, FEASTS_OF_JESUS_CLASS_1_AND_2) and match(lit_days, PATTERN_TEMPORA_SUNDAY_CLASS_2):
        return [match(lit_days, PATTERN_SANCTI_CLASS_1_OR_2)], [], []


def first_class_feast_no_commemoration(day, tempora, lit_days):
    if match(lit_days, PATTERN_CLASS_1):
        return [match(lit_days, PATTERN_CLASS_1)], [], []


def rule_2nd_class_sunday(day, tempora, lit_days):
    # When 2nd class Sunday occurs along with 2nd class feast, the Sunday takes precedence and the feast is commemorated
    if match(lit_days, PATTERN_TEMPORA_SUNDAY_CLASS_2) and match(lit_days, PATTERN_SANCTI_CLASS_2):
        return [match(lit_days, PATTERN_TEMPORA_SUNDAY_CLASS_2)], [match(lit_days, PATTERN_SANCTI_CLASS_2)], []


def rule_1st_class_feria(day, tempora, lit_days):
    # Ash wednesday and holy week always wins
    if match(lit_days, [TEMPORA_QUAD6_1,
                        TEMPORA_QUAD6_2,
                        TEMPORA_QUAD6_3,
                        TEMPORA_QUAD6_4,
                        TEMPORA_QUAD6_5,
                        TEMPORA_QUAD6_6,
                        TEMPORA_PASC0_0,
                        TEMPORA_QUADP3_3]):
        return [match(lit_days, PATTERN_TEMPORA)], [], []


def rule_2nd_class_feast_takes_over_advent_feria_and_ember_days(day, tempora, lit_days):
    look_for = EMBER_DAYS + (PATTERN_ADVENT_FERIA_BETWEEN_17_AND_23, )
    if match(lit_days, look_for) and match(lit_days, PATTERN_SANCTI_CLASS_2):
        return [match(lit_days, PATTERN_SANCTI_CLASS_2)], [match(lit_days, look_for)], []


def rule_bmv_office_on_saturday(day, tempora, lit_days):
    pass


def rule_precedence(day, tempora, lit_days):
    if len(lit_days) == 0:
        return [], [], []
    elif len(lit_days) == 1:
        return lit_days, [], []
    else:
        first, second = sorted(lit_days, key=lambda x: (x.priority, x.rank, x.flexibility))[:2]
        if match([first], PATTERN_TEMPORA_SUNDAY) or (len(tempora) > 0 and second.id == tempora[0].id):
            return [first], [], []
        return [first], [second], []


rules = (
    rule_immaculate_coneption,
    rule_nativity,
    rule_st_matthias,
    rule_feb27,
    rule_all_souls,
    rule_lord_feast1,
    rule_lord_feast2,
    first_class_feast_no_commemoration,
    rule_2nd_class_sunday,
    rule_1st_class_feria,
    rule_2nd_class_feast_takes_over_advent_feria_and_ember_days,
    rule_bmv_office_on_saturday,
    rule_precedence
)
