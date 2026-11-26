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

Potongan di bawah adalah baris 1-25 dari `hasil_cst.txt`, yaitu bagian awal
`class Product` sampai assignment pertama di `__init__`. Pohon ini menampilkan
named node beserta posisi [baris:kolom] dan nama field (`name`, `parameters`,
`body`, `left`, `object`, `type`).

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

Struktur utamanya: `module` -> `class_definition` -> `block` ->
`function_definition` (`__init__`) -> `parameters` dan `block` (isi method).
Parameter `self` berupa `identifier` biasa, sedangkan `product_id: int`,
`name: str`, dan `price: float` dibungkus `typed_parameter` yang berisi
`identifier` dan field `type`.

### 2.2 Perbandingan dengan pohon tulisan tangan

**Yang sama**
- Hierarki inti sama: class -> method -> parameter -> body.
- Urutan dan kedalaman node bernama sama: `class_definition`,
  `function_definition`, `parameters`, `assignment`, `attribute`.

**Yang berbeda**
- **Node anonim (token literal)**: CST tree-sitter menyimpan token sintaks
  seperti `class`, `def`, `(`, `)`, `,`, `:`, `=`, dan `.` sebagai child
  (terlihat di hasil_param.txt). Pohon tulisan tangan biasanya membuangnya
  karena tidak membawa makna.
- **Field**: tree-sitter memberi label pada child (`name:`, `parameters:`,
  `body:`, `left:`, `object:`, `type:`), sehingga peran tiap anak jelas.
  Pada pohon tulisan tangan, peran hanya terlihat dari posisi.
- **Node `block`**: tree-sitter membungkus isi class dan fungsi dalam `block`.
  Di pohon tulisan tangan, statement biasanya langsung jadi anak
  fungsi/class.
- **Node pembungkus**: ada `expression_statement` di atas `assignment`, dan
  `type` di atas `identifier` pada anotasi tipe. Ini tidak muncul di pohon
  tulisan tangan.
- **Posisi**: setiap node punya koordinat [baris:kolom], sedangkan pohon
  tulisan tangan tidak.

### 2.3 Derivasi parameter objek

**a) Parameter `__init__` milik Product**

Kode: `def __init__(self, product_id: int, name: str, price: float):`

Derivasi level demi level (-> berarti "diturunkan menjadi"):

    function_definition
      -> 'def'  name:identifier  parameters:parameters  ':'  body:block
    parameters
      -> '('  identifier  ','  typed_parameter  ','  typed_parameter  ','  typed_parameter  ')'
    identifier (self)
      -> 'self'
    typed_parameter
      -> identifier  ':'  type:type
    type
      -> identifier
    identifier (nama parameter)
      -> 'product_id' / 'name' / 'price'   (token daun)
    identifier (di dalam type)
      -> 'int' / 'str' / 'float'           (token daun)

Pohon hasil akhir (dari `hasil_param.txt`):

    parameters
      (  '('
      identifier  'self'
      ,  ','
      typed_parameter
        identifier  'product_id'
        :  ':'
        type: type
          identifier  'int'
      ,  ','
      typed_parameter
        identifier  'name'
        :  ':'
        type: type
          identifier  'str'
      ,  ','
      typed_parameter
        identifier  'price'
        :  ':'
        type: type
          identifier  'float'
      )  ')'

**b) Pemanggilan `Product(101, "Laptop", 7500000)` (baris 94)**

Derivasi level demi level:

    call
      -> function:identifier  arguments:argument_list
    identifier
      -> 'Product'
    argument_list
      -> '('  expression  ','  expression  ','  expression  ')'
    expression pertama  -> integer '101'
    expression kedua    -> string
    string              -> string_start '"'  string_content 'Laptop'  string_end '"'
    expression ketiga   -> integer '7500000'

Pohon hasil akhir (dari `hasil_param.txt`):

    argument_list
      (  '('
      integer  '101'
      ,  ','
      string
        string_start  '"'
        string_content  'Laptop'
        string_end  '"'
      ,  ','
      integer  '7500000'
      )  ')'

**Perbandingan keduanya**

- Parameter formal memakai `typed_parameter` (ada nama dan tipe), sedangkan
  argumen aktual hanya berupa nilai (`integer`, `string`) tanpa nama atau tipe.
- Kedua daftar sama-sama dibuka `(`, dipisah `,`, dan ditutup `)`.
- Jumlahnya cocok: 3 parameter setelah `self` dan 3 argumen. Urutan tipenya
  juga sesuai (`int` -> `101`, `str` -> `"Laptop"`, `float` -> `7500000`;
  integer boleh dipakai untuk parameter float).
- Tree-sitter tidak mengecek kecocokan jumlah dan tipe argumen dengan
  parameter. Itu tugas analisis semantik, bukan parser.