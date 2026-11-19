# Tugas 1 - Pohon if/else (Bunga, branch 105_Bunga)

Kode: `contoh/ifelse.py`
Jalankan: `python tugas1-3/t1.py tugas1-3/contoh/ifelse.py`

## Perkiraan di kertas
Perkiraan sama dengan hasil. Node anonim (if, >, :, else, (, )) tidak tampil di output t1.py

## Hasil sebenarnya (ringkas, node bernama)
```
module
  if_statement
    condition: comparison_operator (identifier, integer)
    consequence: block -> expression_statement -> call(identifier, argument_list(string))
    alternative: else_clause
      body: block -> expression_statement -> call(identifier, argument_list(string))
```

## Node anonim (tidak tampil di output t1.py, tapi ada di pohon)
| Node | Posisi | Keterangan |
|------|--------|------------|
| `if` | baris 1 | kata kunci, anak `if_statement` |
| `>`  | baris 1 | operator, anak `comparison_operator` |
| `:`  | baris 1 | titik dua setelah kondisi, anak `if_statement` |
| `else` | baris 3 | kata kunci, anak `else_clause` |
| `:`  | baris 3 | titik dua setelah else, anak `else_clause` |
| `(` dan `)` | baris 2 dan 4 | anak `argument_list` |

## Percobaan: hapus `:` pada `if x > 0`
Hasil:
```
(module (if_statement condition: (comparison_operator (identifier) (ERROR (integer)) (call ...)) (ERROR) consequence: (block ...)))
```
Parser tidak berhenti. Ia membungkus bagian yang tidak cocok dengan `ERROR`, lalu tetap
mencoba membangun sisa pohonnya. `if x > 0` dan `print(...)` pada baris berikutnya
tergabung jadi satu `comparison_operator`.

## Percobaan lain
- Hapus `:` pada `else` -> muncul `(ERROR)` dan `else_clause` hilang; baris `print` jadi
  `expression_statement` biasa di luar `if_statement`.
- Hapus `)` pada `print("positif"` -> muncul `ERROR` dan `consequence: (block)` kosong.
- `MISSING` tidak muncul pada percobaan di atas; pada kasus ini tree-sitter memakai `ERROR`.
