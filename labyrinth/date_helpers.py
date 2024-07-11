#!/usr/bin/env python
"""
file: date_helpers
author: adh
created_at: 8/12/21 12:48 PM
"""
#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import re
from datetime import date, timedelta
import argparse
import calendar

import pandas as pd
from pandas._libs.tslibs.offsets import YearBegin, YearEnd, MonthBegin, MonthEnd


year_pat = re.compile("^\d{4}$")
month_pat = re.compile("^\d{4}-\d{2}$")
day_pat = re.compile("^\d{4}-\d{2}-\d{2}$")

year_begin = lambda x: _year_begin(pd.to_datetime(x).strftime("%Y-%m-%d"))
year_end = lambda x: _year_end(pd.to_datetime(x).strftime("%Y-%m-%d"))
month_begin = lambda x: _month_begin(pd.to_datetime(x).strftime("%Y-%m-%d"))
month_end = lambda x: _month_end(pd.to_datetime(x).strftime("%Y-%m-%d"))


def _year_end(dt):
    m = re.match("(\d{4})", dt)
    if m:
        return f"{m.groups()[0]}-12-31"


def _year_begin(dt):
    m = re.match("(\d{4})", dt)
    if m:
        return f"{m.groups()[0]}-01-01"


def _month_end(dt):
    m = re.match("(\d{4})-(\d{2})", dt)
    if m:
        y = int(m.groups()[0])
        m = int(m.groups()[1])
        # monthrange returns weekday , last day of month
        d = calendar.monthrange(y, m)[1]
        return f"{y:04d}-{m:02d}-{d:02d}"


def _month_begin(dt):
    m = re.match("(\d{4})-(\d{2})", dt)
    if m:
        return f"{m.groups()[0]}-{m.groups()[1]}-01"


def fixup_end_date(end_date=None):
    if end_date is None:
        return date.today().strftime("%Y-%m-%d")

    if year_pat.match(end_date):
        return year_end(end_date)

    if month_pat.match(end_date):
        return month_end(end_date)

    return end_date


def fixup_start_date(start_date=None):
    if start_date is None:
        yesterday = date.today() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

    if year_pat.match(start_date):
        return year_begin(start_date)

    if month_pat.match(start_date):
        return month_begin(start_date)

    return start_date


def year_type(arg_value, pat=year_pat):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


def month_type(arg_value, pat=month_pat):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


def day_type(arg_value, pat=day_pat):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value
