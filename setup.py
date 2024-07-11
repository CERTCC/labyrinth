#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

from distutils.core import setup

setup(
    name="labyrinth",
    version="0.8",
    packages=["labyrinth"],
    scripts=[
        "scripts/search_github",
        "scripts/generate_summaries",
        "scripts/repo_deep_dive",
        "scripts/repo_to_vul_id",
    ],
    url="https://vuls.cert.org",
    license="all rights reserved",
    author="adh",
    author_email="adh@cert.org",
    description="search github for exploits",
    include_package_data=True,
    package_data={
        "": [
            "data/*.txt",
        ]
    },
)
