# Praktikum 3: Code Analyzer Python mengidentifikasi error dari CST

## 3.1 Tahapan analyzer
(ISI SENDIRI, urut, dengan kata-katamu)
1. Traversal CST (DFS): kumpulkan class_definition, function_definition, assignment, call, attribute
2. Bangun symbol table per scope (modul, class, fungsi)
3. Resolusi nama: nama tidak ketemu = undefined name
4. Resolusi atribut: cek atribut ada di class
5. Pengecekan tipe: argumen call vs parameter, operand +, return vs return_type
6. Laporkan error beserta baris/kolom dari node.start_point

## 3.2 Error dan node CST kunci

| Error | Node CST kunci | Tahap |
| --- | --- | --- |
| NameError order_status | identifier tak ada di scope fungsi | 3 |
| AttributeError order.id | attribute (field object, attribute) | 4 |
| TypeError calculate_tax("0.11") | call > argument_list > string | 5 |
| str + angka | binary_operator operator + | 5 |
| Return str, deklarasi float | return_statement vs return_type | 5 |

## 3.3 Perbandingan dengan pyflakes dan mypy

| Error | pyflakes | mypy biasa | mypy --check-untyped-defs | checker CST |
| --- | --- | --- | --- | --- |
| "0.11" ke float (baris 52) | tidak | ya | ya | ya (R3) |
| order_status (baris 73) | ya | tidak | ya | ya (R1) |
| order.id (baris 58) | tidak | tidak | tidak | peringatan (R2) |
| product.quantity (baris 83) | tidak | tidak | tidak | peringatan (R2) |
| str + angka, return type (baris 88) | tidak | ya | ya | ya (R4, R5) |
| int jadi float (baris 86) | tidak | ya | ya | ya (R6) |

(ISI SENDIRI: jelaskan kenapa order.id dan product.quantity hanya peringatan,
dan kenapa mypy biasa melewatkan order_status.)
