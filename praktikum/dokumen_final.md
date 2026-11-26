# Laporan Praktikum: Tree-sitter dan Code Analyzer pada Aplikasi Manajemen Order

**Disusun oleh:**
- Ivanka Bunga Aulia (NIM 251524105)
- Fathia Indira Salsabila (NIM 251524098)

D4 Teknik Informatika, Kelas 2D, Politeknik Negeri Bandung

---


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

## 3. Tahapan code analyzer Python mengidentifikasi error dari CST

### 3.1 Gambaran singkat

Dari praktikum 1 dan 2 kami tahu bahwa Tree-sitter hanya mengecek **bentuk** kode (sintaks). Hasil parse `order_app.py` menunjukkan `has_error: False`, artinya kodenya dianggap valid walaupun sebenarnya akan error kalau dijalankan. Jadi semua error di aplikasi manajemen order ini adalah error **semantik** (tipe, nama, dan atribut), yang baru bisa ketahuan kalau ada analyzer yang membaca makna dari CST-nya.

Untuk bagian ini kami memakai dua cara:
1. **Analyzer Python yang sudah jadi**: `pyflakes` dan `mypy`.
2. **Checker buatan sendiri** di atas CST Tree-sitter (`symbols.py` dan `checker.py`), supaya kami paham bagaimana analyzer bekerja dari dalam.

### 3.2 Hasil analyzer yang sudah jadi

| Tool | Temuan |
| --- | --- |
| pyflakes | Baris 73: `undefined name 'order_status'` |
| mypy | Baris 11 (`items` butuh anotasi tipe), baris 52 (argumen `str` padahal butuh `float`), baris 86 (variabel `int` jadi `float`), baris 88 (operator `+` antara `str` dan `int`) |
| mypy `--check-untyped-defs` | Semua temuan mypy di atas, ditambah baris 73 (`Name "order_status" is not defined`) |

Ada dua hal yang kami perhatikan:
- `mypy` biasa tidak menemukan `order_status`, tetapi dengan `--check-untyped-defs` baru ketemu. Penyebabnya, `generate_report` tidak punya anotasi tipe, jadi mypy secara default melewati isi fungsi itu.
- Tidak ada satu pun tool jadi yang menemukan `order.id` (baris 58) dan `product.quantity` (baris 83), padahal atribut itu memang tidak ada di class `Order` maupun `Product`.

### 3.3 Tahapan analyzer mengidentifikasi error dari CST

Alur checker kami ada enam tahap. Berikut penjelasan tiap tahap, beserta di kode mana tahap itu dikerjakan.

**Tahap 1: Traversal CST.** Analyzer menelusuri pohon dari `module` ke bawah dengan DFS (fungsi `walk()` di `symbols.py`). Sambil menelusuri, ia hanya memperhatikan node yang penting: `class_definition`, `function_definition`, `assignment`, `call`, `attribute`, `binary_operator`, dan `return_statement`.

**Tahap 2: Membangun symbol table.** Fungsi `bangun_symbols()` membuat "buku catatan" berisi: nama class beserta atributnya, method beserta parameter dan tipenya, dan fungsi biasa beserta tipe kembaliannya. Atribut class diambil dari assignment `self.x = ...` di dalam `__init__`. Contoh hasilnya, `Order` punya atribut `customer: str`, `items: list`, dan `total: float`. Parameter diambil dari node `typed_parameter`, misalnya `price: float` dibaca sebagai nama `price` dengan tipe `float`.

**Tahap 3: Resolusi nama.** Setiap node `identifier` yang dipakai dicek ada atau tidak di scope fungsi tersebut (parameter, variabel lokal, nama class, nama fungsi, atau builtin). Kalau tidak ada, itu undefined name. Ini yang menangkap `order_status` di baris 73. Variabel itu dipakai di `generate_report`, tetapi tidak pernah dibuat di fungsi itu maupun di luarnya (aturan R1).

**Tahap 4: Resolusi atribut.** Untuk node `attribute` seperti `order.id`, analyzer mencari tahu dulu tipe objeknya, lalu mengecek atributnya ada di symbol table class itu atau tidak. Kalau tipe objek diketahui (misalnya `self` di dalam class `Order`) dan atributnya tidak ada, itu `AttributeError` pasti. Kalau tipe objek tidak diketahui, checker hanya memberi **peringatan** (aturan R2). Ini yang terjadi pada `order.id` dan `product.quantity`: keduanya adalah variabel dari perulangan `for`, sehingga tipenya tidak bisa dipastikan. Checker hanya bisa bilang bahwa `id` dan `quantity` bukan atribut di class mana pun, tanpa bisa membuktikan pasti.

**Tahap 5: Pengecekan tipe.** Tahap ini memeriksa tiga hal.
- *Argumen vs parameter (R3).* Pada `order.calculate_tax("0.11")`, argumennya node `string` (tipe `str`), sedangkan parameter `tax_rate` bertipe `float`. Tipe tidak cocok, jadi dilaporkan `TypeError`. Aturan kecocokannya: `int` boleh dipakai di tempat `float` (misalnya `7500000` untuk `price: float`), tetapi `str` tidak boleh.
- *Operator `+` (R4).* Pada `"Total: " + total` di baris 88, sisi kiri `str` dan sisi kanan angka, jadi dilaporkan `TypeError`.
- *Tipe return (R5).* Fungsi `calculate_bulk_price` dideklarasikan `-> float`, tetapi `return` mengembalikan `str`, jadi dilaporkan tidak sesuai.

