#!/usr/bin/env python
"""
file: config
author: adh
created_at: 9/14/21 2:03 PM
"""
#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import os

DEBUG = False
VERBOSE = False
GH_TOKEN = os.getenv("GH_TOKEN")  # will be None if unset

SEARCH_RESULTS_HOME = "results"
FILE_RESULTS_HOME = "data"
VUL_ID_RESULTS_HOME = os.path.join(FILE_RESULTS_HOME, "vul_id")
REPO_ID_RESULTS_HOME = os.path.join(FILE_RESULTS_HOME, "repo_id")
