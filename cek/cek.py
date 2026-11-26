import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

BATAS_BARIS = 30
ABAIKAN = {"venv", ".venv", ".git", "node_modules", "__pycache__"}

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNGSI = Query(PY, "(function_definition name: (identifier) @nama) @fungsi")


def cari_error_pertama(node):
    """DFS: kembalikan node ERROR/MISSING pertama, atau None."""
    if node.is_error or node.is_missing:
        return node
    if node.has_error:
        for child in node.children:
            hasil = cari_error_pertama(child)
            if hasil is not None:
                return hasil
    return None


def cek_file(path):
    tree = parser.parse(path.read_bytes())
    root = tree.root_node

    # Fitur 1: komentar TODO/FIXME
    for node in QueryCursor(Q_TODO).captures(root).get("c", []):
        teks = node.text.decode(errors="replace").strip()
        print(f"{path}:{node.start_point[0] + 1}: TODO: {teks}")

    # Fitur 2: fungsi lebih dari BATAS_BARIS baris
    for _, cap in QueryCursor(Q_FUNGSI).matches(root):
        fungsi = cap["fungsi"][0]
        nama = cap["nama"][0].text.decode(errors="replace")
        jumlah = fungsi.end_point[0] - fungsi.start_point[0] + 1
        if jumlah > BATAS_BARIS:
            print(f"{path}:{fungsi.start_point[0] + 1}: FUNGSI PANJANG: {nama} ({jumlah} baris)")

    # Fitur 3: file dengan error sintaks
    if root.has_error:
        err = cari_error_pertama(root)
        baris = err.start_point[0] + 1 if err else "?"
        print(f"{path}:{baris}: ERROR SINTAKS")


def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python cek.py <folder>")
        sys.exit(1)

    jumlah_file = 0
    for path in sorted(Path(sys.argv[1]).rglob("*.py")):
        if any(bagian in ABAIKAN for bagian in path.parts):
            continue
        cek_file(path)
        jumlah_file += 1
    print(f"\nSelesai: {jumlah_file} file diperiksa.")


main()
