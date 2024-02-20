# test/test_util_version.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.version’ packaging module. """

import collections
import functools
import io
import json
import tempfile
import textwrap
import unittest.mock

import docutils
import docutils.nodes
import docutils.writers
from packaging.version import InvalidVersion
import testscenarios
import testtools

from util import version


version.ensure_class_bases_begin_with(
        version.__dict__, 'VersionInfoWriter', docutils.writers.Writer)
version.ensure_class_bases_begin_with(
        version.__dict__, 'VersionInfoTranslator',
        docutils.nodes.SparseNodeVisitor)


def make_test_classes_for_ensure_class_bases_begin_with():
    """ Make test classes for use with ‘ensure_class_bases_begin_with’.

        :return: Mapping {`name`: `type`} of the custom types created.
        """

    class quux_metaclass(type):
        def __new__(metaclass, name, bases, namespace):
            return super().__new__(
                    metaclass, name, bases, namespace)

    class Foo:
        __metaclass__ = type

    class Bar:
        pass

    class FooInheritingBar(Bar):
        __metaclass__ = type

    class FooWithCustomMetaclass:
        __metaclass__ = quux_metaclass

    result = {
            name: value for (name, value) in locals().items()
            if isinstance(value, type)}

    return result


class ensure_class_bases_begin_with_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘ensure_class_bases_begin_with’ function. """

    test_classes = make_test_classes_for_ensure_class_bases_begin_with()

    scenarios = [
            ('simple', {
                'test_class': test_classes['Foo'],
                'base_class': test_classes['Bar'],
                }),
            ('custom metaclass', {
                'test_class': test_classes['FooWithCustomMetaclass'],
                'base_class': test_classes['Bar'],
                'expected_metaclass': test_classes['quux_metaclass'],
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.class_name = self.test_class.__name__
        self.test_module_namespace = {self.class_name: self.test_class}

        if not hasattr(self, 'expected_metaclass'):
            self.expected_metaclass = type

        patcher_metaclass = unittest.mock.patch.object(
            self.test_class, '__metaclass__')
        patcher_metaclass.start()
        self.addCleanup(patcher_metaclass.stop)

        self.fake_new_class = type(object)
        self.test_class.__metaclass__.return_value = (
                self.fake_new_class)

    def test_module_namespace_contains_new_class(self):
        """ Specified module namespace should have new class. """
        version.ensure_class_bases_begin_with(
                self.test_module_namespace, self.class_name, self.base_class)
        self.assertIn(self.fake_new_class, self.test_module_namespace.values())

    def test_calls_metaclass_with_expected_class_name(self):
        """ Should call the metaclass with the expected class name. """
        version.ensure_class_bases_begin_with(
                self.test_module_namespace, self.class_name, self.base_class)
        expected_class_name = self.class_name
        self.test_class.__metaclass__.assert_called_with(
                expected_class_name, unittest.mock.ANY, unittest.mock.ANY)

    def test_calls_metaclass_with_expected_bases(self):
        """ Should call the metaclass with the expected bases. """
        version.ensure_class_bases_begin_with(
                self.test_module_namespace, self.class_name, self.base_class)
        expected_bases = tuple(
                [self.base_class]
                + list(self.test_class.__bases__))
        self.test_class.__metaclass__.assert_called_with(
                unittest.mock.ANY, expected_bases, unittest.mock.ANY)

    def test_calls_metaclass_with_expected_namespace(self):
        """ Should call the metaclass with the expected class namespace. """
        version.ensure_class_bases_begin_with(
                self.test_module_namespace, self.class_name, self.base_class)
        expected_namespace = self.test_class.__dict__.copy()
        del expected_namespace['__dict__']
        self.test_class.__metaclass__.assert_called_with(
                unittest.mock.ANY, unittest.mock.ANY, expected_namespace)


class ensure_class_bases_begin_with_AlreadyHasBase_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘ensure_class_bases_begin_with’ function.

        These test cases test the conditions where the class's base is
        already the specified base class.
        """

    test_classes = make_test_classes_for_ensure_class_bases_begin_with()

    scenarios = [
            ('already Bar subclass', {
                'test_class': test_classes['FooInheritingBar'],
                'base_class': test_classes['Bar'],
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.class_name = self.test_class.__name__
        self.test_module_namespace = {self.class_name: self.test_class}

        patcher_metaclass = unittest.mock.patch.object(
            self.test_class, '__metaclass__')
        patcher_metaclass.start()
        self.addCleanup(patcher_metaclass.stop)

    def test_metaclass_not_called(self):
        """ Should not call metaclass to create a new type. """
        version.ensure_class_bases_begin_with(
                self.test_module_namespace, self.class_name, self.base_class)
        self.assertFalse(self.test_class.__metaclass__.called)


class FakeNode:
    """ A fake instance of a `Node` of a document. """

    def __init__(self, source=None, line=None):
        self.source = source
        self.line = line


class InvalidFormatError_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for class `InvalidFormatError`. """

    message_scenarios = [
            ('message-specified', {
                'test_message': "Lorem ipsum, dolor sit amet.",
                'expected_message': "Lorem ipsum, dolor sit amet.",
                'expected_message_text': "Lorem ipsum, dolor sit amet.",
                }),
            ('message-unspecified', {
                'test_message': NotImplemented,
                'expected_message': None,
                'expected_message_text': "(no message)",
                }),
            ]

    node_scenarios = [
            ('node-with-source-and-line', {
                'test_node': FakeNode(source="consecteur", line=17),
                'expected_node_source_text': "consecteur",
                'expected_node_text': "consecteur line 17",
                }),
            ('node-with-source-only', {
                'test_node': FakeNode(source="consecteur"),
                'expected_node_source_text': "consecteur",
                'expected_node_text': "consecteur line (unknown)",
                }),
            ('node-with-line-only', {
                'test_node': FakeNode(line=17),
                'expected_node_source_text': "(source unknown)",
                'expected_node_text': "(source unknown) line 17",
                }),
            ]

    scenarios = testscenarios.multiply_scenarios(
            message_scenarios, node_scenarios)

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_kwargs = {}
        self.test_kwargs['node'] = self.test_node
        if (self.test_message is not NotImplemented):
            self.test_kwargs['message'] = self.test_message

    def test_has_specified_node(self):
        """ Should have specified `node` value. """
        test_instance = version.InvalidFormatError(**self.test_kwargs)
        expected_node = self.test_kwargs['node']
        self.assertEqual(expected_node, test_instance.node)

    def test_has_specified_message(self):
        """ Should have specified `message` value. """
        test_instance = version.InvalidFormatError(**self.test_kwargs)
        self.assertEqual(self.expected_message, test_instance.message)

    def test_str_contains_expected_message_text(self):
        """ Should have `str` containing expected message text. """
        test_instance = version.InvalidFormatError(**self.test_kwargs)
        text = str(test_instance)
        self.assertIn(self.expected_message_text, text)

    def test_str_contains_expected_node_text(self):
        """ Should have `str` containing expected node text. """
        test_instance = version.InvalidFormatError(**self.test_kwargs)
        text = str(test_instance)
        self.assertIn(self.expected_node_text, text)


class VersionInfoWriter_TestCase(testtools.TestCase):
    """ Test cases for ‘VersionInfoWriter’ class. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = version.VersionInfoWriter()

    def test_declares_version_info_support(self):
        """ Should declare support for ‘version_info’. """
        instance = self.test_instance
        expected_support = "version_info"
        result = instance.supports(expected_support)
        self.assertTrue(result)


class VersionInfoWriter_translate_TestCase(testtools.TestCase):
    """ Test cases for ‘VersionInfoWriter.translate’ method. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        patcher_translator = unittest.mock.patch.object(
                version, 'VersionInfoTranslator')
        self.mock_class_translator = patcher_translator.start()
        self.addCleanup(patcher_translator.stop)
        self.mock_translator = self.mock_class_translator.return_value

        self.test_instance = version.VersionInfoWriter()
        patcher_document = unittest.mock.patch.object(
                self.test_instance, 'document')
        patcher_document.start()
        self.addCleanup(patcher_document.stop)

    def test_creates_translator_with_document(self):
        """ Should create a translator with the writer's document. """
        instance = self.test_instance
        expected_document = self.test_instance.document
        instance.translate()
        self.mock_class_translator.assert_called_with(expected_document)

    def test_calls_document_walkabout_with_translator(self):
        """ Should call document.walkabout with the translator. """
        instance = self.test_instance
        instance.translate()
        instance.document.walkabout.assert_called_with(self.mock_translator)

    def test_output_from_translator_astext(self):
        """ Should have output from translator.astext(). """
        instance = self.test_instance
        instance.translate()
        expected_output = self.mock_translator.astext.return_value
        self.assertEqual(expected_output, instance.output)


class NoOpContextManager:
    """ A context manager with no effect. """

    def __enter__(self): pass

    def __exit__(self, exc_type, exc_value, traceback): pass


class ChangeLogEntry_BaseTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Base class for ‘ChangeLogEntry’ test case classes. """

    def expected_error_context(self):
        """ Make a context manager to expect the nominated error. """
        context = NoOpContextManager()
        if hasattr(self, 'expected_error'):
            context = testtools.ExpectedException(self.expected_error)
        return context


class ChangeLogEntry_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry’ class. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = version.ChangeLogEntry()

    def test_instantiate(self):
        """ New instance of ‘ChangeLogEntry’ should be created. """
        self.assertIsInstance(
                self.test_instance, version.ChangeLogEntry)

    def test_minimum_zero_arguments(self):
        """ Initialiser should not require any arguments. """
        instance = version.ChangeLogEntry()
        self.assertIsNot(instance, None)


class ChangeLogEntry_release_date_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.release_date’ attribute. """

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_release_date':
                    version.ChangeLogEntry.default_release_date,
                }),
            ('unknown token', {
                'test_args': {'release_date': "UNKNOWN"},
                'expected_release_date': "UNKNOWN",
                }),
            ('future token', {
                'test_args': {'release_date': "FUTURE"},
                'expected_release_date': "FUTURE",
                }),
            ('2001-01-01', {
                'test_args': {'release_date': "2001-01-01"},
                'expected_release_date': "2001-01-01",
                }),
            ('bogus', {
                'test_args': {'release_date': "b0gUs"},
                'expected_error': ValueError,
                }),
            ]

    def test_has_expected_release_date(self):
        """ Should have default `release_date` attribute. """
        with self.expected_error_context():
            instance = version.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_release_date'):
            self.assertEqual(self.expected_release_date, instance.release_date)


