# test/scaffold.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Scaffolding for unit test modules. """

import builtins
from copy import deepcopy
import doctest
import functools
import logging
import operator
import textwrap
import unittest.mock

import testscenarios
import testtools.testcase


# Disable all but the most critical logging messages.
logging.disable(logging.CRITICAL)


def get_function_signature(func):
    """ Get the function signature as a mapping of attributes.

        :param func: The function object to interrogate.
        :return: A mapping of the components of a function signature.

        The signature is constructed as a mapping:

        * 'name': The function's defined name.
        * 'arg_count': The number of arguments expected by the function.
        * 'arg_names': A sequence of the argument names, as strings.
        * 'arg_defaults': A sequence of the default values for the arguments.
        * 'var_args': The name bound to remaining positional arguments.
        * 'var_kw_args': The name bound to remaining keyword arguments.
        """
    func_code = func.__code__
    func_defaults = func.__defaults__

    arg_count = func_code.co_argcount
    arg_names = func_code.co_varnames[:arg_count]

    arg_defaults = {}
    if func_defaults is not None:
        arg_defaults = {
                name: value
                for (name, value) in (
                    zip(arg_names[::-1], func_defaults[::-1]))
                }

    signature = {
            'name': func.__name__,
            'arg_count': arg_count,
            'arg_names': arg_names,
            'arg_defaults': arg_defaults,
            }

    non_pos_names = list(func_code.co_varnames[arg_count:])
    COLLECTS_ARBITRARY_POSITIONAL_ARGS = 0x04
    if func_code.co_flags & COLLECTS_ARBITRARY_POSITIONAL_ARGS:
        signature['var_args'] = non_pos_names.pop(0)
    COLLECTS_ARBITRARY_KEYWORD_ARGS = 0x08
    if func_code.co_flags & COLLECTS_ARBITRARY_KEYWORD_ARGS:
        signature['var_kw_args'] = non_pos_names.pop(0)

    return signature


def format_function_signature(func):
    """ Format the function signature as printable text.

        :param func: The function object to interrogate.
        :return: A formatted text representation of the function signature.

        The signature is rendered as text; for example::

            foo(spam, eggs, ham=True, beans=None, *args, **kwargs)
        """
    signature = get_function_signature(func)

    args_text = []
    for arg_name in signature['arg_names']:
        if arg_name in signature['arg_defaults']:
            arg_text = "{name}={value!r}".format(
                    name=arg_name, value=signature['arg_defaults'][arg_name])
        else:
            arg_text = "{name}".format(
                    name=arg_name)
        args_text.append(arg_text)
    if 'var_args' in signature:
        args_text.append("*{var_args}".format(signature))
    if 'var_kw_args' in signature:
        args_text.append("**{var_kw_args}".format(signature))
    signature_args_text = ", ".join(args_text)

    func_name = signature['name']
    signature_text = "{name}({args})".format(
            name=func_name, args=signature_args_text)

    return signature_text


