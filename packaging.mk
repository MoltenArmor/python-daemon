# packaging.mk
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for Python packaging.

MODULE_DIR := $(CURDIR)

DESTDIR ?=
PREFIX ?= /usr

PYTHON3 ?= python3
PYTHON ?= ${PYTHON3}

PACKAGING_BUILD_MODULE = build
PACKAGING_BUILD := $(PYTHON) -m ${PACKAGING_BUILD_MODULE}

SETUPTOOLS_CONFIG_MODULE = setup
PACKAGING_SETUP_MODULE_FILE := $(CURDIR)/${SETUPTOOLS_CONFIG_MODULE}.py

CODE_MODULES += ${PACKAGING_SETUP_MODULE_FILE}

GENERATED_FILES += $(CURDIR)/*.egg-info
GENERATED_FILES += $(CURDIR)/.eggs/
GENERATED_FILES += $(CURDIR)/build/
GENERATED_FILES += $(CURDIR)/dist/

GENERATED_FILES += $(CURDIR)/'.tox'
GENERATED_FILES += $(CURDIR)/'.eggs'
GENERATED_FILES += $(shell find $(CURDIR) \
	-type f -name '*.pyc' \( \
		-not -path '*/.tox/*' \
		-not -path '*/.eggs/*' \
	\) )
GENERATED_FILES += $(shell find $(CURDIR) \
	-type d -name '__pycache__' \( \
		-not -path '*/.tox/*' \
		-not -path '*/.eggs/*' \
	\) )


.PHONY: packaging-build
packaging-build:
	$(PACKAGING_BUILD) build

.PHONY: packaging-install
packaging-install:
	$(PACKAGING_BUILD) install ${PACKAGING_INSTALL_OPTS}


.PHONY: packaging-dist
packaging-dist: packaging-sdist packaging-bdist

.PHONY: packaging-bdist
packaging-bdist:
	$(PACKAGING_BUILD) --wheel

.PHONY: packaging-sdist
packaging-sdist:
	$(PACKAGING_BUILD) --sdist


# Copyright © 2006–2023 Ben Finney <ben+python@benfinney.id.au>
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