class ChangeLogEntry_version_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.version’ attribute. """

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_version':
                    version.ChangeLogEntry.default_version,
                }),
            ('unknown token', {
                'test_args': {'version': "UNKNOWN"},
                'expected_version': "UNKNOWN",
                }),
            ('next token', {
                'test_args': {'version': "NEXT"},
                'expected_version': "NEXT",
                }),
            ('0.0', {
                'test_args': {'version': "0.0"},
                'expected_version': "0.0",
                }),
            ('1.2.3', {
                'test_args': {'version': "1.2.3"},
                'expected_version': "1.2.3",
                }),
            ('1.23.456', {
                'test_args': {'version': "1.23.456"},
                'expected_version': "1.23.456",
                }),
            ('1.23.456a5', {
                'test_args': {'version': "1.23.456a5"},
                'expected_version': "1.23.456a5",
                }),
            ('123.456.789', {
                'test_args': {'version': "123.456.789"},
                'expected_version': "123.456.789",
                }),
            ('non-number', {
                'test_args': {'version': "b0gUs"},
                'expected_error': InvalidVersion,
                }),
            ('negative', {
                'test_args': {'version': "-1.0"},
                'expected_error': InvalidVersion,
                }),
            ('non-number parts', {
                'test_args': {'version': "1.b0gUs.0"},
                'expected_error': InvalidVersion,
                }),
            ]

    def test_has_expected_version(self):
        """ Should have default `version` attribute. """
        with self.expected_error_context():
            instance = version.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_version'):
            self.assertEqual(self.expected_version, instance.version)


class ChangeLogEntry_maintainer_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.maintainer’ attribute. """

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_maintainer': None,
                }),
            ('person', {
                'test_args': {'maintainer': "Foo Bar <foo.bar@example.org>"},
                'expected_maintainer': "Foo Bar <foo.bar@example.org>",
                }),
            ('bogus', {
                'test_args': {'maintainer': "b0gUs"},
                'expected_error': ValueError,
                }),
            ]

    def test_has_expected_maintainer(self):
        """ Should have default `maintainer` attribute. """
        with self.expected_error_context():
            instance = version.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_maintainer'):
            self.assertEqual(self.expected_maintainer, instance.maintainer)


