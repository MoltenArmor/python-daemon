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
PACKAGING_BUILD_OPTS ?=

SETUPTOOLS_CONFIG_MODULE = setup
PACKAGING_SETUP_MODULE_FILE := $(CURDIR)/${SETUPTOOLS_CONFIG_MODULE}.py

CODE_MODULES += ${PACKAGING_SETUP_MODULE_FILE}

PIP_INSTALL_OPTS ?= --no-input
PIP_TEST_DEPENDENCIES = .[test]
PIP_TEST_DEPENDENCIES_EXPLICIT = \
	lockfile \
	coverage testscenarios testtools
PIP_DEVEL_DEPENDENCIES = .[devel]
PIP_DEVEL_DEPENDENCIES_EXPLICIT = \
	${PIP_TEST_DEPENDENCIES_EXPLICIT} \
	sphinx docutils packaging setuptools wheel

installed_packages = $(shell \
	$(PYTHON) -m pip list \
		| tail --lines +2 \
		| cut -d ' ' -f 1)

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


define exit_with_error_if_packages_not_installed =
	not_installed_packages="$(strip \
		$(filter-out ${installed_packages},${1}))" ; \
	if [[ -n "$${not_installed_packages}" ]] ; then \
		echo "Dependency packages not installed:" \
			"$${not_installed_packages}" ; \
		/bin/false ; \
	fi
endef


.PHONY: pip-confirm-devel-dependencies-installed
pip-confirm-devel-dependencies-installed:
	@$(call exit_with_error_if_packages_not_installed, \
		${PIP_DEVEL_DEPENDENCIES_EXPLICIT})

.PHONY: pip-install-devel-dependencies
pip-install-devel-dependencies:
	$(PYTHON) -m pip install \
		${PIP_INSTALL_OPTS} \
		${PIP_DEVEL_DEPENDENCIES}


.PHONY: pip-confirm-test-dependencies-installed
pip-confirm-test-dependencies-installed:
	@$(call exit_with_error_if_packages_not_installed, \
		${PIP_TEST_DEPENDENCIES_EXPLICIT})

.PHONY: pip-install-test-dependencies
pip-install-test-dependencies:
	$(PYTHON) -m pip install \
		${PIP_INSTALL_OPTS} \
		${PIP_TEST_DEPENDENCIES}


.PHONY: packaging-build
packaging-build: packaging-dist


.PHONY: packaging-dist
packaging-dist:
	$(PACKAGING_BUILD) ${PACKAGING_BUILD_OPTS} --sdist --wheel

.PHONY: packaging-bdist
packaging-bdist:
	$(PACKAGING_BUILD) ${PACKAGING_BUILD_OPTS} --wheel

.PHONY: packaging-sdist
packaging-sdist:
	$(PACKAGING_BUILD) ${PACKAGING_BUILD_OPTS} --sdist


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
