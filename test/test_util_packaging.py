# test/test_util_packaging.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.packaging’ packaging module. """

import collections
import io
import os
import os.path
import unittest.mock

import setuptools
import setuptools.command
import setuptools.dist
import testscenarios
import testtools

from util import packaging


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


class WriteVersionInfoCommand_BaseTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Base class for ‘WriteVersionInfoCommand’ test case classes. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        fake_distribution_name = self.getUniqueString()

        self.test_distribution = setuptools.dist.Distribution()
        self.test_distribution.metadata.name = fake_distribution_name


class WriteVersionInfoCommand_TestCase(WriteVersionInfoCommand_BaseTestCase):
    """ Test cases for ‘WriteVersionInfoCommand’ class. """

    def test_subclass_of_setuptools_command(self):
        """ Should be a subclass of ‘setuptools.Command’. """
        instance = packaging.WriteVersionInfoCommand(self.test_distribution)
        self.assertIsInstance(instance, setuptools.Command)


class WriteVersionInfoCommand_user_options_TestCase(
        WriteVersionInfoCommand_BaseTestCase):
    """ Test cases for ‘WriteVersionInfoCommand.user_options’ attribute. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = packaging.WriteVersionInfoCommand(
                self.test_distribution)
        self.FancyGetopt = setuptools.distutils.fancy_getopt.FancyGetopt
        self.commandline_parser = self.FancyGetopt(
                self.test_instance.user_options)

    def test_parses_correctly_as_fancy_getopt(self):
        """ Should parse correctly in ‘FancyGetopt’. """
        self.assertIsInstance(self.commandline_parser, self.FancyGetopt)

    def test_includes_base_class_user_options(self):
        """ Should include base class's user_options. """
        base_command = setuptools.command.egg_info.egg_info
        expected_user_options = base_command.user_options
        self.assertThat(
                set(expected_user_options),
                IsSubset(set(self.test_instance.user_options)))

    def test_has_option_changelog_path(self):
        """ Should have a ‘changelog-path’ option. """
        expected_option_name = "changelog-path="
        result = self.commandline_parser.has_option(expected_option_name)
        self.assertTrue(result)

    def test_has_option_outfile_path(self):
        """ Should have a ‘outfile-path’ option. """
        expected_option_name = "outfile-path="
        result = self.commandline_parser.has_option(expected_option_name)
        self.assertTrue(result)


class WriteVersionInfoCommand_initialize_options_TestCase(
        WriteVersionInfoCommand_BaseTestCase):
    """ Test cases for ‘WriteVersionInfoCommand.initialize_options’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        patcher_func_egg_info_initialize_options = (
                unittest.mock.patch.object(
                    setuptools.command.egg_info.egg_info,
                    "initialize_options"))
        patcher_func_egg_info_initialize_options.start()
        self.addCleanup(patcher_func_egg_info_initialize_options.stop)

    def test_calls_base_class_method(self):
        """ Should call base class's ‘initialize_options’ method. """
        packaging.WriteVersionInfoCommand(self.test_distribution)
        base_command_class = setuptools.command.egg_info.egg_info
        base_command_class.initialize_options.assert_called_with()

    def test_sets_changelog_path_to_none(self):
        """ Should set ‘changelog_path’ attribute to ``None``. """
        instance = packaging.WriteVersionInfoCommand(self.test_distribution)
        self.assertIs(instance.changelog_path, None)

    def test_sets_outfile_path_to_none(self):
        """ Should set ‘outfile_path’ attribute to ``None``. """
        instance = packaging.WriteVersionInfoCommand(self.test_distribution)
        self.assertIs(instance.outfile_path, None)


