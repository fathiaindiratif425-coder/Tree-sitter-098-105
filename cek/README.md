# cek.py

CLI kecil untuk memeriksa file Python memakai tree-sitter.

## Fitur
1. Komentar `TODO` / `FIXME` beserta file dan barisnya
2. Fungsi dengan body lebih dari 30 baris (semua fungsi dihitung, termasuk method dan fungsi bersarang)
3. File yang pohonnya mengandung error sintaks, beserta baris pertama yang bermasalah

## Instalasi
python3 -m venv .venv
source .venv/bin/activate
pip install tree-sitter tree-sitter-python

## Menjalankan
python cek.py <folder>

Folder venv, .venv, .git, node_modules, dan __pycache__ dilewati.

## Contoh output
uji/panjang.py:1: FUNGSI PANJANG: panjang (37 baris)
uji/rusak.py:1: ERROR SINTAKS
uji/todo.py:1: TODO: # TODO: tambah validasi
uji/todo.py:3: TODO: # FIXME: ini sementara

Selesai: 3 file diperiksa.
