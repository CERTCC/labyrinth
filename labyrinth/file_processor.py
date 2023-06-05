#!/usr/bin/env python
"""
file: file_processor
author: adh
created_at: 8/24/21 11:15 AM
"""
import hashlib
import os
import pandas as pd

from labyrinth.patterns import find_vul_ids
from labyrinth.ignorelist import IGNORE_FILE_EXTS, IGNORE_DIRS

import logging

logger = logging.getLogger(__name__)


def process_file(fpath, workdir="/"):
    relpath = os.path.relpath(fpath, start=workdir)
    logger.debug(f"Processing {relpath}")

    df = pd.DataFrame()
    if not os.path.isfile(fpath):
        return df

    try:
        with open(fpath, "r", encoding="ISO-8859-1") as fp:

            # start with the path to find matches
            filematches = find_vul_ids(relpath)

            # look in the file for more
            for line in fp.readlines():
                linematches = find_vul_ids(line.strip())
                filematches.extend(linematches)
            # unique them
            filematches = list(set(filematches))

            if len(filematches):
                logger.debug(f"File {relpath} matched on {', '.join(filematches)}")
                df["match"] = filematches
                df["file"] = relpath

                file_sha1 = _file_sha1(fpath)
                df["file_sha1"] = file_sha1

                df = df.sort_values(by="match").reset_index(drop=True)

    except UnicodeDecodeError as e:
        logger.warning(f"Skipping file {relpath} because of UnicodeDecodeError: {e}")

    return df


def _file_sha1(fpath):
    # get the file sha1
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()
    with open(fpath, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    file_sha1 = sha1.hexdigest()
    return file_sha1


def _filename_accept(f):
    # forget about .gitignore etc
    if f.startswith(".git"):
        return False

    for ext in IGNORE_FILE_EXTS:
        if f.endswith(ext):
            return False

    return True


def process_dir(path, workdir="/"):
    df = pd.DataFrame()

    count = 0
    for (dirpath, dirnames, filenames) in os.walk(path, topdown=True):
        # filter dirnames we're willing to visit
        dirnames[:] = [d for d in dirnames if not d in IGNORE_DIRS]
        filenames[:] = [f for f in filenames if _filename_accept(f)]

        for f in filenames:
            fpath = os.path.join(dirpath, f)
            _df = process_file(fpath, workdir)
            if len(_df):
                df = pd.concat([df,_df])
            count += 1
            if count % 1000 == 0:
                logger.info(f"Processed {count} files so far")

    if "match" in df.columns:
        logger.info(
            f"Found {df['match'].nunique()} matches in {df['file_sha1'].nunique()} out of {count} files"
        )
        df = df.sort_values(by="match").reset_index(drop=True)

    return df