class WriteVersionInfoCommand_finalize_options_TestCase(
        WriteVersionInfoCommand_BaseTestCase):
    """ Test cases for ‘WriteVersionInfoCommand.finalize_options’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = packaging.WriteVersionInfoCommand(
                self.test_distribution)

        patcher_func_egg_info_finalize_options = unittest.mock.patch.object(
                setuptools.command.egg_info.egg_info, "finalize_options")
        patcher_func_egg_info_finalize_options.start()
        self.addCleanup(patcher_func_egg_info_finalize_options.stop)

        self.fake_script_dir = self.getUniqueString()
        self.test_distribution.script_name = os.path.join(
                self.fake_script_dir, self.getUniqueString())

        self.fake_egg_dir = self.getUniqueString()
        self.test_instance.egg_info = self.fake_egg_dir

        patcher_func_get_changelog_path = unittest.mock.patch.object(
                packaging, "get_changelog_path")
        patcher_func_get_changelog_path.start()
        self.addCleanup(patcher_func_get_changelog_path.stop)

        self.fake_changelog_path = self.getUniqueString()
        packaging.get_changelog_path.return_value = self.fake_changelog_path

    def test_calls_base_class_method(self):
        """ Should call base class's ‘finalize_options’ method. """
        base_command_class = setuptools.command.egg_info.egg_info
        self.test_instance.finalize_options()
        base_command_class.finalize_options.assert_called_with()

    def test_sets_force_to_none(self):
        """ Should set ‘force’ attribute to ``None``. """
        self.test_instance.finalize_options()
        self.assertIs(self.test_instance.force, None)

    def test_sets_changelog_path_using_get_changelog_path(self):
        """ Should set ‘changelog_path’ attribute if it was ``None``. """
        self.test_instance.changelog_path = None
        self.test_instance.finalize_options()
        expected_changelog_path = self.fake_changelog_path
        self.assertEqual(
                expected_changelog_path, self.test_instance.changelog_path)

    def test_leaves_changelog_path_if_already_set(self):
        """ Should leave ‘changelog_path’ attribute set. """
        prior_changelog_path = self.getUniqueString()
        self.test_instance.changelog_path = prior_changelog_path
        self.test_instance.finalize_options()
        expected_changelog_path = prior_changelog_path
        self.assertEqual(
                expected_changelog_path, self.test_instance.changelog_path)

    def test_sets_outfile_path_to_default(self):
        """ Should set ‘outfile_path’ attribute to default value. """
        fake_version_info_filename = self.getUniqueString()
        with unittest.mock.patch.object(
                packaging, "version_info_filename",
                new=fake_version_info_filename):
            self.test_instance.finalize_options()
        expected_outfile_path = os.path.join(
                self.fake_egg_dir, fake_version_info_filename)
        self.assertEqual(
                expected_outfile_path, self.test_instance.outfile_path)

    def test_leaves_outfile_path_if_already_set(self):
        """ Should leave ‘outfile_path’ attribute set. """
        prior_outfile_path = self.getUniqueString()
        self.test_instance.outfile_path = prior_outfile_path
        self.test_instance.finalize_options()
        expected_outfile_path = prior_outfile_path
        self.assertEqual(
                expected_outfile_path, self.test_instance.outfile_path)