class ChangeLogEntry_body_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.body’ attribute. """

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_body': None,
                }),
            ('simple', {
                'test_args': {'body': "Foo bar baz."},
                'expected_body': "Foo bar baz.",
                }),
            ]

    def test_has_expected_body(self):
        """ Should have default `body` attribute. """
        instance = version.ChangeLogEntry(**self.test_args)
        self.assertEqual(self.expected_body, instance.body)


class ChangeLogEntry_as_version_info_entry_TestCase(
        ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.as_version_info_entry’ attribute. """

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_result': collections.OrderedDict([
                    (
                        'release_date',
                        version.ChangeLogEntry.default_release_date),
                    ('version', version.ChangeLogEntry.default_version),
                    ('maintainer', None),
                    ('body', None),
                    ]),
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = version.ChangeLogEntry(**self.test_args)

    def test_returns_result(self):
        """ Should return expected result. """
        result = self.test_instance.as_version_info_entry()
        self.assertEqual(self.expected_result, result)


def make_mock_field_node(field_name, field_body):
    """ Make a mock Docutils field node for tests. """

    mock_field_node = unittest.mock.MagicMock(
            name='field', spec=docutils.nodes.field)

    mock_field_name_node = unittest.mock.MagicMock(
            name='field_name', spec=docutils.nodes.field_name)
    mock_field_name_node.parent = mock_field_node
    mock_field_name_node.children = [field_name]

    mock_field_body_node = unittest.mock.MagicMock(
            name='field_body', spec=docutils.nodes.field_body)
    mock_field_body_node.parent = mock_field_node
    mock_field_body_node.children = [field_body]

    mock_field_node.children = [mock_field_name_node, mock_field_body_node]

    def fake_func_first_child_matching_class(node_class):
        result = None
        node_class_name = node_class.__name__
        for (index, node) in enumerate(mock_field_node.children):
            if node._mock_name == node_class_name:
                result = index
                break
        return result

    mock_field_node.first_child_matching_class.side_effect = (
            fake_func_first_child_matching_class)

    return mock_field_node


