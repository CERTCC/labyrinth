#!/usr/bin/env python
"""
file: data_loader
author: adh
created_at: 8/25/21 9:33 AM
"""
#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import pandas as pd
from labyrinth.dir_helpers import yearly_summaries, monthly_summaries, daily_summaries


def load_years(results_dir):
    files = yearly_summaries(results_dir)
    return load_data(files)


def load_months(results_dir):
    files = monthly_summaries(results_dir)
    return load_data(files)


def load_days(results_dir):
    files = daily_summaries(results_dir)
    return load_data(files)


def load_data(json_files):
    df = pd.DataFrame()
    for f in json_files:
        _df = pd.read_json(f)
        df = df.append(_df)
    return df