class has_changelog_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘has_changelog’ function. """

    fake_os_path_exists_side_effects = {
            'true': (lambda path: True),
            'false': (lambda path: False),
            }

    scenarios = [
            ('no changelog path', {
                'changelog_path': None,
                'expected_result': False,
                }),
            ('changelog exists', {
                'os_path_exists_scenario': 'true',
                'expected_result': True,
                }),
            ('changelog not found', {
                'os_path_exists_scenario': 'false',
                'expected_result': False,
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_distribution = setuptools.dist.Distribution()
        self.test_command = packaging.EggInfoCommand(
                self.test_distribution)

        patcher_func_get_changelog_path = unittest.mock.patch.object(
                packaging, "get_changelog_path")
        patcher_func_get_changelog_path.start()
        self.addCleanup(patcher_func_get_changelog_path.stop)

        self.fake_changelog_file_path = self.getUniqueString()
        if hasattr(self, 'changelog_path'):
            self.fake_changelog_file_path = self.changelog_path
        packaging.get_changelog_path.return_value = (
                self.fake_changelog_file_path)
        self.fake_changelog_file = io.StringIO()

        def fake_os_path_exists(path):
            if path == self.fake_changelog_file_path:
                side_effect = self.fake_os_path_exists_side_effects[
                        self.os_path_exists_scenario]
                if callable(side_effect):
                    result = side_effect(path)
                else:
                    raise side_effect
            else:
                result = False
            return result

        func_patcher_os_path_exists = unittest.mock.patch.object(
                os.path, "exists")
        func_patcher_os_path_exists.start()
        self.addCleanup(func_patcher_os_path_exists.stop)
        os.path.exists.side_effect = fake_os_path_exists

    def test_gets_changelog_path_from_distribution(self):
        """ Should call ‘get_changelog_path’ with distribution. """
        packaging.has_changelog(self.test_command)
        packaging.get_changelog_path.assert_called_with(
                self.test_distribution)

    def test_returns_expected_result(self):
        """ Should return the expected result. """
        result = packaging.has_changelog(self.test_command)
        self.assertEqual(self.expected_result, result)


class WriteVersionInfoCommand_run_TestCase(
        WriteVersionInfoCommand_BaseTestCase):
    """ Test cases for ‘WriteVersionInfoCommand.run’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = packaging.WriteVersionInfoCommand(
                self.test_distribution)

        self.fake_changelog_path = self.set_changelog_path(self.test_instance)
        self.fake_outfile_path = self.set_outfile_path(self.test_instance)

        self.patch_version_info()
        self.patch_egg_info_write_file()

    def set_changelog_path(self, instance):
        """ Set the changelog path for the test instance `instance`. """
        self.test_instance.changelog_path = self.getUniqueString()
        return self.test_instance.changelog_path

    def set_outfile_path(self, instance):
        """ Set the outfile path for the test instance `instance`. """
        self.test_instance.outfile_path = self.getUniqueString()
        return self.test_instance.outfile_path

    def patch_version_info(self):
        """ Patch the generation of version info. """
        self.fake_version_info = self.getUniqueString()
        func_patcher = unittest.mock.patch.object(
                packaging, 'generate_version_info_from_changelog',
                return_value=self.fake_version_info)
        self.mock_func_generate_version_info = func_patcher.start()
        self.addCleanup(func_patcher.stop)

        self.fake_version_info_serialised = self.getUniqueString()
        func_patcher = unittest.mock.patch.object(
                packaging, 'serialise_version_info_from_mapping',
                return_value=self.fake_version_info_serialised)
        self.mock_func_serialise_version_info = func_patcher.start()
        self.addCleanup(func_patcher.stop)

    def patch_egg_info_write_file(self):
        """ Patch the command `write_file` method for this test case. """
        func_patcher = unittest.mock.patch.object(
            packaging.WriteVersionInfoCommand, 'write_file')
        self.mock_func_egg_info_write_file = func_patcher.start()
        self.addCleanup(func_patcher.stop)

    def test_returns_none(self):
        """ Should return ``None``. """
        result = self.test_instance.run()
        self.assertIs(result, None)

    def test_generates_version_info_from_changelog(self):
        """ Should generate version info from specified changelog. """
        self.test_instance.run()
        expected_changelog_path = self.test_instance.changelog_path
        self.mock_func_generate_version_info.assert_called_with(
                expected_changelog_path)

    def test_serialises_version_info_from_mapping(self):
        """ Should serialise version info from specified mapping. """
        self.test_instance.run()
        expected_version_info = self.fake_version_info
        self.mock_func_serialise_version_info.assert_called_with(
                expected_version_info)

    def test_writes_file_using_command_context(self):
        """ Should write the metadata file using the command context. """
        self.test_instance.run()
        expected_content = self.fake_version_info_serialised
        self.mock_func_egg_info_write_file.assert_called_with(
                "version info", self.fake_outfile_path, expected_content)


IsSubset = testtools.matchers.MatchesPredicateWithParams(
        set.issubset, "{0} should be a subset of {1}")


class Command_BaseTestCase:
    """ Base for test cases for Setuptools command classes. """

    def test_subclass_of_base_command(self):
        """ Should be a subclass of expected base command class.. """
        self.assertIsInstance(self.test_instance, self.base_command_class)

    def test_sub_commands_include_base_class_sub_commands(self):
        """ Should include base class's sub-commands in this sub_commands. """
        expected_sub_commands = self.base_command_class.sub_commands
        self.assertThat(
                set(expected_sub_commands),
                IsSubset(set(self.test_instance.sub_commands)))


