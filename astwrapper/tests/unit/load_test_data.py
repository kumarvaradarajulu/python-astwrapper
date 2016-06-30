import ast
import os

from astwrapper import AstModuleWrapper


current_file_dir = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_MODULE_FILE_NAME = os.path.join(current_file_dir, '..', 'test_data', 'test_data.py')


with open(TEST_DATA_MODULE_FILE_NAME, 'r') as f:
    test_data_module_ast_tree = ast.parse(f.read())
    f.seek(0)
    test_data_module_number_of_lines = sum(1 for line in f.readlines())

# Test data ast tree with AstModuleWrapper
test_data_wrapped_module_ast_tree = AstModuleWrapper(TEST_DATA_MODULE_FILE_NAME).node
