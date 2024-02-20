# test/test_util_metadata.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.metadata’ packaging module. """

import textwrap

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


class FakeObject(object):
    """ A fake object for testing. """


class docstring_from_object_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘docstring_from_object’ function. """

    scenarios = [
            ('single-line', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.
                    """),
                'expected_result': "Lorem ipsum, dolor sit amet.",
                }),
            ('synopsis one-paragraph', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.
                    """),
                'expected_result': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis."""),
                }),
            ('synopsis three-paragraphs', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                    tellus ac, placerat convallis erat. Nunc id mi libero.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.

                    Suspendisse potenti. Fusce egestas id quam non posuere.
                    Maecenas egestas faucibus elit. Aliquam erat volutpat.
                    """),
                'expected_result': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                    tellus ac, placerat convallis erat. Nunc id mi libero.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.

                    Suspendisse potenti. Fusce egestas id quam non posuere.
                    Maecenas egestas faucibus elit. Aliquam erat volutpat."""),
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        self.test_object = FakeObject()
        self.test_object.__doc__ = self.test_docstring

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = util.metadata.docstring_from_object(self.test_object)
        self.assertEqual(self.expected_result, result)


class synopsis_and_description_from_docstring_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘synopsis_and_description_from_docstring’ function. """

    scenarios = [
            ('single-line', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.
                    """),
                'expected_synopsis': "Lorem ipsum, dolor sit amet.",
                'expected_description': "",
                }),
            ('synopsis one-paragraph', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.
                    """),
                'expected_synopsis': "Lorem ipsum, dolor sit amet.",
                'expected_description': textwrap.dedent("""\
                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis."""),
                }),
            ('synopsis three-paragraphs', {
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                    tellus ac, placerat convallis erat. Nunc id mi libero.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.

                    Suspendisse potenti. Fusce egestas id quam non posuere.
                    Maecenas egestas faucibus elit. Aliquam erat volutpat.
                    """),
                'expected_synopsis': "Lorem ipsum, dolor sit amet.",
                'expected_description': textwrap.dedent("""\
                    Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                    tellus ac, placerat convallis erat. Nunc id mi libero.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.

                    Suspendisse potenti. Fusce egestas id quam non posuere.
                    Maecenas egestas faucibus elit. Aliquam erat volutpat."""),
                }),
            ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = util.metadata.synopsis_and_description_from_docstring(
                self.test_docstring)
        expected_result = (self.expected_synopsis, self.expected_description)
        self.assertEqual(expected_result, result)


# Copyright © 2008–2024 Ben Finney <ben+python@benfinney.id.au>
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