class EggInfoCommand_BaseTestCase(testtools.TestCase):
    """ Base for test cases for class ‘EggInfoCommand’. """

    command_class = packaging.EggInfoCommand
    base_command_class = setuptools.command.egg_info.egg_info

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_distribution = setuptools.dist.Distribution()
        self.test_instance = self.command_class(self.test_distribution)


class EggInfoCommand_TestCase(
        EggInfoCommand_BaseTestCase,
        Command_BaseTestCase):
    """ Test cases for ‘EggInfoCommand’ class. """

    def test_sub_commands_includes_write_version_info_command(self):
        """ Should include sub-command named ‘write_version_info’. """
        commands_by_name = dict(self.test_instance.sub_commands)
        expected_predicate = packaging.has_changelog
        expected_item = ('write_version_info', expected_predicate)
        self.assertIn(expected_item, commands_by_name.items())


@unittest.mock.patch.object(
        setuptools.command.egg_info.egg_info, "run",
        return_value=None,
        )
class EggInfoCommand_run_TestCase(EggInfoCommand_BaseTestCase):
    """ Test cases for ‘EggInfoCommand.run’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        patcher_func_egg_info_get_sub_commands = (
                unittest.mock.patch.object(
                    self.base_command_class, "get_sub_commands"))
        patcher_func_egg_info_get_sub_commands.start()
        self.addCleanup(patcher_func_egg_info_get_sub_commands.stop)

        patcher_func_egg_info_run_command = unittest.mock.patch.object(
                self.base_command_class, "run_command")
        patcher_func_egg_info_run_command.start()
        self.addCleanup(patcher_func_egg_info_run_command.stop)

    def test_returns_none(self, mock_func_egg_info_run):
        """ Should return ``None``. """
        result = self.test_instance.run()
        self.assertIs(result, None)

    def test_calls_base_class_run(self, mock_func_egg_info_run):
        """ Should call base class's ‘run’ method. """
        self.test_instance.run()
        mock_func_egg_info_run.assert_called_with()


class BuildCommand_BaseTestCase(testtools.TestCase):
    """ Base for test cases for class ‘BuildCommand’. """

    command_class = packaging.BuildCommand
    base_command_class = setuptools.command.build.build

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_distribution = setuptools.dist.Distribution()
        self.test_instance = self.command_class(self.test_distribution)


class BuildCommand_TestCase(
        BuildCommand_BaseTestCase,
        Command_BaseTestCase):
    """ Test cases for ‘BuildCommand’ class. """

    def test_sub_commands_includes_egg_info_command(self):
        """ Should include sub-command named ‘egg_info’. """
        commands_by_name = dict(self.test_instance.sub_commands)
        expected_predicate = None
        expected_item = ('egg_info', expected_predicate)
        self.assertIn(expected_item, commands_by_name.items())


@unittest.mock.patch.object(
        setuptools.command.build.build, "run",
        return_value=None,
        )
class BuildCommand_run_TestCase(BuildCommand_BaseTestCase):
    """ Test cases for ‘BuildCommand.run’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        patcher_func_build_get_sub_commands = unittest.mock.patch.object(
                self.base_command_class, "get_sub_commands")
        patcher_func_build_get_sub_commands.start()
        self.addCleanup(patcher_func_build_get_sub_commands.stop)

        patcher_func_build_run_command = unittest.mock.patch.object(
                self.base_command_class, "run_command")
        patcher_func_build_run_command.start()
        self.addCleanup(patcher_func_build_run_command.stop)

    def test_returns_none(self, mock_func_build_run):
        """ Should return ``None``. """
        result = self.test_instance.run()
        self.assertIs(result, None)

    def test_calls_base_class_run(self, mock_func_build_run):
        """ Should call base class's ‘run’ method. """
        self.test_instance.run()
        mock_func_build_run.assert_called_with()


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
