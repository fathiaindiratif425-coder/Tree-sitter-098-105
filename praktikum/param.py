import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))
tree = parser.parse(open(sys.argv[1], "rb").read())

def tampil(node, kedalaman=0, field=None):
    label = f"{field}: " if field else ""
    teks = f"  '{node.text.decode()}'" if node.child_count == 0 else ""
    print("  " * kedalaman + f"{label}{node.type}{teks}")
    for i, c in enumerate(node.children):
        tampil(c, kedalaman + 1, node.field_name_for_child(i))

def cari(node):
    if node.type == "function_definition":
        nama = node.child_by_field_name("name").text.decode()
        print(f"\n=== def {nama} ===")
        tampil(node.child_by_field_name("parameters"))
    if node.type == "call":
        fungsi = node.child_by_field_name("function").text.decode()
        if fungsi == "Product":
            print(f"\n=== pemanggilan {fungsi}(...) baris {node.start_point[0] + 1} ===")
            tampil(node.child_by_field_name("arguments"))
    for c in node.named_children:
        cari(c)

cari(tree.root_node)
