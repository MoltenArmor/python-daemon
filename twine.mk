# twine.mk
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for PyPI Twine.

MODULE_DIR := $(CURDIR)

RELEASE_PYPI_REPOSITORY_NAME ?= testpypi

PYTHON_TWINE ?= $(PYTHON3) -m twine
PYTHON_TWINE_UPLOAD_OPTS ?= \
	--repository ${RELEASE_PYPI_REPOSITORY_NAME} \
	--non-interactive

PYTHON_TWINE_CHECK_OPTS ?= --strict

TWINE_DIST_FILES ?= ${DIST_DIR}/*


.PHONY: twine-upload
twine-upload: pip-confirm-dist-dependencies-installed
twine-upload: packaging-dist
	$(PYTHON_TWINE) upload ${PYTHON_TWINE_UPLOAD_OPTS} ${TWINE_DIST_FILES}


.PHONY: twine-check
twine-check: pip-confirm-dist-dependencies-installed
twine-check: packaging-dist
	$(PYTHON_TWINE) check ${PYTHON_TWINE_CHECK_OPTS} ${TWINE_DIST_FILES}


# Copyright © 2006–2024 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local Variables:
# mode: makefile
# coding: utf-8
# End:
# vim: fileencoding=utf-8 filetype=make :
