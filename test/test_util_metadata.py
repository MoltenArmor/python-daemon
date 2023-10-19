# test_util_metadata.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.metadata’ packaging module. """

import testscenarios
import testtools

import util.metadata


class parse_person_field_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_latest_version’ function. """

    scenarios = [
            ('simple', {
                'test_person': "Foo Bar <foo.bar@example.com>",
                'expected_result': ("Foo Bar", "foo.bar@example.com"),
                }),
            ('empty', {
                'test_person': "",
                'expected_result': (None, None),
                }),
            ('none', {
                'test_person': None,
                'expected_error': TypeError,
                }),
            ('no email', {
                'test_person': "Foo Bar",
                'expected_result': ("Foo Bar", None),
                }),
            ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        if hasattr(self, 'expected_error'):
            self.assertRaises(
                    self.expected_error,
                    util.metadata.parse_person_field, self.test_person)
        else:
            result = util.metadata.parse_person_field(self.test_person)
            self.assertEqual(self.expected_result, result)


# Copyright © 2008–2023 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