**Tahap 6: Pelaporan.** Setiap temuan dicatat lewat fungsi `lapor()` dengan nomor baris dan kolom dari `node.start_point`, lalu diurutkan dan dicetak.

Selain itu ada satu aturan tambahan (R6): di `calculate_bulk_price`, variabel `total` mulai dari `0` (tipe `int`), lalu di baris 86 diisi hasil pengurangan dengan `discount` yang bertipe `float`. Perubahan tipe ini dicatat sebagai type inconsistency.

### 3.4 Node CST yang menjadi kunci deteksi tiap error

| Error | Baris | Node CST kunci | Tahap |
| --- | --- | --- | --- |
| `order_status` tidak terdefinisi | 73 | `identifier` yang tidak ada di scope fungsi | 3 |
| `order.id` tidak ada atributnya | 58 | `attribute` (field `object` dan `attribute`) | 4 |
| `product.quantity` tidak ada atributnya | 83 | `attribute` (field `object` dan `attribute`) | 4 |
| `calculate_tax("0.11")` salah tipe | 52 | `call` > `argument_list` > `string` | 5 |
| `"Total: " + total` | 88 | `binary_operator` dengan operator `+` | 5 |
| Return `str`, deklarasi `float` | 88 | `return_statement` dibandingkan dengan field `return_type` di `function_definition` | 5 |
| `total` berubah dari `int` ke `float` | 86 | `assignment` (field `left` dan `right`) | 5 |

### 3.5 Hasil checker buatan sendiri

```
BARIS KOL ATURAN PESAN
52 34 R3 TypeError: argumen '"0.11"' bertipe str, parameter 'tax_rate' butuh float
58 15 R2 PERINGATAN: 'order.id' - tipe 'order' tidak diketahui dan 'id' bukan atribut class mana pun
73 26 R1 NameError: nama 'order_status' tidak didefinisikan di fungsi 'generate_report'
83 33 R2 PERINGATAN: 'product.quantity' - tipe 'product' tidak diketahui dan 'quantity' bukan atribut class mana pun
86 8 R6 variabel 'total' awalnya int lalu jadi float (type inconsistency)
88 4 R5 return bertipe str, tetapi 'calculate_bulk_price' dideklarasikan -> float
88 11 R4 TypeError: operator + antara str dan float

Total temuan: 7
```

### 3.6 Perbandingan checker dengan pyflakes dan mypy

| Error | pyflakes | mypy biasa | mypy `--check-untyped-defs` | Checker CST |
| --- | --- | --- | --- | --- |
| `"0.11"` ke parameter float (baris 52) | tidak | ya | ya | ya (R3) |
| `order_status` (baris 73) | ya | tidak | ya | ya (R1) |
| `order.id` (baris 58) | tidak | tidak | tidak | peringatan (R2) |
| `product.quantity` (baris 83) | tidak | tidak | tidak | peringatan (R2) |
| `str + angka` dan return type (baris 88) | tidak | ya | ya | ya (R4, R5) |
| `int` jadi `float` (baris 86) | tidak | ya | ya | ya (R6) |

Hal-hal yang kami simpulkan dari perbandingan ini:
1. `order.id` dan `product.quantity` hanya terdeteksi oleh checker kami, itu pun hanya sebagai peringatan. Tool jadi melewatkannya karena tipe variabel loop tidak diketahui. Ini kelebihan sekaligus keterbatasan checker kami: ia bisa menandai kemungkinan error, tetapi tidak bisa memastikannya.
2. Pada baris 88, mypy menulis `str` dan `int`, sedangkan checker kami menulis `str` dan `float`. Perbedaannya karena mypy memakai tipe awal `total` (`int`, dari `total = 0`), sedangkan checker kami melacak bahwa pada baris 86 `total` sudah menjadi `float`.
3. Checker kami hanya memiliki 6 aturan dan dibuat khusus untuk kode ini, jadi tidak selengkap pyflakes atau mypy. Tujuannya untuk memahami cara kerja analisis semantik, bukan menggantikan tool jadi.
4. Ada satu kesalahan yang tidak ditangkap tool mana pun, yaitu kesalahan logika di `process_order`: diskon hanya diterapkan kalau `total > 100000`, dan pajak dihitung dari `total` awal, bukan dari harga setelah diskon. Hal seperti ini hanya bisa ditemukan dengan membaca kode atau menguji perilakunya.

### 3.7 Kesimpulan

Tree-sitter menghasilkan CST yang lengkap dan akurat soal struktur kode, tetapi CST itu tidak tahu arti dari kode. Analyzer-lah yang menambahkan makna dengan membangun symbol table, mencocokkan nama, atribut, dan tipe, lalu menandai bagian CST yang tidak konsisten. Kunci deteksinya selalu berupa node tertentu di CST (misalnya `call`, `attribute`, `binary_operator`, atau `return_statement`), sehingga kualitas analisis sangat bergantung pada seberapa jelas informasi tipe yang tersedia di kode.
