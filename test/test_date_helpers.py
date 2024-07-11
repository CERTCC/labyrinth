#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import unittest
import labyrinth.date_helpers as dh


class MyTestCase(unittest.TestCase):
    def test_year_begin(self):
        for year in range(1988, 2100):
            jan1 = f"{year:04d}-01-01"
            for month in range(1, 13):
                for d in range(1, 29):
                    # every day should yield jan 1 of the same year
                    d = f"{year:04d}-{month:02d}-{d:02d}"
                    self.assertEqual(jan1, dh.year_begin(d))

    def test_year_end(self):
        for year in range(1988, 2100):
            dec31 = f"{year:04d}-12-31"
            for month in range(1, 13):
                for d in range(1, 29):
                    d = f"{year:04d}-{month:02d}-{d:02d}"
                    # every day should yield dec 31 of the same year
                    self.assertEqual(dec31, dh.year_end(d))

    def test_month_begin(self):
        for year in range(1988, 2100):
            for month in range(1, 13):
                mon1 = f"{year:04d}-{month:02d}-01"
                for d in range(1, 29):
                    d = f"{year:04d}-{month:02d}-{d:02d}"
                    self.assertEqual(mon1, dh.month_begin(d))

    def test_month_end(self):
        for year in range(1988, 2100):
            if year % 2:
                # only check Feb in odd years so we don't have to
                # worry about leap years
                month = 2
                for d in range(1, 29):
                    eom = f"{year:04d}-{month:02d}-28"
                    day = f"{year:04d}-{month:02d}-{d:02d}"
                    self.assertEqual(
                        eom,
                        dh.month_end(day),
                    )
            for month in [1, 3, 5, 7, 8, 10, 12]:
                mon31 = f"{year:04d}-{month:02d}-31"
                for d in range(1, 32):
                    d = f"{year:04d}-{month:02d}-{d:02d}"
                    self.assertEqual(mon31, dh.month_end(d))
            for month in [4, 6, 9, 11]:
                mon31 = f"{year:04d}-{month:02d}-30"
                for d in range(1, 31):
                    d = f"{year:04d}-{month:02d}-{d:02d}"
                    self.assertEqual(mon31, dh.month_end(d))

    def test_fixup_end_date(self):
        for year in range(1988, 2100):
            self.assertEqual(f"{year:4d}-12-31", dh.fixup_end_date(str(year)))

            for month in range(1, 13):
                s = f"{year:04d}-{month:02d}"
                self.assertTrue(
                    dh.fixup_end_date(s).startswith(f"{year:04d}-{month:02d}-")
                )

    def test_fixup_start_date(self):
        for year in range(1988, 2100):
            for month in range(1, 13):
                s = f"{year:04d}-{month:02d}"
                self.assertEqual(f"{year}-{month:02d}-01", dh.fixup_start_date(s))

            self.assertEqual(f"{year:4d}-01-01", dh.fixup_start_date(str(year)))


if __name__ == "__main__":
    unittest.main()
