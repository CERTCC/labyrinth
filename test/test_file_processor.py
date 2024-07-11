#  Copyright (c) 2023 Carnegie Mellon University.
#  Labyrinth Repository Search
#  Licensed under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  Carnegie Mellon®, CERT® and CERT Coordination Center® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
#  This Software includes and/or makes use of Third-Party Software subject to its own license, see license.txt file for more information.
#  DM23-0717
#

import unittest
import tempfile
import labyrinth.file_processor as filep
import shutil
import random


alphabet = "abcdefghijklmnopqrstuvwxyz"


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.workdir)

    @unittest.skip("not implemented")
    def test_process_file(self):
        # TODO: write me
        pass

    def test_file_sha1(self):
        tf = tempfile.mktemp(dir=self.workdir)
        with open(tf, "w") as fp:
            fp.write(alphabet)
            fp.write("\n")

        # checked against shasum on mac
        self.assertEqual(
            "8c723a0fa70b111017b4a6f06afe1c0dbcec14e3", filep._file_sha1(tf)
        )

    def test_filename_accept(self):
        for ext in [".json", ".png", ".jpg", ".gif", ".owl"]:
            with self.subTest(ext=ext):
                for i in range(30):
                    s = "".join(random.choice(alphabet) for _ in range(12))
                    # accept most things
                    self.assertTrue(filep._filename_accept(s))
                    # unless it starts with .git
                    self.assertFalse(filep._filename_accept(f".git/{s}"))
                    # or it ends with an undesired extension
                    self.assertFalse(filep._filename_accept(s + ext))

    @unittest.skip("not implemented")
    def test_process_dir(self):
        # TODO: write me
        pass


if __name__ == "__main__":
    unittest.main()
