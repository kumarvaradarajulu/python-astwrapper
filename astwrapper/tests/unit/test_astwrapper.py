import unittest
import mock
import ast

from astwrapper import AstModuleWrapper, AstWrapper
from tests.unit.load_test_data import (
    TEST_DATA_MODULE_FILE_NAME,
    test_data_module_ast_tree,
    test_data_module_number_of_lines,
)


TESTING_MODULE = 'astwrapper'


class TestAstWrapper(unittest.TestCase):
    """
    Test suite to test AstWrapper
    """
    def setUp(self):
        super(TestAstWrapper, self).setUp()

        self.lines_changed = range(1, 22)

    @mock.patch.object(AstWrapper, '_load_node_parents')
    @mock.patch.object(AstWrapper, '_parse_source')
    def test_init_with_valid_args(self, mock__parse_source, mock__load_node_parents):
        """ Test case to test init method with valid args """
        mock__parse_source.return_value = test_data_module_ast_tree
        wrapper = AstWrapper(TEST_DATA_MODULE_FILE_NAME, self.lines_changed)
        mock__parse_source.assert_called_with(TEST_DATA_MODULE_FILE_NAME)
        mock__load_node_parents.assert_called_with(test_data_module_ast_tree)
        self.assertDictEqual(wrapper.changed_nodes, {})
        self.assertListEqual(self.lines_changed, wrapper.module_lines_changed)

    @mock.patch.object(AstWrapper, '_load_node_parents')
    @mock.patch.object(AstWrapper, '_parse_source')
    def test_init_with_no_args(self, mock__parse_source, mock__load_node_parents):
        """ Test case to test init method with no args """
        mock__parse_source.return_value = test_data_module_ast_tree
        wrapper = AstWrapper()
        mock__parse_source.assert_called_with('')

        # Attributes must be set to their defaults
        self.assertListEqual([], wrapper.module_lines_changed)
        self.assertEqual('', wrapper.source)

    def test__parse_source(self):
        """ Test to check if _parse_source raises NotImplementedError error """
        with self.assertRaises(NotImplementedError):
            wrapper = AstWrapper()  # noqa

    @mock.patch.object(AstWrapper, '_parse_source')
    def test__load_node_parents(self, mock__parse_source):
        """ Test case for _load_node_parents method """
        module_ast_tree = test_data_module_ast_tree
        mock__parse_source.return_value = module_ast_tree
        wrapper = AstWrapper(TEST_DATA_MODULE_FILE_NAME, self.lines_changed)

        module_node = wrapper.node
        module_node_body = module_node.body

        # Check Module line range
        self.assertTupleEqual(module_node.line_range, (1, test_data_module_number_of_lines))

        # Check def test_function
        self.assertTupleEqual(module_node_body[5].line_range, (10, 14))
        # check if test_function contains pass statement on line 27
        self.assertIsInstance(module_node_body[5].body[1], ast.Pass)
        self.assertTupleEqual(module_node_body[5].body[1].line_range, (14, 14))

        # Check import simplejson node for wrapping
        self.assertTrue(module_node_body[3].is_new)
        self.assertTupleEqual(module_node_body[3].line_range, (5, 5))

        # Check class AstWrapper node for wrapper
        astwrapper_class = module_node_body[6]
        self.assertTupleEqual(astwrapper_class.line_range, (17, 116))

        # Check class AstModuleWrapper
        ast_module_wrapper_class = module_node_body[7]
        self.assertTupleEqual(ast_module_wrapper_class.line_range, (119, 141))

        # Check line number of _parse_source method of AstModuleWrapper class
        self.assertTupleEqual(ast_module_wrapper_class.body[1].line_range, (124, 141))

        # Check if the lasr node is an if condition for __name__ == 'main'
        self.assertIsInstance(module_node_body[8], ast.If)
        self.assertTupleEqual(module_node_body[8].line_range, (144, 145))


class TestAstModuleWrapper(unittest.TestCase):
    """
    Test suite to test AstModuleWrapper
    """
    def setUp(self):
        super(TestAstModuleWrapper, self).setUp()
        self.lines_changed = []

    @mock.patch.object(AstWrapper, '_load_node_parents')
    @mock.patch(TESTING_MODULE + '.ast')
    @mock.patch(TESTING_MODULE + '.os')
    def test__parse_source_with_existent_file(self, mock_os, mock_ast, mock__load_node_parents):
        """
        Test to check if _parse_source parses the source file.
        """
        mock_os.path.isfile.return_value = True

        with mock.patch(TESTING_MODULE + '.open', mock.mock_open(), create=True):
            wrapper = AstModuleWrapper(TEST_DATA_MODULE_FILE_NAME)  # noqa
            self.assertTrue(mock_ast.parse.called)

    @mock.patch.object(AstWrapper, '_load_node_parents')
    @mock.patch(TESTING_MODULE + '.log')
    @mock.patch(TESTING_MODULE + '.ast')
    @mock.patch(TESTING_MODULE + '.os')
    def test__parse_source_with_non_existent_file(self, mock_os, mock_ast,
                                                  mock_log, mock__load_node_parents):
        """
        Test to check if _parse_source raises Exception
        """
        mock_os.path.isfile.return_value = False

        with mock.patch(TESTING_MODULE + '.open', mock.mock_open(), create=True):

            wrapper = AstModuleWrapper(TEST_DATA_MODULE_FILE_NAME)

        self.assertFalse(mock_ast.parse.called)
        self.assertIsNone(wrapper.node)
        mock_log.warning.assert_called_with("Unable to parse source file={}".format(TEST_DATA_MODULE_FILE_NAME))
