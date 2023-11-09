#! /usr/bin/make -f
#
# Makefile
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile for this project.

SHELL = /bin/bash
PATH = /usr/bin:/bin

# Variables that will be extended by module include files.
GENERATED_FILES :=
CODE_MODULES :=
TEST_MODULES :=
CODE_PROGRAMS :=

# Directories with semantic meaning.
CODE_PACKAGE_DIRS := daemon
DOC_DIR := doc
BUILD_DIR = $(CURDIR)/build
DIST_DIR = $(CURDIR)/dist

GENERATED_FILES += ${BUILD_DIR}/
GENERATED_FILES += ${DIST_DIR}/

# List of modules (directories) that comprise our ‘make’ project.
MODULES := ${CODE_PACKAGE_DIRS}
MODULES += ${DOC_DIR}


# Establish the default goal.
.PHONY: all
all:

# Include the make data for each module.
include $(patsubst %,%/module.mk,${MODULES})


all: build

.PHONY: build
build:

.PHONY: dist
dist:

.PHONY: install
install: build


include packaging.mk

build: packaging-build

install: packaging-install

.PHONY: bdist
bdist: packaging-bdist

.PHONY: sdist
sdist: packaging-sdist

.PHONY: dist
dist: packaging-dist


include test.mk


include twine.mk

.PHONY: publish
publish: twine-check twine-upload

test: twine-check


.PHONY: clean
clean:
	$(RM) -r ${GENERATED_FILES}


# Copyright © 2006–2023 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local Variables:
# coding: utf-8
# mode: makefile
# End:
# vim: fileencoding=utf-8 filetype=make :
