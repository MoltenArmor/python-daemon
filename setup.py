# setup.py
# Python Setuptools configuration program for this distribution.
# Documentation: <URL:https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-py>.  # noqa: E501

# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Distribution setup for ‘python-daemon’ library. """

import pathlib
import sys

from setuptools import setup

# This module is not inside a package, so we can't use relative imports. We
# instead add its directory to the import path.
package_root_dir = pathlib.Path(__file__).parent
sys.path.insert(0, str(package_root_dir))
import util.metadata  # noqa: E402
import util.packaging  # noqa: E402


main_module = util.packaging.main_module_by_name(
        'daemon', fromlist=['_metadata'])
metadata = main_module._metadata

changelog_infile_path = package_root_dir.joinpath("ChangeLog")
latest_changelog_entry = util.metadata.get_latest_changelog_entry(
    changelog_infile_path)
(maintainer_name, maintainer_email) = util.metadata.parse_person_field(
    latest_changelog_entry.maintainer)

description_fields = util.metadata.description_fields_from_docstring(
    util.metadata.docstring_from_object(main_module))


test_requirements = [
        "testtools",
        "testscenarios >=0.4",
        "coverage",
        "docutils",
        "changelog-chug",
        ]

build_requirements = [
        "wheel",
        "build",
        "sphinx",
        ] + test_requirements

dist_requirements = [
        "twine",
        ] + build_requirements

devel_requirements = [
        "isort",
        ] + dist_requirements


setup_kwargs = dict(
        version=latest_changelog_entry.version,

        # Setuptools metadata.
        setup_requires=build_requirements,
        install_requires=[
            "setuptools >=62.4.0",
            "lockfile >=0.10",
            ],
        extras_require={
            'test': test_requirements,
            'build': build_requirements,
            'dist': dist_requirements,
            'devel': devel_requirements,
            },

        # PyPI metadata.
        description=description_fields.synopsis,
        long_description=description_fields.long_description,
        long_description_content_type=description_fields.content_type,
        author=metadata.author_name,
        author_email=metadata.author_email,
        maintainer=maintainer_name,
        maintainer_email=maintainer_email,
        license=metadata.license,
        )

# Docutils is only required for building, but Setuptools can't distinguish
# dependencies properly.
# See <URL:https://github.com/pypa/setuptools/issues/457>.
setup_kwargs['install_requires'].append("docutils")


if __name__ == '__main__':  # pragma: nocover
    setup(**setup_kwargs)


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