class JsonEqual(testtools.matchers.Matcher):
    """ A matcher to compare the value of JSON streams. """

    def __init__(self, expected):
        self.expected_value = expected

    def match(self, content):
        """ Assert the JSON `content` matches the `expected_content`. """
        result = None
        actual_value = json.loads(content.decode('utf-8'))
        if actual_value != self.expected_value:
            result = JsonValueMismatch(self.expected_value, actual_value)
        return result


class JsonValueMismatch(testtools.matchers.Mismatch):
    """ The specified JSON stream does not evaluate to the expected value. """

    def __init__(self, expected, actual):
        self.expected_value = expected
        self.actual_value = actual

    def describe(self):
        """ Emit a text description of this mismatch. """
        expected_json_text = json.dumps(self.expected_value, indent=4)
        actual_json_text = json.dumps(self.actual_value, indent=4)
        text = (
                "\n"
                "reference: {expected}\n"
                "actual: {actual}\n").format(
                    expected=expected_json_text, actual=actual_json_text)
        return text


class changelog_to_version_info_collection_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘changelog_to_version_info_collection’ function. """

    scenarios = [
            ('single entry', {
                'test_input': textwrap.dedent("""\
                    Version 1.0
                    ===========

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_version_info': [
                    {
                        'release_date': "2009-01-01",
                        'version': "1.0",
                        'maintainer': "Foo Bar <foo.bar@example.org>",
                        'body': "* Lorem ipsum dolor sit amet.\n",
                        },
                    ],
                }),
            ('multiple entries', {
                'test_input': textwrap.dedent("""\
                    Version 1.0
                    ===========

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.


                    Version 0.8
                    ===========

                    :Released: 2004-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Donec venenatis nisl aliquam ipsum.


                    Version 0.7.2
                    =============

                    :Released: 2001-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Pellentesque elementum mollis finibus.
                    """),
                'expected_version_info': [
                    {
                        'release_date': "2009-01-01",
                        'version': "1.0",
                        'maintainer': "Foo Bar <foo.bar@example.org>",
                        'body': "* Lorem ipsum dolor sit amet.\n",
                        },
                    {
                        'release_date': "2004-01-01",
                        'version': "0.8",
                        'maintainer': "Foo Bar <foo.bar@example.org>",
                        'body': "* Donec venenatis nisl aliquam ipsum.\n",
                        },
                    {
                        'release_date': "2001-01-01",
                        'version': "0.7.2",
                        'maintainer': "Foo Bar <foo.bar@example.org>",
                        'body': "* Pellentesque elementum mollis finibus.\n",
                        },
                    ],
                }),
            ('trailing comment', {
                'test_input': textwrap.dedent("""\
                    Version NEXT
                    ============

                    :Released: FUTURE
                    :Maintainer:

                    * Lorem ipsum dolor sit amet.

                    ..
                        Vivamus aliquam felis rutrum rutrum dictum.
                    """),
                'expected_version_info': [
                    {
                        'release_date': "FUTURE",
                        'version': "NEXT",
                        'maintainer': "",
                        'body': "* Lorem ipsum dolor sit amet.\n",
                        },
                    ],
                }),
            ('inline comment', {
                'test_input': textwrap.dedent("""\
                    Version NEXT
                    ============

                    :Released: FUTURE
                    :Maintainer:

                    ..
                        Vivamus aliquam felis rutrum rutrum dictum.

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_version_info': [
                    {
                        'release_date': "FUTURE",
                        'version': "NEXT",
                        'maintainer': "",
                        'body': "* Lorem ipsum dolor sit amet.\n",
                        },
                    ],
                }),
            ('unreleased entry', {
                'test_input': textwrap.dedent("""\
                    Version NEXT
                    ============

                    :Released: FUTURE
                    :Maintainer:

                    * Lorem ipsum dolor sit amet.


                    Version 0.8
                    ===========

                    :Released: 2001-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Donec venenatis nisl aliquam ipsum.
                    """),
                'expected_version_info': [
                    {
                        'release_date': "FUTURE",
                        'version': "NEXT",
                        'maintainer': "",
                        'body': "* Lorem ipsum dolor sit amet.\n",
                        },
                    {
                        'release_date': "2001-01-01",
                        'version': "0.8",
                        'maintainer': "Foo Bar <foo.bar@example.org>",
                        'body': "* Donec venenatis nisl aliquam ipsum.\n",
                        },
                    ],
                }),
            ('no section', {
                'test_input': textwrap.dedent("""\
                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_error': version.InvalidFormatError,
                }),
            ('subsection', {
                'test_input': textwrap.dedent("""\
                    Version 1.0
                    ===========

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.

                    Ut ultricies fermentum quam
                    ---------------------------

                    * In commodo magna facilisis in.
                    """),
                'expected_error': version.InvalidFormatError,
                'subsection': True,
                }),
            ('unknown field', {
                'test_input': textwrap.dedent("""\
                    Version 1.0
                    ===========

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>
                    :Favourite: Spam

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_error': version.InvalidFormatError,
                }),
            ('invalid version word', {
                'test_input': textwrap.dedent("""\
                    BoGuS 1.0
                    =========

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_error': version.InvalidFormatError,
                }),
            ('invalid section title', {
                'test_input': textwrap.dedent("""\
                    Lorem Ipsum 1.0
                    ===============

                    :Released: 2009-01-01
                    :Maintainer: Foo Bar <foo.bar@example.org>

                    * Lorem ipsum dolor sit amet.
                    """),
                'expected_error': version.InvalidFormatError,
                }),
            ]

    def expected_error_context(self):
        """ Make a context manager to expect the nominated error. """
        context = NoOpContextManager()
        if hasattr(self, 'expected_error'):
            context = testtools.ExpectedException(self.expected_error)
        return context

    def test_returns_expected_version_info(self):
        """ Should return expected version info mapping. """
        infile = io.StringIO(self.test_input)
        with self.expected_error_context():
            result = version.changelog_to_version_info_collection(infile)
        if hasattr(self, 'expected_version_info'):
            self.assertThat(result, JsonEqual(self.expected_version_info))


fake_version_info = {
        'release_date': "2001-01-01", 'version': "2.0",
        'maintainer': None, 'body': None,
        }


@unittest.mock.patch.object(
        version, "get_latest_version", return_value=fake_version_info)
class generate_version_info_from_changelog_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘generate_version_info_from_changelog’ function. """

    fake_open_side_effects = {
            'success': (
                lambda *args, **kwargs: io.StringIO()),
            'file not found': FileNotFoundError(),
            'permission denied': PermissionError(),
            }

    scenarios = [
            ('simple', {
                'open_scenario': 'success',
                'fake_versions_json': json.dumps([fake_version_info]),
                'expected_result': fake_version_info,
                }),
            ('file not found', {
                'open_scenario': 'file not found',
                'expected_result': {},
                }),
            ('permission denied', {
                'open_scenario': 'permission denied',
                'expected_result': {},
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.fake_changelog_file_path = tempfile.mktemp()

        def fake_open(filespec, *args, **kwargs):
            if filespec == self.fake_changelog_file_path:
                side_effect = self.fake_open_side_effects[self.open_scenario]
                if callable(side_effect):
                    result = side_effect()
                else:
                    raise side_effect
            else:
                result = io.StringIO()
            return result

        func_patcher_io_open = unittest.mock.patch.object(
                io, "open")
        func_patcher_io_open.start()
        self.addCleanup(func_patcher_io_open.stop)
        io.open.side_effect = fake_open

        self.file_encoding = "utf-8"

        func_patcher_changelog_to_version_info_collection = (
                unittest.mock.patch.object(
                    version, "changelog_to_version_info_collection"))
        func_patcher_changelog_to_version_info_collection.start()
        self.addCleanup(func_patcher_changelog_to_version_info_collection.stop)
        if hasattr(self, 'fake_versions_json'):
            version.changelog_to_version_info_collection.return_value = (
                    self.fake_versions_json.encode(self.file_encoding))

    def test_returns_empty_collection_on_read_error(
            self,
            mock_func_get_latest_version):
        """ Should return empty collection on error reading changelog. """
        test_error = PermissionError("Not for you")
        version.changelog_to_version_info_collection.side_effect = test_error
        result = version.generate_version_info_from_changelog(
                self.fake_changelog_file_path)
        expected_result = {}
        self.assertDictEqual(expected_result, result)

    def test_opens_file_with_expected_encoding(
            self,
            mock_func_get_latest_version):
        """ Should open changelog file in text mode with expected encoding. """
        version.generate_version_info_from_changelog(
                self.fake_changelog_file_path)
        expected_file_path = self.fake_changelog_file_path
        expected_open_mode = 'rt'
        expected_encoding = self.file_encoding
        (open_args_positional, open_args_kwargs) = io.open.call_args
        (open_args_filespec, open_args_mode) = open_args_positional[:2]
        open_args_encoding = open_args_kwargs['encoding']
        self.assertEqual(expected_file_path, open_args_filespec)
        self.assertEqual(expected_open_mode, open_args_mode)
        self.assertEqual(expected_encoding, open_args_encoding)

    def test_returns_expected_result(
            self,
            mock_func_get_latest_version):
        """ Should return expected result. """
        result = version.generate_version_info_from_changelog(
                self.fake_changelog_file_path)
        self.assertEqual(self.expected_result, result)


DefaultNoneDict = functools.partial(collections.defaultdict, lambda: None)


class get_latest_version_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_latest_version’ function. """

    scenarios = [
            ('simple', {
                'test_versions': [
                    DefaultNoneDict({'release_date': "LATEST"}),
                    ],
                'expected_result': version.ChangeLogEntry.make_ordered_dict(
                    DefaultNoneDict({'release_date': "LATEST"})),
                }),
            ('no versions', {
                'test_versions': [],
                'expected_result': collections.OrderedDict(),
                }),
            ('ordered versions', {
                'test_versions': [
                    DefaultNoneDict({'release_date': "1"}),
                    DefaultNoneDict({'release_date': "2"}),
                    DefaultNoneDict({'release_date': "LATEST"}),
                    ],
                'expected_result': version.ChangeLogEntry.make_ordered_dict(
                    DefaultNoneDict({'release_date': "LATEST"})),
                }),
            ('un-ordered versions', {
                'test_versions': [
                    DefaultNoneDict({'release_date': "2"}),
                    DefaultNoneDict({'release_date': "LATEST"}),
                    DefaultNoneDict({'release_date': "1"}),
                    ],
                'expected_result': version.ChangeLogEntry.make_ordered_dict(
                    DefaultNoneDict({'release_date': "LATEST"})),
                }),
            ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = version.get_latest_version(self.test_versions)
        self.assertDictEqual(self.expected_result, result)


@unittest.mock.patch.object(json, "dumps", side_effect=json.dumps)
class serialise_version_info_from_mapping_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_latest_version’ function. """

    scenarios = [
            ('simple', {
                'test_version_info': {'foo': "spam"},
                }),
            ]

    for (name, scenario) in scenarios:
        scenario['fake_json_dump'] = json.dumps(scenario['test_version_info'])
        scenario['expected_value'] = scenario['test_version_info']

    def test_passes_specified_object(self, mock_func_json_dumps):
        """ Should pass the specified object to `json.dumps`. """
        version.serialise_version_info_from_mapping(
                self.test_version_info)
        mock_func_json_dumps.assert_called_with(
                self.test_version_info, indent=unittest.mock.ANY)

    def test_returns_expected_result(self, mock_func_json_dumps):
        """ Should return expected result. """
        mock_func_json_dumps.return_value = self.fake_json_dump
        result = version.serialise_version_info_from_mapping(
                self.test_version_info)
        value = json.loads(result)
        self.assertEqual(self.expected_value, value)


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
