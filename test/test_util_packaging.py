# test/test_util_packaging.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.packaging’ packaging module. """

import builtins
import collections
import os
import os.path
import textwrap
import types
import unittest.mock

import setuptools
import setuptools.command
import setuptools.dist
import testscenarios
import testtools

from util import packaging


class FakeModule(types.ModuleType):
    """ A fake module object with no code. """


def patch_builtins_import(
        testcase,
        *,
        fake_module=None,
        fake_module_name='lorem',
):
    """ Patch the built-in ‘__import__’ for the `testcase`. """
    if fake_module is None:
        fake_module = FakeModule(name=fake_module_name)

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        result = (
                fake_module if (name == fake_module_name)
                else orig_import(
                    name,
                    globals=globals, locals=locals,
                    fromlist=fromlist, level=level)
        )
        return result

    orig_import = builtins.__import__
    func_patcher = unittest.mock.patch.object(
            builtins, '__import__',
            wraps=fake_import)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)


class main_module_by_name_TestCase(
        testscenarios.WithScenarios, unittest.TestCase):
    """ Test cases for ‘get_changelog_path’ function. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_module_name = 'lorem'
        self.test_module = FakeModule(self.test_module_name)
        patch_builtins_import(
            self,
            fake_module=self.test_module,
            fake_module_name=self.test_module_name,
        )

    def test_returns_expected_module_for_correct_name(self):
        """ Should return expected module object. """
        result = packaging.main_module_by_name(self.test_module_name)
        self.assertEqual(self.test_module, result)

    def test_raises_importerror_for_unexpected_name(self):
        """ Should raise ImportError when name is unexpected. """
        with self.assertRaises(ModuleNotFoundError):
            __ = packaging.main_module_by_name('b0gUs')


DistributionMetadata_defaults = {
        name: None
        for name in list(collections.OrderedDict.fromkeys(
            getattr(
                setuptools.distutils.dist.DistributionMetadata,
                '_METHOD_BASENAMES')))
        }
FakeDistributionMetadata = collections.namedtuple(
        'FakeDistributionMetadata', DistributionMetadata_defaults.keys())

Distribution_defaults = {
        'metadata': None,
        'version': None,
        'release_date': None,
        'maintainer': None,
        'maintainer_email': None,
        }
FakeDistribution = collections.namedtuple(
        'FakeDistribution', Distribution_defaults.keys())


def make_fake_distribution(
        fields_override=None, metadata_fields_override=None):
    metadata_fields = DistributionMetadata_defaults.copy()
    if metadata_fields_override is not None:
        metadata_fields.update(metadata_fields_override)
    metadata = FakeDistributionMetadata(**metadata_fields)

    fields = Distribution_defaults.copy()
    fields['metadata'] = metadata
    if fields_override is not None:
        fields.update(fields_override)
    distribution = FakeDistribution(**fields)

    return distribution


def patch_main_module_by_name(
        testcase,
        *,
        fake_module=None,
        fake_module_name='lorem',
):
    """ Patch the ‘main_module_by_name’ function for the `testcase`. """
    if fake_module is None:
        fake_module = FakeModule(name=fake_module_name)
    func_patcher = unittest.mock.patch.object(
            packaging, 'main_module_by_name',
            return_value=fake_module)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)


def patch_docstring_from_object(testcase, *, fake_docstring):
    """ Patch the ‘docstring_from_object’ function for the `testcase`. """
    func_patcher = unittest.mock.patch.object(
            packaging, 'docstring_from_object',
            return_value=fake_docstring)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)


class derive_dist_description_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘derive_dist_description’ function. """

    scenarios = [
            ('simple', {
                'test_args': {
                    'distribution': setuptools.dist.Distribution(),
                    },
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.
                    """),
                'expected_synopsis': "Lorem ipsum, dolor sit amet.",
                'expected_long_description': textwrap.dedent("""\
                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis."""),
                'expected_long_description_content_type': "text/x-rst",
                }),
            ('content-type-specified', {
                'test_args': {
                    'distribution': setuptools.dist.Distribution(),
                    'content_type': "text/markdown",
                    },
                'test_docstring': textwrap.dedent("""\
                    Lorem ipsum, dolor sit amet.

                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis.
                    """),
                'expected_synopsis': "Lorem ipsum, dolor sit amet.",
                'expected_long_description': textwrap.dedent("""\
                    Donec et semper sapien, et faucibus felis. Nunc suscipit
                    quam id lectus imperdiet varius. Praesent mattis arcu in
                    sem laoreet, at tincidunt velit venenatis."""),
                'expected_long_description_content_type': "text/markdown",
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        patch_main_module_by_name(self)
        patch_docstring_from_object(self, fake_docstring=self.test_docstring)
        self.test_distribution = self.test_args['distribution']

    def test_sets_expected_synopsis(self):
        """ Should set the expected `metadata.description` value. """
        packaging.derive_dist_description(**self.test_args)
        self.assertEqual(
                self.expected_synopsis,
                self.test_distribution.metadata.description)

    def test_sets_expected_long_description(self):
        """ Should set the expected `metadata.long_description` value. """
        packaging.derive_dist_description(**self.test_args)
        self.assertEqual(
                self.expected_long_description,
                self.test_distribution.metadata.long_description)

    def test_sets_expected_long_description_content_type(self):
        """ Should set expected `metadata.long_description_content_type`. """
        packaging.derive_dist_description(**self.test_args)
        self.assertEqual(
                self.expected_long_description_content_type,
                self.test_distribution.metadata.long_description_content_type)


def patch_get_changelog_path(testcase, *, fake_path):
    """ Patch the ‘main_module_by_name’ function for the `testcase`. """
    func_patcher = unittest.mock.patch.object(
            packaging, 'get_changelog_path',
            return_value=fake_path)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)


def patch_generate_version_info_from_changelog(testcase, *, fake_result):
    """ Patch ‘generate_version_info_from_changelog’ for the `testcase`. """
    func_patcher = unittest.mock.patch.object(
            packaging, 'generate_version_info_from_changelog',
            return_value=fake_result)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)


class derive_version_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘derive_version’ function. """

    scenarios = [
            ('simple', {
                'fake_version_info': {
                    'release_date': "2023-10-20",
                    'version': "4.0.7",
                    'maintainer': "Yolanda Hall <yhall@kline-barnes.biz>",
                    'body': None,
                    },
                'expected_version': "4.0.7",
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        patch_get_changelog_path(self, fake_path="/nonexistent")
        patch_generate_version_info_from_changelog(
                self, fake_result=self.fake_version_info)
        self.test_distribution = setuptools.dist.Distribution()

    def test_sets_expected_version_attribute(self):
        """ Should set expected `metadata.version` value. """
        packaging.derive_version(self.test_distribution)
        self.assertEqual(
                self.expected_version,
                self.test_distribution.metadata.version)


class derive_maintainer_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘derive_maintainer’ function. """

    scenarios = [
            ('simple', {
                'fake_version_info': {
                    'release_date': "2023-10-20",
                    'version': "4.0.7",
                    'maintainer': "Yolanda Hall <yhall@kline-barnes.biz>",
                    'body': None,
                    },
                'expected_maintainer': "Yolanda Hall",
                'expected_maintainer_email': "yhall@kline-barnes.biz",
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        patch_get_changelog_path(self, fake_path="/nonexistent")
        patch_generate_version_info_from_changelog(
                self, fake_result=self.fake_version_info)
        self.test_distribution = setuptools.dist.Distribution()

    def test_sets_expected_maintainer_attribute(self):
        """ Should set expected `metadata.maintainer` value. """
        packaging.derive_maintainer(self.test_distribution)
        self.assertEqual(
                self.expected_maintainer,
                self.test_distribution.metadata.maintainer)

    def test_sets_expected_maintainer_email_attribute(self):
        """ Should set expected `metadata.maintainer_email` value. """
        packaging.derive_maintainer(self.test_distribution)
        self.assertEqual(
                self.expected_maintainer_email,
                self.test_distribution.metadata.maintainer_email)


class get_changelog_path_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_changelog_path’ function. """

    default_src_root = "/dolor/sit/amet"
    default_script_filename = "setup.py"

    scenarios = [
            ('simple', {}),
            ('unusual script name', {
                'script_filename': "lorem_ipsum",
                }),
            ('specify root path', {
                'src_root': "/diam/ornare",
                }),
            ('specify filename', {
                'changelog_filename': "adipiscing",
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        test_distribution = setuptools.dist.Distribution()
        self.test_distribution = unittest.mock.MagicMock(
                test_distribution)

        if not hasattr(self, 'src_root'):
            self.src_root = self.default_src_root
        if not hasattr(self, 'script_filename'):
            self.script_filename = self.default_script_filename

        self.test_distribution.packages = None
        self.test_distribution.package_dir = {'': self.src_root}
        self.test_distribution.script_name = self.script_filename

        changelog_filename = packaging.changelog_filename
        if hasattr(self, 'changelog_filename'):
            changelog_filename = self.changelog_filename

        self.expected_result = os.path.join(self.src_root, changelog_filename)

    def test_returns_expected_result(self):
        """ Should return expected result. """
        args = {
                'distribution': self.test_distribution,
                }
        if hasattr(self, 'changelog_filename'):
            args.update({'filename': self.changelog_filename})
        result = packaging.get_changelog_path(**args)
        self.assertEqual(self.expected_result, result)


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
