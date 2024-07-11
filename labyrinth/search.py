#!/usr/bin/env python
"""
file: search
author: adh
created_at: 8/12/21 3:28 PM
"""
#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import datetime

import pandas as pd
from github import Github
from github.GithubException import RateLimitExceededException
import random
import time

import labyrinth
from labyrinth.date_helpers import fixup_start_date, fixup_end_date
from labyrinth.rate_limit_helpers import check_rate_limits


def main():
    pass


if __name__ == "__main__":
    main()

class RateLimitedIterator:
    def __init__(self, paginated_list, github_client):
        self.paginated_list = iter(paginated_list)
        self.gh = github_client

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                return next(self.paginated_list)
            except RateLimitExceededException as e:
                print("Rate limit exceeded, handling...")
                # Handle the rate limit (e.g., sleep, log, check rate limits)
                time.sleep(random.randint(10, 30))  # Example: sleep for a random time
                check_rate_limits(self.gh)  # Check and handle rate limits
                # The loop will retry fetching the next item after handling the rate limit

def do_search(query, start_date=None, end_date=None, page_size=100):

    start_date = fixup_start_date(start_date)
    end_date = fixup_end_date(end_date)
    # these will be y-m-d strings

    start_dates = pd.date_range(start_date, end_date, freq="7D", tz="utc")
    end_dates = [d + pd.DateOffset(days=6) for d in start_dates]

    end_date_ts = pd.to_datetime(end_date, utc=True)
    if end_dates[-1] > end_date_ts:
        # we overshot end date, so fix that
        end_dates[-1] = end_date_ts

    # convert the timestamps back to our formatted date strings
    fmt_dates = lambda ts_iter: [d.strftime("%Y-%m-%d") for d in ts_iter]
    start_dates = fmt_dates(start_dates)
    end_dates = fmt_dates(end_dates)

    quals = [{"pushed": f"{d1}..{d2}"} for d1, d2 in zip(start_dates, end_dates)]

    print(f"Starting {len(quals)} queries", flush=True)

    if page_size > 100:
        raise ValueError("Github requires page_size <= 100")
    gh = Github(login_or_token=labyrinth.GH_TOKEN, per_page=page_size, retry=2)

    results = []
    for qualifiers in quals:
        check_rate_limits(gh)
        quals = " ".join(f"{k}:{v}" for k, v in qualifiers.items())
        qstr = f"{query} {quals}"

        print(f"Search: {qstr}", flush=True)

        result = gh.search_repositories(
            query, sort="updated", order="asc", **qualifiers
        )

        # result is a generator of repository objects
        count = 0

        result_iterator = RateLimitedIterator(result, gh)
        for r in result_iterator:
            # timestamp
            ts = (
                datetime.datetime.utcnow()
                .replace(microsecond=0)
                .astimezone(datetime.timezone.utc)
                .isoformat()
            )

            data = r.raw_data

            data["matched_on"] = qstr
            data["matched_at"] = ts
            results.append(data)
            count += 1

        print(f"Found {count} results for {qstr}", flush=True)

    return results
