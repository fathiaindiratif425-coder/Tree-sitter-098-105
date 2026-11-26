import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))
tree = parser.parse(open(sys.argv[1], "rb").read())
print("has_error:", tree.root_node.has_error)
print(tree.root_node)
