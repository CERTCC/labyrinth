#!/usr/bin/env python
"""
file: repo_processor_2
author: adh
created_at: 9/3/21 9:56 AM
"""
import logging
import os
import time
import datetime
import glob
import tempfile

import dateutil.parser
import pandas as pd
from github import Github, GithubException
import git

import labyrinth
from labyrinth.dir_helpers import setup_output_dirs
import labyrinth.config as cfg
from labyrinth.patterns import repo_id_to_path, find_vul_ids
from labyrinth.ignorelist import IGNORE_REPOS
from labyrinth.rate_limit_helpers import check_rl_core
from labyrinth.file_processor import process_dir

logger = logging.getLogger(__name__)

AGE_LIMIT_SEC = 3600  # might get overwritten at runtime


def set_max_age(age_limit):
    global AGE_LIMIT_SEC
    AGE_LIMIT_SEC = age_limit


def process_git_url(clone_from, workdir):
    logger.debug(f"Cloning {clone_from} to {workdir}")
    try:
        git.Repo().clone_from(
            url=clone_from,
            to_path=workdir,
            depth=1,
        )
    except git.exc.GitCommandError as e:
        logger.warning(f"Skipping git repo at {clone_from} due to GitCommandError: {e}")
        return pd.DataFrame()

    df = process_dir(workdir, workdir)
    return df


def _check_repo_newer(ts, repo_name):
    """
    True if Github has more recent data than repofile
    """
    m_ts = datetime.datetime.fromtimestamp(ts)

    gh = Github(login_or_token=labyrinth.GH_TOKEN)
    check_rl_core(gh)

    try:
        repo = gh.get_repo(repo_name)
    except GithubException as e:
        logger.error(f"Caught GithubException on {repo_name}: {e}")
        return False

    if m_ts < repo.pushed_at:
        return True

    return False


def _check_stale_results(ts):
    """
    True if age of repofile exceeds AGE_LIMIT_SEC
    """
    age_seconds = time.time() - ts
    # are they recent?

    if age_seconds >= AGE_LIMIT_SEC:
        return True

    return False


def process_row(row):
    # each row is a record for a repository
    repo_name = row["full_name"]
    repo_id = row["id"]
    clone_url = row["clone_url"]
    repo_num = row["index"]
    repo_tot = row["total_repos"]

    df = pd.DataFrame()

    for key, ignorelist in IGNORE_REPOS.items():

        if str(row[key]).lower() in ignorelist:
            return pd.DataFrame()

    repo_path = os.path.join(cfg.REPO_ID_RESULTS_HOME, repo_id_to_path(repo_id))
    csvfile = os.path.join(repo_path, f"{repo_id}.csv")
    tsfile = os.path.join(repo_path, f"{repo_id}.ts")

    # do we already have results for repo?
    if os.path.exists(tsfile):

        # read ts
        ts = None
        with open(tsfile, "r") as fp:
            content = fp.read()
            try:
                ts = dateutil.parser.isoparse(content.strip()).timestamp()
            except ValueError as e:
                logger.error(f"Failed to parse timestamp out of {tsfile}: {e}")

        if ts is not None:
            stale = _check_stale_results(ts)
            if not stale:
                logger.info(
                    f"Found existing results for {repo_name} within past {AGE_LIMIT_SEC} seconds, skipping"
                )
            #     return pd.DataFrame()

            # it is stale, but does github have anything newer?
            gh_has_newer = _check_repo_newer(ts, repo_name)
            if not gh_has_newer:
                logger.info(f"Repo has not changed since we last looked, skipping")
                return pd.DataFrame()
    else:
        # we don't already have results
        # write an empty file to at least record that we looked at this repo
        # it will get overwritten later if we have results
        logger.debug(f"No existing results found for {csvfile}, creating placeholder")
        os.makedirs(repo_path, exist_ok=True)
        df.to_csv(csvfile, index=False)

    row_matches = find_vul_ids(_concat_str_cols(row))

    if len(row_matches):
        df["match"] = row_matches
        df["file"] = "_GITHUB_REPO_METADATA_"
        df["file_sha1"] = None

    with tempfile.TemporaryDirectory(prefix="git-clone-") as workdir:
        logger.info(f"Cloning {clone_url} {repo_num} of {repo_tot}")
        _df = process_git_url(clone_url, workdir)

    if len(_df):
        df = pd.concat([df,_df])

    if not len(df):
        return pd.DataFrame()

    df = df.sort_values(by="match")
    df = df.drop_duplicates(subset=["match", "file_sha1"])

    # these are the same for every row
    df["repo_full_name"] = repo_name
    df["repo_id"] = repo_id
    df["repo_html_url"] = row["html_url"]
    df["repo_pushed_at"] = row["pushed_at"]

    # write the timestamp file for this repo
    with open(tsfile, "w") as fp:
        # we don't need subsecond resolution for this
        now = datetime.datetime.now().replace(microsecond=0)
        fp.write(f"{now.isoformat()}\n")

    return df


