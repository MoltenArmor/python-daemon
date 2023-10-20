# util/packaging.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Custom packaging functionality for this project.

    This module provides functionality for Setuptools to dynamically derive
    project metadata at build time.

    Requires:

    * Docutils <https://docutils.sourceforge.io/>
    * JSON <https://docs.python.org/3/reference/json.html>
    """

import functools
import os.path
import sys

import setuptools
import setuptools.command.build
import setuptools.command.build_py
import setuptools.command.egg_info
import setuptools.dist

from .metadata import (
    docstring_from_object,
    parse_person_field,
    synopsis_and_description_from_docstring,
)
from .version import (
    generate_version_info_from_changelog,
    serialise_version_info_from_mapping,
)


def main_module_by_name(
        module_name,
        *,
        fromlist=None,
):
    """ Get the main module of this project, named `module_name`.

        :param module_name: The name of the module to import.
        :param fromlist: The list (of `str`) of names of objects to import in
            the module namespace.
        :return: The Python `module` object representing the main module.
        """
    module = __import__(module_name, level=0, fromlist=fromlist)
    return module


changelog_filename = "ChangeLog"


def get_changelog_path(distribution, filename=changelog_filename):
    """ Get the changelog file path for the distribution.

        :param distribution: The setuptools.dist.Distribution instance.
        :param filename: The base filename of the changelog document.
        :return: Filesystem path of the changelog document, or ``None``
            if not discoverable.
        """
    build_py_command = setuptools.command.build_py.build_py(distribution)
    build_py_command.finalize_options()
    setup_dirname = build_py_command.get_package_dir("")
    filepath = os.path.join(setup_dirname, filename)

    return filepath


def has_changelog(command):
    """ Return ``True`` iff the distribution's changelog file exists. """
    result = False

    changelog_path = get_changelog_path(command.distribution)
    if changelog_path is not None:
        if os.path.exists(changelog_path):
            result = True

    return result


class BuildCommand(setuptools.command.build.build):
    """ Custom ‘build’ command for this distribution. """

    sub_commands = (
            setuptools.command.build.build.sub_commands + [
                ('egg_info', None),
            ])


class EggInfoCommand(setuptools.command.egg_info.egg_info):
    """ Custom ‘egg_info’ command for this distribution. """

    sub_commands = ([
            ('write_version_info', has_changelog),
            ] + setuptools.command.egg_info.egg_info.sub_commands)


version_info_filename = "version_info.json"


class WriteVersionInfoCommand(setuptools.command.egg_info.egg_info):
    """ Setuptools command to serialise version info metadata. """

    user_options = ([
            ("changelog-path=", None,
             "Filesystem path to the changelog document."),
            ("outfile-path=", None,
             "Filesystem path to the version info file."),
            ] + setuptools.command.egg_info.egg_info.user_options)

    def initialize_options(self):
        """ Initialise command options to defaults. """
        super().initialize_options()
        self.changelog_path = None
        self.outfile_path = None

    def finalize_options(self):
        """ Finalise command options before execution. """
        self.set_undefined_options(
                'build',
                ('force', 'force'))

        super().finalize_options()

        if self.changelog_path is None:
            self.changelog_path = get_changelog_path(self.distribution)

        if self.outfile_path is None:
            egg_dir = self.egg_info
            self.outfile_path = os.path.join(egg_dir, version_info_filename)

    def run(self):
        """ Execute this command. """
        version_info = generate_version_info_from_changelog(
                self.changelog_path)
        content = serialise_version_info_from_mapping(version_info)
        self.write_file("version info", self.outfile_path, content)


def derive_dist_description(
        distribution,
        *,
        content_type="text/x-rst",
):
    """ Derive description fields for `distribution`, from the main module.

        :param distribution: The `setuptools.dist.Distribution` to inspect and
            modify.
        :param content_type: The MIME Content-Type value to describe the
            content of the long description.
        :return: ``None``.

        Read the main module's docstring, and derive values for metadata
        attributes of `distribution`:

        * `description`: The synopsis (one-line) description from the
          docstring.
        * `long_description: The remainder (separated by a blank line after the
          synopsis) of the docstring content.
        * `long_description_content_type`: Set to `content_type` value.
        """
    main_module = main_module_by_name('daemon')
    main_module_docstring = docstring_from_object(main_module)
    (synopsis, long_description) = synopsis_and_description_from_docstring(
        main_module_docstring)
    distribution.metadata.description = synopsis
    distribution.metadata.long_description = long_description
    distribution.metadata.long_description_content_type = content_type


class ChangelogAwareDistribution(setuptools.dist.Distribution):
    """ A distribution of Python code for installation.

        This class gets the following attributes instead from the
        ‘ChangeLog’ document:

        * version
        * maintainer
        * maintainer_email
        """

    __metaclass__ = type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.script_name is None:
            self.script_name = sys.argv[1]

        # Undo the per-instance delegation for these methods.
        del (
                self.get_version,
                self.get_maintainer,
                self.get_maintainer_email,
                )

    @functools.lru_cache(maxsize=128)
    def get_version_info(self):
        changelog_path = get_changelog_path(self)
        version_info = generate_version_info_from_changelog(changelog_path)
        return version_info

    def get_version(self):
        version_info = self.get_version_info()
        version_string = version_info['version']
        return version_string

    def get_maintainer(self):
        version_info = self.get_version_info()
        person = parse_person_field(version_info['maintainer'])
        return person.name

    def get_maintainer_email(self):
        version_info = self.get_version_info()
        person = parse_person_field(version_info['maintainer'])
        return person.email


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