class TestCase(testtools.testcase.TestCase):
    """ Test case behaviour. """

    def failUnlessOutputCheckerMatch(self, want, got, msg=None):
        """ Fail unless the specified string matches the expected.

            :param want: The desired output pattern.
            :param got: The actual text to match.
            :param msg: A message to prefix on the failure message.
            :return: ``None``.
            :raises self.failureException: If the text does not match.

            Fail the test unless ``want`` matches ``got``, as determined by
            a ``doctest.OutputChecker`` instance. This is not an equality
            check, but a pattern match according to the ``OutputChecker``
            rules.
            """
        checker = doctest.OutputChecker()
        want = textwrap.dedent(want)
        source = ""
        example = doctest.Example(source, want)
        got = textwrap.dedent(got)
        checker_optionflags = functools.reduce(operator.or_, [
                doctest.ELLIPSIS,
                ])
        if not checker.check_output(want, got, checker_optionflags):
            if msg is None:
                diff = checker.output_difference(
                        example, got, checker_optionflags)
                msg = "\n".join([
                        "Output received did not match expected output",
                        "{diff}",
                        ]).format(
                            diff=diff)
            raise self.failureException(msg)

    assertOutputCheckerMatch = failUnlessOutputCheckerMatch

    def failUnlessFunctionInTraceback(self, traceback, function, msg=None):
        """ Fail if the function is not in the traceback.

            :param traceback: The traceback object to interrogate.
            :param function: The function object to match.
            :param msg: A message to prefix on the failure message.
            :return: ``None``.

            :raises self.failureException: If the function is not in the
                traceback.

            Fail the test if the function ``function`` is not at any of the
            levels in the traceback object ``traceback``.
            """
        func_in_traceback = False
        expected_code = function.func_code
        current_traceback = traceback
        while current_traceback is not None:
            if expected_code is current_traceback.tb_frame.f_code:
                func_in_traceback = True
                break
            current_traceback = current_traceback.tb_next

        if not func_in_traceback:
            if msg is None:
                msg = (
                        "Traceback did not lead to original function"
                        " {function}"
                        ).format(
                            function=function)
            raise self.failureException(msg)

    assertFunctionInTraceback = failUnlessFunctionInTraceback

    def failUnlessFunctionSignatureMatch(self, first, second, msg=None):
        """ Fail if the function signatures do not match.

            :param first: The first function to compare.
            :param second: The second function to compare.
            :param msg: A message to prefix to the failure message.
            :return: ``None``.

            :raises self.failureException: If the function signatures do
                not match.

            Fail the test if the function signature does not match between
            the ``first`` function and the ``second`` function.

            The function signature includes:

            * function name,

            * count of named parameters,

            * sequence of named parameters,

            * default values of named parameters,

            * collector for arbitrary positional arguments,

            * collector for arbitrary keyword arguments.
            """
        first_signature = get_function_signature(first)
        second_signature = get_function_signature(second)

        if first_signature != second_signature:
            if msg is None:
                first_signature_text = format_function_signature(first)
                second_signature_text = format_function_signature(second)
                msg = (textwrap.dedent("""\
                        Function signatures do not match:
                            {first!r} != {second!r}
                        Expected:
                            {first_text}
                        Got:
                            {second_text}
                        """)).format(
                            first=first_signature,
                            first_text=first_signature_text,
                            second=second_signature,
                            second_text=second_signature_text,
                            )
            raise self.failureException(msg)

    assertFunctionSignatureMatch = failUnlessFunctionSignatureMatch


class TestCaseWithScenarios(testscenarios.WithScenarios, TestCase):
    """ Test cases run per scenario. """


class Exception_TestCase(TestCaseWithScenarios):
    """ Test cases for exception classes. """

    def test_exception_instance(self):
        """ Exception instance should be created. """
        self.assertIsNot(self.instance, None)

    def test_exception_types(self):
        """ Exception instance should match expected types. """
        for match_type in self.types:
            self.assertIsInstance(self.instance, match_type)


def make_exception_scenarios(scenarios):
    """ Make test scenarios for exception classes.

        :param scenarios: Sequence of scenarios.
        :return: List of scenarios with additional mapping entries.

        Use this with `testscenarios` to adapt `Exception_TestCase`_ for
        any exceptions that need testing.

        Each scenario is a tuple (`name`, `map`) where `map` is a mapping
        of attributes to be applied to each test case. Attributes map must
        contain items for:

            :key exc_type:
                The exception type to be tested.
            :key min_args:
                The minimum argument count for the exception instance
                initialiser.
            :key types:
                Sequence of types that should be superclasses of each
                instance of the exception type.
        """
    updated_scenarios = deepcopy(scenarios)
    for (name, scenario) in updated_scenarios:
        args = (None,) * scenario['min_args']
        scenario['args'] = args
        instance = scenario['exc_type'](*args)
        scenario['instance'] = instance

    return updated_scenarios


def mock_builtin_open_for_fake_files(testcase, *, fake_file_content_by_path):
    """ Mock builtin `open` during `testcase`, for specific fake files.

        :param testcase: The test case during which to mock `open`.
        :param fake_file_content_by_path: Mapping of
            `{file_path: fake_file_content}`.

        Create fake files (`io.StringIO`) containing each `fake_file_content`.
        Wrap the `builtins.open` function such that, for the specified
        `file_path` only, a specific mock `open` function will be called,
        that returns the corresponding fake file; for any unspecified path,
        the original `builtins.open` will be called as normal.
        """
    testcase.mock_open_by_path = {
        file_path: unittest.mock.mock_open(read_data=fake_file_content)
        for (file_path, fake_file_content)
        in fake_file_content_by_path.items()}

    open_orig = builtins.open

    def fake_open(file, *args, **kwargs):
        """ Wrapper for builtin `open`, faking for specific paths. """
        open_func = (
            testcase.mock_open_by_path[file]
            if file in testcase.mock_open_by_path
            else open_orig)
        return open_func(file, *args, **kwargs)

    testcase.open_patcher = unittest.mock.patch.object(
        builtins, 'open', side_effect=fake_open)
    testcase.open_patcher.start()
    testcase.addCleanup(testcase.open_patcher.stop)


# Copyright © 2007–2024 Ben Finney <ben+python@benfinney.id.au>
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
