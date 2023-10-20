# daemon/_metadata.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Package metadata for the ‘python-daemon’ distribution. """

import json

import pkg_resources


distribution_name = "python-daemon"
version_info_filename = "version_info.json"


def get_distribution(name):
    """ Get the `Distribution` instance for distribution `name`.

        :param name: The distribution name for the query.
        :return: The `pkg_resources.Distribution` instance, or
            ``None`` if the distribution instance is not found.
        """
    distribution = None
    try:
        distribution = pkg_resources.get_distribution(name)
    except pkg_resources.DistributionNotFound:
        pass

    return distribution


def get_distribution_version_info(
        distribution, filename=version_info_filename):
    """ Get the version info from the installed distribution.

        :param distribution: The `pkg_resources.Distribution` instance
            representing the Python package to interrogate.
        :param filename: Base filename of the version info resource.
        :return: The version info as a mapping of fields.

        The version info is stored as a metadata file in the
        `distribution`.

        If the `distribution` is ``None``, or the version info
        metadata file is not found, the return value mapping fields
        have placeholder values.
        """
    version_info = {
            'release_date': "UNKNOWN",
            'version': "UNKNOWN",
            'maintainer': "UNKNOWN",
            }

    if distribution is not None:
        if distribution.has_metadata(filename):
            content = distribution.get_metadata(filename)
            version_info = json.loads(content)

    return version_info


distribution = get_distribution(distribution_name)
version_info = get_distribution_version_info(distribution)

version_installed = version_info['version']


author_name = "Ben Finney"
author_email = "ben+python@benfinney.id.au"
author = "{name} <{email}>".format(name=author_name, email=author_email)

license = "Apache-2"
url = "https://pagure.io/python-daemon/"


# Copyright © 2008–2023 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Apache License, version 2.0 as published by the
# Apache Software Foundation.
# No warranty expressed or implied. See the file ‘LICENSE.ASF-2’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
