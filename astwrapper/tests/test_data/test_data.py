""" This Module is an exact replica of astwrapper.py just to use it as test data """

import ast
import logging
import os

log = logging.getLogger(__name__)


def test_function(arg):
    """
    A simple test function
    """
    pass


class AstWrapper(object):
    """
    AstWrapper is a wrapper to add additional attributes to an ast tree.

    The addition attributes added to a AST node are:
        parent      - this holds the immediate parent of the node
        parents     - this holds the all the parents of a node, 1st element being the immediate parent and last
                      being the top of the tree.
        line_range  - Line range is a tuple containing start and end line of the node.
        end_line    - End line of the node, for function it will be the line number of the last line.
        is_new      - If module_lines_changed was specified, this will hold True or False depending on the
                      line number of the node
    """
    def __init__(self, source='', module_lines_changed=[]):
        """
        Args:
            source (str): Source str or file name of the source file.
            module_lines_changed (list): List of lines changed for a module, useful when used with git diff

        """
        self.source = source
        self.module_lines_changed = module_lines_changed

        # To keep track of changed nodes
        self.changed_nodes = {}

        self.node = self._parse_source(source)
        if self.node:
            self._load_node_parents(self.node)

    def _parse_source(self, source):
        """
        This method must be implemented in inherited classes to parse source lines
        """
        raise NotImplementedError

    def _load_node_parents(self, node):
        """
        Method to set various additional attributes to a specific node and its children recursively

        Args:
            node (AST): Ast node to load parents
        """

        if not hasattr(node, 'parent'):
            node.parent = None
            node.parents = []

        if not hasattr(node, 'line_range'):
            node.line_range = ()
            node.is_new = False
            node.end_line = 0

        for child_node in ast.iter_child_nodes(node):
            # set node parent
            self._set_node_parent(child_node, node)
            self._load_node_parents(child_node)

            new_end_line = hasattr(child_node, 'body') and child_node.end_line or getattr(child_node, 'lineno', 0)
            if child_node and hasattr(child_node, 'lineno') and hasattr(node, 'body') and node.end_line < new_end_line:
                # If a class has a decorator end line could be wrong.
                    node.end_line = new_end_line

        # TODO: end_line for Expressions and Assignments may not be correct, if it spans multiple lines.
        #       But that should not be an issue and we are interested in start line and processor shall take care of
        #       looping through values etc.
        if node.end_line == 0:
            node.end_line = getattr(node, 'lineno', 0)

        if isinstance(node, ast.Module):
            node.line_range = (getattr(node, 'lineno', 1), node.end_line,)
        else:
            node.line_range = (getattr(node, 'lineno', 0), node.end_line,)

        self._set_is_new(node)

    def _set_node_parent(self, child_node, node):
        """
        Set parent and parents attribute for an AST node

        Args:
            child_node (AST): Child node for which parent & parents attribute is to be set
            node (AST): Ast node that is parent to the child_node
        """
        if not hasattr(child_node, 'parent'):
            child_node.parent = None
            child_node.parents = []

        child_node.parent = node
        child_node.parents.append(node)
        child_node.parents.extend(node.parents)

    def _set_is_new(self, node):
        """
        Set is_new flag to True if the whole node is new.
        """
        node.is_new = node.line_range[0] in self.module_lines_changed and node.line_range[1] in self.module_lines_changed

        if node.is_new:
            self.changed_nodes[node.line_range] = node


class AstModuleWrapper(AstWrapper):
    """
    Wrapper for ast module providing various helper methods
    """

    def _parse_source(self, source):
        """
        Module to parse
        Args:
            source (str): Source module file name to be loaded and parsed by ast module

        """
        ast_tree = None

        if not os.path.isfile(source):
            # If module is not a file write to std out, could be that file was deleted
            log.warning("Unable to parse source file={}".format(source))
            return

        with open(source, 'r') as f:
            ast_tree = ast.parse(f.read())

        return ast_tree


if __name__ == "__main__":
    tree = AstModuleWrapper(TEST_DATA_FILE_NAME, range(1, 150))
