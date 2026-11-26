# Praktikum 1-2: Parse Tree Aplikasi Manajemen Order

## 1. Jenis error pada source code

Kode lolos pengecekan sintaks (has_error = False, tidak ada node ERROR atau MISSING). Semua error bersifat semantik (tipe dan scope), sehingga tidak terdeteksi oleh parser.

| No | Baris | Kode | Jenis error | Penjelasan |
| --- | --- | --- | --- | --- |
| 1 | 52 | `order.calculate_tax("0.11")` | TypeError | Argumen bertipe str, parameter `tax_rate` bertipe float. Error langsung saat main() dijalankan. |
| 2 | 58 | `order.id` | AttributeError | Kelas Order tidak punya atribut `id`. Muncul bila find_order() dipanggil. |
| 3 | 73 | `order_status` | NameError | Variabel tidak pernah didefinisikan. Muncul bila generate_report() dipanggil. |
| 4 | 83 | `product.quantity` | AttributeError | Kelas Product tidak punya atribut `quantity`. Muncul bila calculate_bulk_price() dipanggil. |
| 5 | 88 | `"Total: " + total` | TypeError | Penjumlahan str dengan angka. Tipe return juga tidak sesuai anotasi float. |

Catatan: baris 86 mengurangi discount sebagai nominal, padahal apply_discount memakai persen (kemungkinan kesalahan logika).

## 2. CST dari Tree-sitter

### 2.1 Hasil parse (potongan class Product)
(ISI SENDIRI: salin dari hasil_cst.txt baris 1-25, lihat blok di bawah)

### 2.2 Perbandingan dengan pohon tulisan tangan
(ISI SENDIRI: apa yang sama, apa yang berbeda: node anonim, field, node block)

### 2.3 Derivasi parameter objek
(ISI SENDIRI: derivasi level demi level untuk __init__ Product dan pemanggilan Product(...), dari hasil_param.txt)

Potongan CST (baris 1-25):

    module [1:0]
      class_definition [1:0]
        name: identifier [1:6]
        body: block [2:4]
          function_definition [2:4]
            name: identifier [2:8]
            parameters: parameters [2:16]
              identifier [2:17]
              typed_parameter [2:23]
                identifier [2:23]
                type: type [2:35]
                  identifier [2:35]
              typed_parameter [2:40]
                identifier [2:40]
                type: type [2:46]
                  identifier [2:46]
              typed_parameter [2:51]
                identifier [2:51]
                type: type [2:58]
                  identifier [2:58]
            body: block [3:8]
              expression_statement [3:8]
                assignment [3:8]
                  left: attribute [3:8]
                    object: identifier [3:8]