def _concat_str_cols(row):
    cols2check = [
        "full_name",
        "html_url",
        "description",
        "url",
        "homepage",
    ]
    # concatenate some string columns so we can do a single vul ID pattern match
    # note that this has to be done before we truncate the descriptions in the next step
    _concatenated_strings = " ".join([str(x) for x in row[cols2check]])
    return _concatenated_strings


def scan_repos(top_dir, mod=None, divisor=100):
    # read in summary search result data
    glob_pattern = f"{top_dir}/**/*_summary.json"
    summary_files = glob.glob(glob_pattern, recursive=True)

    df = pd.DataFrame()
    logger.info(f"Reading {len(summary_files)} search result summaries")
    # read in the files one at a time
    for f in summary_files:
        logger.debug(f"Reading results from {f}")
        _df = pd.read_json(f)
        if mod is not None:
            # filter out and keep only the ones that match our desired modulus
            mods = _df["id"].apply(lambda x: x % divisor)
            _df = _df[mods == mod]
        # append them onto our collection
        df = pd.concat((df, _df)).drop_duplicates(subset=["id"])
        logger.debug(f"Found {len(df)} results so far")

    logger.info(f"Found {len(df)} search results to process")
    if len(df) == 0:
        return pd.DataFrame()

    # start small, get bigger
    df = df.sort_values(by="size", ascending=True)
    # get a clean index
    df = df.reset_index(drop=True)
    # get a column for the index by size
    df = df.reset_index(drop=False)
    # but it's zero based and we want a 1-based counter
    df["index"] += 1
    # so now the total is just the max of the index
    df["total_repos"] = df["index"].max()

    # process it row-wise
    results = df.apply(process_row, axis=1).to_list()
    # aggregate results
    df1 = pd.concat(results)

    if len(df1):
        df1 = df1.sort_values(by="match")

    return df1


def _dump_csv(df, outfile):
    df.to_csv(outfile, index=False, float_format="%.6f")


def dump_results_by_repo(df):
    outdir = cfg.REPO_ID_RESULTS_HOME
    os.makedirs(outdir, exist_ok=True)

    cols = ["repo_id", "repo_full_name", "file", "file_sha1", "match"]
    try:
        df = pd.DataFrame(df[cols])
    except KeyError as e:
        logger.warning(f"Caught KeyError on DataFrame: {e}")
        return

    df = df.drop_duplicates()
    df = df.sort_values(by=["repo_id", "file"])

    for gname, group in df.groupby(by=["repo_id"]):
        group_path = repo_id_to_path(gname)
        group_dir = os.path.join(outdir, group_path)
        os.makedirs(group_dir, exist_ok=True)

        csvfile = os.path.join(group_dir, f"{gname}.csv")

        # we're just going to overwrite the old data since we just looked at the whole thing
        new_df = group
        new_df = new_df.sort_values(by=["match", "file"], ascending=True)
        new_df = new_df.drop_duplicates(
            subset=["file_sha1", "match"],
            keep="first",
        )

        repo_name = group["repo_full_name"].unique()[0]

        logger.debug(f"Write {repo_name} results to {csvfile} ({len(new_df)})")
        # sort by file_sha1 to keep the json ordering consistent across runs
        new_df = new_df.sort_values(by="file_sha1", ascending=True)
        _dump_csv(new_df, csvfile)


def process_modulo(top_dir, mod=None, divisor=100):
    setup_output_dirs()
    df = scan_repos(top_dir, mod, divisor)
    if len(df):
        dump_results_by_repo(df)
    else:
        logger.warning("No results found")


def concat_string_fields(df):
    cols2check = [
        "full_name",
        "html_url",
        "description",
        "url",
        "homepage",
    ]
    # concatenate some string columns so we can do a single vul ID pattern match
    # note that this has to be done before we truncate the descriptions in the next step
    _concatenated_strings = (
        df[cols2check].fillna("").applymap(str).agg(" ".join, axis=1)
    )
    return _concatenated_strings
