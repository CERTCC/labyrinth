#!/usr/bin/env python
"""
file: rate_limit_helpers
author: adh
created_at: 8/12/21 12:54 PM
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
import time
import random
import logging

logger = logging.getLogger(__name__)

NAP_LIMIT = 50

rl_timers = {
    "core": 3600,
    "search": 60,
    "graphql": 3600,
}


def _rl_pause(rlkey, rl, threshold=10):
    """
    If you are too close to a rate limit threshold, take a nap.
    Otherwise just return and go about your day.
    """
    remaining = rl.remaining
    if remaining < (5 * threshold):
        logger.info(f"Rate limit {rlkey} has {remaining} remaining")

    if remaining > threshold:
        return

    # how long to wait?
    nap_delta = rl.reset - datetime.datetime.utcnow()
    # nap_delta is a timedelta object
    # .total_seconds() is what you want, beware of .seconds()!!!
    nap_seconds = nap_delta.total_seconds()

    if nap_seconds > 0:
        # it's positive, rl.reset is still in the future
        # but we don't want to go too big
        nap_seconds = min(nap_seconds, rl_timers[rlkey])
    else:
        # it's negative, and rl.reset is already in the past
        # still might be a little out of sync though so
        # take a short nap
        nap_seconds = 1

    # add some jitter up to a minute
    nap_seconds += random.random() * min(60, nap_seconds / 2)

    logger.info(
        f"Pausing for {nap_seconds:.1f} to wait for {rlkey} rate limit to catch up ({remaining})"
    )
    time.sleep(nap_seconds)
    return True


def check_rate_limits(gh, nap_count=0):
    if nap_count > NAP_LIMIT:
        raise RuntimeError("Too many naps. Try again when things aren't so busy.")

    limits = {
        "core": gh.get_rate_limit().core,
        "search": gh.get_rate_limit().search,
        "graphql": gh.get_rate_limit().graphql,
    }

    thresh = {"core": 100, "graphql": 100, "search": 5}

    for key, rl in limits.items():
        napped = _rl_pause(key, rl, threshold=thresh[key])
        if napped:
            nap_count += 1
            # we don't know what happened while we were asleep
            return check_rate_limits(gh, nap_count)


def check_rl_core(gh, nap_count=0):
    if nap_count > NAP_LIMIT:
        raise RuntimeError("Too many naps. Try again when things aren't so busy.")

    rl = gh.get_rate_limit().core
    napped = _rl_pause("core", rl, threshold=100)
    if napped:
        nap_count += 1
        return check_rl_core(gh, nap_count)
