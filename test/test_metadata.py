# test/test_metadata.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘_metadata’ private module. """

import re
import urllib.parse as urlparse

import testtools.helpers
import testtools.matchers

import daemon._metadata as metadata

from . import scaffold


class HasAttribute(testtools.matchers.Matcher):
    """ A matcher to assert an object has a named attribute. """

    def __init__(self, name):
        self.attribute_name = name

    def match(self, instance):
        """ Assert the object `instance` has an attribute named `name`. """
        result = None
        if not hasattr(instance, self.attribute_name):
            result = AttributeNotFoundMismatch(instance, self.attribute_name)
        return result


class AttributeNotFoundMismatch(testtools.matchers.Mismatch):
    """ The specified instance does not have the named attribute. """

    def __init__(self, instance, name):
        self.instance = instance
        self.attribute_name = name

    def describe(self):
        """ Emit a text description of this mismatch. """
        text = (
                "{instance!r}"
                " has no attribute named {name!r}").format(
                    instance=self.instance, name=self.attribute_name)
        return text


class metadata_value_TestCase(scaffold.TestCaseWithScenarios):
    """ Test cases for metadata module values. """

    expected_str_attributes = {
            'author',
            'license',
            'url',
            }

    scenarios = [
            (name, {'attribute_name': name})
            for name in expected_str_attributes]
    for (name, params) in scenarios:
        if name == 'version_installed':
            # No duck typing, this attribute might be None.
            params['ducktype_attribute_name'] = NotImplemented
            continue
        # Expect an attribute of ‘str’ to test this value.
        params['ducktype_attribute_name'] = 'isdigit'

    def test_module_has_attribute(self):
        """ Metadata should have expected value as a module attribute. """
        self.assertThat(
                metadata, HasAttribute(self.attribute_name))

    def test_module_attribute_has_duck_type(self):
        """ Metadata value should have expected duck-typing attribute. """
        if self.ducktype_attribute_name == NotImplemented:
            self.skipTest("Can't assert this attribute's type")
        instance = getattr(metadata, self.attribute_name)
        self.assertThat(
                instance, HasAttribute(self.ducktype_attribute_name))


class metadata_content_TestCase(scaffold.TestCase):
    """ Test cases for content of metadata. """

    def test_author_formatted_correctly(self):
        """ Author information should be formatted correctly. """
        regex_pattern = (
                r".+ "  # Name.
                r"<[^>]+>"  # Email address, in angle brackets.
                )
        regex_flags = re.UNICODE
        self.assertThat(
                metadata.author,
                testtools.matchers.MatchesRegex(regex_pattern, regex_flags))

    def test_url_parses_correctly(self):
        """ Homepage URL should parse correctly. """
        result = urlparse.urlparse(metadata.url)
        self.assertIsInstance(
                result, urlparse.ParseResult,
                "URL value {url!r} did not parse correctly".format(
                    url=metadata.url))


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
