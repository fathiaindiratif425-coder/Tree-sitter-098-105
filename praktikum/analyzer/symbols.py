"""Traversal CST + symbol table (Tree-sitter)."""
import json
import tree_sitter_python as tsp
from tree_sitter import Language, Parser


def teks(n):
    return n.text.decode() if n is not None else None


def walk(n):
    """DFS: kunjungi node lalu semua anaknya."""
    yield n
    for c in n.children:
        yield from walk(c)


def tipe_literal(n):
    """Tipe dari node literal. None = tidak diketahui."""
    return {"integer": "int", "float": "float", "string": "str",
            "list": "list", "dictionary": "dict", "true": "bool", "false": "bool"}.get(n.type)


def ambil_params(func):
    """List (nama, tipe) tanpa 'self'. Tipe None jika tidak dianotasi."""
    hasil = []
    for p in func.child_by_field_name("parameters").named_children:
        if p.type == "identifier" and teks(p) != "self":
            hasil.append((teks(p), None))
        elif p.type == "typed_parameter":
            nama = teks(p.named_children[0])
            if nama != "self":
                hasil.append((nama, teks(p.child_by_field_name("type"))))
    return hasil


def ret_type(func):
    r = func.child_by_field_name("return_type")
    return teks(r) if r else None


def bangun_symbols(root):
    """Hasil: {'classes': {nama: {attrs, methods}}, 'functions': {nama: {params, ret}}}"""
    classes, functions = {}, {}
    for n in root.children:
        if n.type == "function_definition":
            functions[teks(n.child_by_field_name("name"))] = {
                "params": ambil_params(n), "ret": ret_type(n)}
        elif n.type == "class_definition":
            cname = teks(n.child_by_field_name("name"))
            attrs, methods = {}, {}
            for m in n.child_by_field_name("body").children:
                if m.type != "function_definition":
                    continue
                mname = teks(m.child_by_field_name("name"))
                params = ambil_params(m)
                methods[mname] = {"params": params, "ret": ret_type(m)}
                if mname == "__init__":
                    ptype = dict(params)
                    for a in walk(m):
                        if a.type != "assignment":
                            continue
                        kiri, kanan = a.child_by_field_name("left"), a.child_by_field_name("right")
                        if kiri.type == "attribute" and teks(kiri.child_by_field_name("object")) == "self":
                            t = tipe_literal(kanan) or (ptype.get(teks(kanan)) if kanan.type == "identifier" else None)
                            attrs[teks(kiri.child_by_field_name("attribute"))] = t
            classes[cname] = {"attrs": attrs, "methods": methods}
    return {"classes": classes, "functions": functions}


def parse(path="praktikum/order_app.py"):
    parser = Parser(Language(tsp.language()))
    return parser.parse(open(path, "rb").read()).root_node


if __name__ == "__main__":
    print(json.dumps(bangun_symbols(parse()), indent=2, ensure_ascii=False))
