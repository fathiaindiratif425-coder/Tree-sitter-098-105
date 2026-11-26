"""Checker semantik buatan sendiri di atas CST Tree-sitter.
Aturan: R1 undefined name | R2 atribut tidak ada | R3 tipe argumen call
        R4 operator str + angka | R5 return type | R6 tipe variabel berubah
"""
import builtins
from symbols import parse, bangun_symbols, walk, teks, tipe_literal

root = parse()
SYM = bangun_symbols(root)
CLASSES, FUNCS = SYM["classes"], SYM["functions"]
SEMUA_ATRIBUT = {a for c in CLASSES.values() for a in list(c["attrs"]) + list(c["methods"])}
BUILTIN = set(dir(builtins))
temuan = []


def lapor(kode, node, pesan):
    r, c = node.start_point
    temuan.append((r + 1, c, kode, pesan))


def tipe_ekspresi(n, env):
    """Infer tipe ekspresi. None = tidak diketahui."""
    t = tipe_literal(n)
    if t:
        return t
    if n.type == "identifier":
        return env.get(teks(n))
    if n.type == "attribute":
        obj, att = n.child_by_field_name("object"), teks(n.child_by_field_name("attribute"))
        ct = env.get(teks(obj)) if obj.type == "identifier" else None
        return CLASSES[ct]["attrs"].get(att) if ct in CLASSES else None
    if n.type == "call":
        f = n.child_by_field_name("function")
        if f.type == "identifier" and teks(f) in CLASSES:
            return teks(f)
        if f.type == "identifier" and teks(f) in FUNCS:
            return FUNCS[teks(f)]["ret"]
        if f.type == "attribute":
            ct = env.get(teks(f.child_by_field_name("object")))
            if ct in CLASSES:
                m = CLASSES[ct]["methods"].get(teks(f.child_by_field_name("attribute")))
                return m["ret"] if m else None
    if n.type == "binary_operator":
        a = tipe_ekspresi(n.child_by_field_name("left"), env)
        b = tipe_ekspresi(n.child_by_field_name("right"), env)
        if a == "str" and teks(n.child_by_field_name("operator")) == "+":
            return "str"
        if {a, b} <= {"int", "float"} and a and b:
            return "float" if "float" in (a, b) else "int"
    return None


def cocok(param_t, arg_t):
    return arg_t is None or param_t is None or param_t == arg_t or (param_t == "float" and arg_t == "int")


def periksa_fungsi(func, kelas=None):
    fname = teks(func.child_by_field_name("name"))
    env = {}
    if kelas:
        env["self"] = kelas
    for nama, t in ambil_params_semua(func):
        env[nama] = t
    dikenal = set(env) | set(CLASSES) | set(FUNCS) | BUILTIN

    for n in walk(func.child_by_field_name("body")):
        # kumpulkan definisi lokal (urut kemunculan)
        if n.type == "assignment" and n.child_by_field_name("left").type == "identifier":
            nama = teks(n.child_by_field_name("left"))
            t = tipe_ekspresi(n.child_by_field_name("right"), env)
            if env.get(nama) == "int" and t == "float":
                lapor("R6", n, f"variabel '{nama}' awalnya int lalu jadi float (type inconsistency)")
            dikenal.add(nama)
            if t:
                env[nama] = t
        if n.type == "for_statement":
            dikenal.add(teks(n.child_by_field_name("left")))

    env2 = {k: v for k, v in env.items()}
    for n in walk(func.child_by_field_name("body")):
        p = n.parent
        # R1 undefined name
        if n.type == "identifier":
            if p.type == "attribute" and p.child_by_field_name("attribute") == n:
                continue
            if p.type == "keyword_argument" and p.child_by_field_name("name") == n:
                continue
            if teks(n) not in dikenal:
                lapor("R1", n, f"NameError: nama '{teks(n)}' tidak didefinisikan di fungsi '{fname}'")
        # R2 atribut tidak ada
        if n.type == "attribute" and n.child_by_field_name("object").type == "identifier":
            obj, att = teks(n.child_by_field_name("object")), teks(n.child_by_field_name("attribute"))
            ct = env2.get(obj)
            if ct in CLASSES:
                c = CLASSES[ct]
                if att not in c["attrs"] and att not in c["methods"]:
                    lapor("R2", n, f"AttributeError: class {ct} tidak punya atribut '{att}'")
            elif ct is None and att not in SEMUA_ATRIBUT and obj in dikenal and obj not in BUILTIN:
                lapor("R2", n, f"PERINGATAN: '{obj}.{att}' - tipe '{obj}' tidak diketahui dan "
                               f"'{att}' bukan atribut class mana pun")
        # R3 tipe argumen
        if n.type == "call":
            f = n.child_by_field_name("function")
            params = None
            if f.type == "identifier" and teks(f) in CLASSES:
                params = CLASSES[teks(f)]["methods"].get("__init__", {}).get("params")
            elif f.type == "identifier" and teks(f) in FUNCS:
                params = FUNCS[teks(f)]["params"]
            elif f.type == "attribute":
                ct = env2.get(teks(f.child_by_field_name("object")))
                if ct in CLASSES:
                    m = CLASSES[ct]["methods"].get(teks(f.child_by_field_name("attribute")))
                    params = m["params"] if m else None
            if params:
                args = [a for a in n.child_by_field_name("arguments").named_children
                        if a.type != "keyword_argument"]
                for (pn, pt), a in zip(params, args):
                    at = tipe_ekspresi(a, env2)
                    if not cocok(pt, at):
                        lapor("R3", a, f"TypeError: argumen '{teks(a)}' bertipe {at}, "
                                       f"parameter '{pn}' butuh {pt}")
        # R4 str + angka
        if n.type == "binary_operator" and teks(n.child_by_field_name("operator")) == "+":
            a = tipe_ekspresi(n.child_by_field_name("left"), env2)
            b = tipe_ekspresi(n.child_by_field_name("right"), env2)
            if {a, b} & {"str"} and {a, b} & {"int", "float"}:
                lapor("R4", n, f"TypeError: operator + antara {a} dan {b}")
        # R5 return type
        if n.type == "return_statement" and n.named_child_count:
            rt = func.child_by_field_name("return_type")
            if rt is not None:
                t = tipe_ekspresi(n.named_children[0], env2)
                if t and not cocok(teks(rt), t):
                    lapor("R5", n, f"return bertipe {t}, tetapi '{fname}' dideklarasikan -> {teks(rt)}")


def ambil_params_semua(func):
    out = []
    for p in func.child_by_field_name("parameters").named_children:
        if p.type == "identifier":
            out.append((teks(p), None))
        elif p.type == "typed_parameter":
            out.append((teks(p.named_children[0]), teks(p.child_by_field_name("type"))))
    return out


for n in root.children:
    if n.type == "function_definition":
        periksa_fungsi(n)
    elif n.type == "class_definition":
        for m in n.child_by_field_name("body").children:
            if m.type == "function_definition":
                periksa_fungsi(m, teks(n.child_by_field_name("name")))

print(f"{'BARIS':<6}{'KOL':<5}{'ATURAN':<7}PESAN")
for r, c, k, p in sorted(temuan):
    print(f"{r:<6}{c:<5}{k:<7}{p}")
print(f"\nTotal temuan: {len(temuan)}")
