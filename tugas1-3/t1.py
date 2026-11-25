import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

kode = b"def sapa(nama):\n    return nama\n"

tree = parser.parse(kode)
print(kode.decode())
print(tree.root_node)


fungsi = tree.root_node.children[0]
print("--- anak fungsi_definition ---")
for c in fungsi.children:
    print(c.type, "bernama" if c.is_named else "anonim")

print("--- anak parameters ---")
params = fungsi.child_by_field_name("parameters")
for c in params.children:
    print(c.type, "bernama" if c.is_named else "anonim")