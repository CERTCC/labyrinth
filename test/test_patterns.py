#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import unittest
import labyrinth.patterns as lp

pattern_tests = [
    ("cve_2019-10298282", "CVE-2019-10298282"),
    ("cve2019-10298282", "CVE-2019-10298282"),
    ("cveaosjdocn29918asoenwhh1129", "CVE-29918-1129"),
    ("bid_201982", "BID-201982"),
    ("Vu1234", "VU#1234"),
    ("Vu////1234", "VU#1234"),
    ("icSa1927-1720-128w", "ICSA-1927-1720-128W"),
    ("uvi--1238-1221y2", "UVI-1238-1221"),
]


class MyTestCase(unittest.TestCase):
    def test_find_vul_ids(self):
        test_str = (
            "cve-1066-1234, Vu090909; ms88-001::BId-1082 "
            "zdi_can-1234.Zdi-12-1234, cNvD_1923-10288"
        )

        r = lp.find_vul_ids(test_str)
        self.assertIn("CVE-1066-1234", r)
        self.assertIn("VU#090909", r)
        self.assertIn("MS88-001", r)
        self.assertIn("BID-1082", r)
        self.assertIn("ZDI-CAN-1234", r)
        self.assertIn("ZDI-12-1234", r)
        self.assertIn("CNVD-1923-10288", r)

    def test_normalize(self):
        for input, expected_output in pattern_tests:
            output = lp.normalize(input)
            self.assertEqual(expected_output, output)

    def test_id_to_path(self):
        id_str = "VU#1234"
        self.assertEqual("VU/12/VU#1234", lp.id_to_path(id_str))

        id_str = "CNVD-C-1234-1234"
        self.assertEqual("CNVD/1234/12/CNVD-C-1234-1234", lp.id_to_path(id_str))

        id_str = "CVE-1234-123456"
        self.assertEqual("CVE/1234/12/CVE-1234-123456", lp.id_to_path(id_str))

        id_str = "BID-12038"
        self.assertEqual("BID/12/BID-12038", lp.id_to_path(id_str))

        id_str = "MS04-1827"
        self.assertEqual("MS/04/MS04-1827", lp.id_to_path(id_str))

    def test_repo_id_to_path(self):
        id_str = "a"
        self.assertEqual("a/a", lp.repo_id_to_path(id_str))

        id_str = "ab"
        self.assertEqual("ab/ab", lp.repo_id_to_path(id_str))

        id_str = "abc"
        self.assertEqual("ab/c/abc", lp.repo_id_to_path(id_str))

        id_str = "abcd"
        self.assertEqual("ab/cd/abcd", lp.repo_id_to_path(id_str))

        id_str = "abcde"
        self.assertEqual("ab/cd/e/abcde", lp.repo_id_to_path(id_str))

        id_str = "abcdef"
        self.assertEqual("ab/cd/ef/abcdef", lp.repo_id_to_path(id_str))

        id_str = "abcdefg"
        self.assertEqual("ab/cd/ef/abcdefg", lp.repo_id_to_path(id_str))

        id_str = "abcdefghijklmnop"
        self.assertEqual("ab/cd/ef/abcdefghijklmnop", lp.repo_id_to_path(id_str))

    def test_oldpath2newpath(self):
        pass


if __name__ == "__main__":
    unittest.main()
