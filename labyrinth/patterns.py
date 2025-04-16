#!/usr/bin/env python
"""
file: patterns
author: adh
created_at: 3/27/20 9:47 AM
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
import os
from labyrinth.errors import LabyrinthPatternError

ID_PATTERNS = [
    # sometimes with dashes,
    # sometimes with underscores, like in urls
    "CVE[-_][0-9]{4}[-_][0-9]+",
    # find metasploit code mentioning CVE IDs
    "CVE.?,\s+.?[0-9]{4}-[0-9]+",
    # some exploitdb matches CVE : YYYY-nnnnn
    "CVE\s+:\s+[0-9]{4}-[0-9]+",
    # VU#nn, VU-nn, VU_nn, VUnn
    "VU[#-_]?[0-9]{2,}",
    # Euro Vul Db
    "EUVD[-_][0-9]{4}[-_][0-9]+",
    # Global Security Db
    "GSD[-_][0-9]{4}[-_][0-9]+",
    # Bugtraq ID
    "BID-\d+",
    # bugtraq id in urls
    "securityfocus\.com/bid/\d+",
    # find metasploit code mentioning BIDs
    "BID.?,\s+.?[0-9]+",
    "OSVDB[-_]\d+",
    # find metasploit code mentioning OSVDBIDs
    "OSVDB.?,\s+.?[0-9]+",
    # find VU# by urls
    "kb\.cert\.org/vuls/id/\d+",
    # ICSA
    "ICSA[-_]0-9]{2}[-_][0-9]+[-_][0-9]+[A-Z]",
    # UVI https://github.com/cloudsecurityalliance/uvi-database
    "UVI[-_][0-9]{4}[-_][0-9]+",
    # microsoft
    "MS[0-9]{2}[-_][0-9]+",
    # zero day inititative (two ID formats)
    "ZDI[-_]CAN[-_][0-9]+",
    "ZDI[-_][0-9]{2}[-_][0-9]+",
    # Google Project Zero
    "bugs\.chromium\.org/p/project-zero/issues/detail\?id=\d+",
    "code.google.com/p/google-security-research/issues/detail\?id=\d+",
    # Zero Science Lab
    "ZSL[-_][0-9]{4}[-_][0-9]+",
    # china nvd
    "CNVD[-_][0-9]{4}[-_][0-9]+",
    # find metasploit code mentioning CNVD IDs
    "CNVD.?,\s+.?[0-9]{4}[-_][0-9]+",
    # china nvd
    "CNVD[-_]C[-_][0-9]{4}[-_][0-9]+",
    # china NNVD CNNVD-{YYYY}{MM}-{NNN}
    "CNNVD[-_][0-9]{6}[-_][0-9]+",
    # github security advisories e.g. GHSA-289g-75hj-mg9m
    "GHSA[-_][a-z0-9]{4}[-_][a-z0-9]{4}[-_][a-z0-9]{4}",
]
ID_REGEX = "|".join(ID_PATTERNS)  # join into one giant regex
PATTERN = re.compile(ID_REGEX, re.I)  # compile it case insensitive

ID_REGEX_CLI = f'"{ID_REGEX}"'  # enclose in quotes


def find_vul_ids(str):
    matches = (normalize(m) for m in PATTERN.findall(str))
    matches = sorted(list(set(matches)))
    return matches


def normalize(id_str):
    id_str = id_str.upper()

    # note: because we're using "startswith" it's ok to use "match"
    # otherwise we'd want to use "search"
    #
    # also, since we've already matched the ID patterns above,
    # we can be a bit more liberal in our pattern matching here
    # (e.g., using \D instead of specific delimiters)
    m = re.match("CVE\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"CVE-{m.groups()[0]}-{int(m.groups()[1]):04d}"

    m = re.match("EUVD\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"EUVD-{m.groups()[0]}-{int(m.groups()[1]):04d}"
    m = re.match("GSD\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    
    if m:
        return f"GSD-{m.groups()[0]}-{int(m.groups()[1]):04d}"
    
    m = re.match("BID\D*(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"BID-{int(m.groups()[0])}"

    m = re.match("SECURITYFOCUS\.COM/BID/(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"BID-{int(m.groups()[0])}"

    m = re.match("OSVDB\D*(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"OSVDB-{int(m.groups()[0])}"

    m = re.match("VU\D*(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"VU#{m.groups()[0]}"

    m = re.match("KB\.CERT\.ORG/VULS/ID/(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"VU#{int(m.groups()[0])}"

    m = re.match("ICSA\D*(\d+)\D+(\d+)\D+(\d+\w?)", id_str, re.IGNORECASE)
    if m:
        return f"ICSA-{m.groups()[0]}-{m.groups()[1]}-{m.groups()[2]}"

    m = re.match("UVI\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"UVI-{m.groups()[0]}-{m.groups()[1]}"

    m = re.match("MS(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"MS{m.groups()[0]}-{int(m.groups()[1]):03d}"

    # ZDI-CAN-NNN
    m = re.match("ZDI[^C]+CAN\D*(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"ZDI-CAN-{m.groups()[0]}"

    # ZDI-NN-NNN
    m = re.match("ZDI\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"ZDI-{m.groups()[0]}-{m.groups()[1]}"

    # ZSL-NN-NNN
    m = re.match("ZSL\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"ZSL-{m.groups()[0]}-{m.groups()[1]}"

    if id_str.startswith("BUGS.CHROMIUM.ORG"):
        m = re.search("PROJECT-ZERO/ISSUES/DETAIL\?ID=(\d+)", id_str, re.IGNORECASE)
        if m:
            return f"GPZ-{m.groups()[0]}"

    if id_str.startswith("CODE.GOOGLE.COM"):
        m = re.search(
            "GOOGLE-SECURITY-RESEARCH/ISSUES/DETAIL\?ID=(\d+)", id_str, re.IGNORECASE
        )
        if m:
            return f"GPZ-{m.groups()[0]}"

    m = re.match("CNVD\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"CNVD-{m.groups()[0]}-{m.groups()[1]}"

    # candidates?
    m = re.match("CNVD[^C]+C\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"CNVD-C-{m.groups()[0]}-{m.groups()[1]}"

    m = re.match("CNNVD\D*(\d+)\D+(\d+)", id_str, re.IGNORECASE)
    if m:
        return f"CNNVD-{m.groups()[0]}-{m.groups()[1]}"

    m = re.match("GHSA[^a-z0-9]*([a-z0-9]+)[^a-z0-9]*([a-z0-9]+)[^a-z0-9]*([a-z0-9]+)", id_str, re.IGNORECASE)
    if m:
        return f"GHSA-{m.groups()[0]}-{m.groups()[1]}-{m.groups()[2]}"

    # default to no change
    return id_str


def id_to_path(id_str):
    parts = None

    if id_str.startswith("VU#"):
        m = re.match("(VU)#(\d{2})", id_str)
        if m:
            parts = [m.groups()[0], m.groups()[1], id_str]
    elif id_str.startswith("CNVD-C"):
        m = re.match("CNVD-C-(\d+)-(\d+)", id_str)
        if m:
            # "CNVD-C-2010-10201801 --> CNVD, 2010, 10, CNVD-C-2010-10201801
            parts = ["CNVD", m.groups()[0], m.groups()[1][:2], id_str]
    elif id_str.count("-") > 1:
        # get the first two chunks
        m = re.match("([^-]+)-([^-]+)-(.+)", id_str)
        if m:
            # "CVE-2010-10201801 --> CVE, 2010, 10, CVE-2010-10201801
            parts = [m.groups()[0], m.groups()[1], m.groups()[2][:2], id_str]
    elif id_str.count("-") == 1:
        # MS08-067 like
        m = re.match("([a-z]+)(\d+)-(\d+)", id_str, re.IGNORECASE)
        if m:
            # MS08-067 --> MS, 08, MS08-067
            parts = [m.groups()[0], m.groups()[1], id_str]
        else:
            # BID-10108 like - we just want the first 2 digits to spread the files out
            m = re.match("([a-z]+)-(\d{1,2})", id_str, re.IGNORECASE)
            if m:
                # BID-10108 --> BID, 10, BID-10108
                parts = [m.groups()[0], m.groups()[1], id_str]

    if parts is None:
        raise LabyrinthPatternError(
            f"Could not parse id string {id_str} into directories"
        )

    return os.path.join(*parts)


def repo_id_to_path(id_str):
    # make sure it's a string not an int
    id_str = str(id_str)
    # split it into chunks
    parts = re.findall(".{1,2}", id_str)
    # take up to the first 3 chunks
    # (list slices are tolerant when there are less than 3)
    parts = parts[:3]
    parts.append(id_str)

    return os.path.join(*parts)


def oldpath2newpath(oldpath):
    if "CVE" in oldpath:
        pattern = re.compile("(CVE-(\d+)-(\d+))")
        cve_id, year, num = pattern.search(oldpath).groups()
        return os.path.join("data/vul_id", id_to_path(cve_id))
