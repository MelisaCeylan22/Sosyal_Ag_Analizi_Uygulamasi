# Sosyal Ağ Analizi Uygulaması  
**Ekip:** Melisa Ceylan  
**Tarih:** 02.01.2026  

---

## 1. Giriş

### 1.1 Problemin Tanımı
Sosyal ağlar; kullanıcılar (düğümler) ve aralarındaki ilişkiler (kenarlar) üzerinden modellenebilen, analiz edilmesi gereken karmaşık yapılardır. Gerçek hayatta “kim kiminle etkileşimde?”, “bir kullanıcıdan diğerine en kısa yol nedir?”, “ağ hangi alt topluluklara ayrılıyor?” gibi sorulara cevap aramak için graf teorisi temelli algoritmalar kullanılır.  
Bu proje, sosyal ağ benzeri verileri **graf modeli** ile temsil edip, temel graf algoritmalarını çalıştırarak sonuçları **görsel ve anlaşılır** biçimde sunan bir masaüstü uygulaması geliştirmeyi hedefler.

### 1.2 Amaç
Bu çalışmanın amacı:
- Sosyal ağ yapısını **düğüm–kenar (Graph)** modeliyle kurmak,
- BFS, DFS, Dijkstra, A* gibi algoritmalarla ağ üzerinde gezinme / yol bulma işlemlerini gerçekleştirmek,
- Welsh–Powell renklendirme ile düğüm renklendirme yaklaşımını uygulamak,
- Algoritmaların çalışmasını **görselleştirerek** adım adım izlenebilir hale getirmek,
- Graf verisini **JSON/CSV** formatlarında kaydedip tekrar yükleyebilmek,
- Hatalı veri girişlerini (duplicate edge, self-loop vb.) yöneterek sistemin güvenilirliğini artırmaktır.

### 1.3 Kapsam
Uygulama aşağıdaki ana bileşenleri kapsar:
- **Graf Modeli İşlemleri:** Düğüm/kenar ekleme, silme, güncelleme, ağırlık (weight) yönetimi  
- **Algoritmalar:** BFS, DFS, Dijkstra, A*  
- **Renklendirme:** Welsh–Powell düğüm renklendirme  
- **Görselleştirme:** Algoritma adımlarının ekranda animasyon/renk değişimiyle gösterimi  
- **Veri Saklama:** JSON/CSV dışa aktarma ve içe aktarma  
- **Test ve Hata Yönetimi:** Hatalı kenarlar, tekrar eden bağlantılar, self-loop vb. kontroller

### 1.4 Varsayımlar ve Kısıtlar
- Dijkstra algoritması gereği **negatif ağırlıklı (negative weight)** kenarlar desteklenmez; bu tür girişler hata olarak ele alınır.
- Self-loop (bir düğümün kendisine bağlanması) ve duplicate edge (aynı iki düğüm arasında aynı bağlantının tekrar eklenmesi) gibi durumlar uygulama kurallarına göre engellenir veya kullanıcıya uyarı verilir.
- Uygulama bir “sosyal ağ simülasyonu” değil; sosyal ağların **graf temsili ve analizini** hedefleyen bir analiz aracıdır.

### 1.5 Beklenen Çıktılar
- Seçilen algoritmaya göre ziyaret sırası / bulunan yol / maliyet bilgisi
- Görsel ekranda algoritmanın adım adım ilerleyişi
- Kaydedilebilir/yüklenebilir graf veri dosyaları (JSON/CSV)

  

## 2. Algoritmalar ve Analizler

Bu bölümde uygulamada gerçeklenen algoritmaların çalışma mantığı, akış diyagramları (Mermaid), karmaşıklık analizi ve kısa literatür notları sunulmuştur.

### 2.1 BFS (Breadth-First Search) — Genişlik Öncelikli Arama
 
BFS, bir graf üzerinde başlangıç düğümünden başlayıp düğümleri katman katman (level-by-level) ziyaret eden temel bir gezme algoritmasıdır. Önce başlangıcın komşuları, sonra onların komşuları şeklinde genişleyerek ilerler. Bu yüzden kuyruk (queue) veri yapısı ile uygulanması doğaldır. Ağırlıksız graflarda BFS, başlangıçtan diğer düğümlere giden en az kenarlı yolu (shortest path in number of edges) bulur.

#### 2.1.1 Literatürde Kısa Notlar

- BFS, graf gezme algoritmalarının en temel taşlarından biridir ve özellikle ağırlıksız en kısa yol problemi için standart yaklaşımdır.
- Erken dönem çalışmalarda BFS’nin temel fikri (katmanlı genişleme) ve ağ/maze benzeri yapılarda kullanımı klasikleşmiştir; günümüzde sosyal ağ analizinden ağ güvenliğine kadar birçok alanda “temel yapı taşı” olarak geçer.
- BFS’nin bir başka güçlü yönü, gezerken aynı anda ebeveyn (parent) ilişkisi tutularak “hangi düğüme nereden ulaşıldığı” bilgisinin çıkarılabilmesidir.

#### 2.1.2 Akış diyagramı:

```mermaid
flowchart TD
  A[Başla] --> B[Input: graph, start]
  B --> C["q = deque([start])"]
  C --> D["visited = {start}"]
  D --> E["parent[start] = None"]
  E --> F["order = []"]

  F --> G{q boş mu?}
  G -- Hayır --> H["u = q.popleft()"]
  H --> I["order.append(u)"]
  I --> J["for v in neighbors(graph, u)"]
  J --> K{v visited içinde mi?}

  K -- Hayır --> L["visited.add(v)"]
  L --> M["parent[v] = u"]
  M --> N["q.append(v)"]
  N --> J

  K -- Evet --> J
  J --> G

  G -- Evet --> O["return order, parent"]
```


#### 2.1.3 Çalışma Mantığı

Bu süreç BFS’yi şu şekilde yürütür:

**Başlatma (Initialization)**

- q = deque([start]) ile kuyruk yalnızca başlangıç düğümünü içerir.
- visited = {start} ile başlangıç düğümü daha en başta ziyaret edildi işaretlenir.
- parent = {start: None} ile başlangıcın ebeveyni olmadığını belirtilir.
- order = liste, düğümlerin işlenme (kuyruktan çıkma) sırasını tutar.

**Ana döngü (while q)**

Kuyruk boş değilken çalışır.

- u = q.popleft() ile kuyruğun başından düğüm alınır (FIFO mantığı).
- order.append(u) ile işlenen düğüm ziyaret sırasına eklenir.
- Bu kodda “order”a ekleme, düğüm kuyruğa girince değil, kuyruktan çıkınca yapılır.

**Komşuları gezme (for v in neighbors(graph, u))**

- for v in neighbors(graph, u) ile u düğümünün komşuları dolaşılır.
- Eğer v daha önce ziyaret edilmediyse:

    - visited.add(v) → düğüm keşfedildiği an visited işaretlenir (tekrar kuyruğa eklenmesi engellenir).
    - parent[v] = u → v düğümüne ilk kez u üzerinden ulaşıldığı kaydedilir (BFS ağacı oluşur).
    - q.append(v) → v kuyruğun sonuna eklenir; böylece katman mantığı korunur.

**Çıktı**

Döngü bittiğinde kuyruk boşalmıştır, yani erişilebilen tüm düğümler gezilmiştir.

Fonksiyon şunu döndürür:

- order: Düğümlerin BFS sırasında kuyruktan çıkma sırası (popleft sırası)
- parent: her düğümün BFS ağacındaki ebeveyni (yol geri sarma için kullanılabilir)

Bu sürüm, parent sayesinde istenirse “start → herhangi bir düğüm” yolunu geriye doğru takip ederek çıkarabilir (parent chain).

#### 2.1.4 Karmaşıklık Analizi

Bu uygulamada BFS, visited kümesi ile her düğümü en fazla bir kez keşfeder ve her kenarı en fazla bir kez (yönsüz graf ise pratikte iki uçtan) kontrol eder.

- **Zaman Karmaşıklığı:** **O(V + E)**
  - V: düğüm sayısı, E: kenar sayısı
  - Her düğüm kuyruğa en fazla 1 kez girer/çıkar.
  - neighbors(graph, u) üzerinden komşular gezilirken toplamda kenarlar taranır.

- **Bellek Karmaşıklığı:** **O(V)**
  - visited en fazla V düğüm tutar.
  - parent en fazla V kayıt tutar.
  - order en fazla V eleman tutar.
  - q (deque) en kötü durumda O(V) büyüyebilir.

### 2.2 DFS (Depth-First Search) — Derinlik Öncelikli Arama
DFS (Depth-First Search), bir graf üzerinde başlangıç düğümünden başlayarak **mümkün olduğunca derine** inmeyi hedefleyen temel bir gezme algoritmasıdır. Bir yol boyunca ilerler, ilerleyemeyince geri dönüp (backtracking) başka kollara yönelir. Bu davranış genellikle **yığın (stack)** ya da özyineleme (recursion) ile sağlanır.

#### 2.2.1 Literatür Notu

DFS, graf teorisinde en temel iki gezme yaklaşımından biridir (BFS ile birlikte). Literatürde DFS’nin önemi şu noktalarda vurgulanır:

- **Keşif mantığı:** DFS, bir düğümden başlayıp bir komşu üzerinden “olabildiğince derine” inmeye çalışır. Bu davranış, grafik üzerinde bir **arama ağacı (DFS tree)** oluşturur. Bu ağaç üzerinden “hangi düğüme nereden ulaşıldı?” bilgisi çıkarılabilir.
- **Temel alt yapı algoritması:** DFS, tek başına bir “gezinme” algoritması olmasının yanında;  
  **bağlı bileşen bulma**, **döngü (cycle) tespiti**, **topolojik sıralama**, **köprü ve kesme noktaları** gibi birçok graf probleminin temel bileşenidir. Bu yüzden ders kitaplarında ve klasik graf algoritmaları kaynaklarında “çok amaçlı temel araç” olarak geçer.
- **Uygulama alanı:** Sosyal ağlarda “ağın bir bölgesini derinlemesine tarama”, yazılım analizinde “bağımlılık grafında derin arama”, ağ güvenliğinde “erişilebilirlik taraması” gibi örneklerde DFS yaklaşımı sık görülür.
- **Yığın (stack) / özyineleme:** Literatürde DFS genellikle recursion ile anlatılsa da, pratikte recursion limitleri nedeniyle **stack tabanlı iteratif DFS** de standarttır. .
- Kısacası DFS, “grafı dolaşmak için basit bir yöntem” olmanın ötesinde, birçok daha büyük algoritmanın iskeletini oluşturan temel bir parçadır.

#### 2.2.2 Akış Diyagramı
```mermaid
flowchart TD
  A[Start] --> B["Input: graph, start"]
  B --> C["stack = [start]"]
  C --> D["visited = empty set"]
  D --> E["parent[start] = None"]
  E --> F["order = empty list"]

  F --> G{stack empty?}
  G -- No --> H["u = stack.pop()"]
  H --> I{u visited?}
  I -- Yes --> G
  I -- No --> J["visited.add(u)"]
  J --> K["order.append(u)"]

  K --> L["ns = list(neighbors(graph, u))"]
  L --> M["reverse(ns)  (DFS hissi için)"]
  M --> N["for v in ns"]
  N --> O{v visited?}
  O -- Yes --> N
  O -- No --> P{v in parent?}
  P -- No --> Q["parent[v] = u"]
  P -- Yes --> R["(parent değişmez)"]
  Q --> S["stack.append(v)"]
  R --> S
  S --> N

  N --> G
  G -- Yes --> T["Return: order and parent"]
```
#### 2.2.3 Çalışma Mantığı

Bu projedeki DFS uygulaması, özyineleme yerine **yığın (stack) tabanlı iteratif** yöntemle gerçekleştirilmiştir. Algoritma, bir düğümden başlayarak mümkün olduğunca derine ilerler; ilerleyemediğinde yığından geri dönerek başka dalları keşfeder.

**Başlatma**
- stack = [start]: ile arama başlangıç düğümünü içeren bir yığınla başlatılır.
- visited = set(): başlangıçta boştur; düğümler “işlenecekleri anda” visited olarak işaretlenir.
- parent[start] = None ile başlangıç düğümünün ebeveyni olmadığı belirtilir.
- order = []` listesi, düğümlerin DFS sırasında **işlenme sırasını** tutmak için kullanılır.

**Ana Döngü**

Yığın boşalana kadar şu adımlar tekrarlanır:
- u = stack.pop() ile yığının en üstündeki düğüm alınır (LIFO).
- Eğer `u` daha önce ziyaret edilmişse (`u in visited`), bu düğüm işlenmeden atlanır (`continue`).  
  Bu kontrol, aynı düğümün farklı yollardan yığına eklenmiş olabileceği durumlarda **tekrar işlemeyi engeller**.
  - u ziyaret edilmemişse:
  - visited.add(u) ile düğüm ziyaret edildi olarak işaretlenir.
  - order.append(u) ile işlenme sırasına eklenir.

**Komşuların Yığına Eklenmesi (DFS Sırasını Korumak İçin)**
- neighbors(graph, u) ile u düğümünün komşuları alınır, list() ile listeye çevrilir ve reverse() yapılır.
- Bunun amacı şudur: Yığın LIFO çalıştığı için komşuları ters sırayla yığına eklemek, ekranda/çıktıda **daha doğal bir DFS ziyaret sırası** üretir.
- Her komşu v için:
  - Eğer v henüz ziyaret edilmemişse:
    - v ilk kez görülüyorsa parent[v] = u atanır. Böylece DFS ağacı oluşur ve “v düğümüne hangi düğüm üzerinden ulaşıldı?” bilgisi korunur.
    - stack.append(v) ile v işlenmek üzere yığına eklenir.

**Çıktı**

Algoritma sonunda aşağıdaki bilgiler döndürülür:
- order: Düğümlerin DFS sırasında **işlendiği** (visited’a alındığı) sıra
- parent: DFS ağacındaki ebeveyn ilişkileri (istenirse herhangi bir düğüme giden yol, ebeveynler üzerinden geriye doğru takip edilerek çıkarılabilir)


#### 2.2.4 Karmaşıklık Analizi

DFS algoritmasının çalışma maliyeti grafın büyüklüğüne bağlıdır. Burada  
**V** düğüm sayısını, **E** ise kenar sayısını ifade eder.

**Zaman Karmaşıklığı: O(V + E)**  
Bu implementasyonda zaman karmaşıklığının O(V + E) olmasının temel gerekçeleri şunlardır:

- **Düğümler açısından (O(V))**:  
  Her düğüm, visited kümesine alındıktan sonra bir daha işlenmez. Kodda yer alan  
  if u in visited: continue kontrolü, aynı düğümün yığına birden fazla kez eklenmiş olması durumunda bile düğümün tekrar tekrar işlenmesini engeller. Bu nedenle her düğüm en fazla bir kez “işleme” adımına girer ve bu kısım toplamda O(V) maliyet oluşturur.

- **Kenarlar/komşuluk taraması açısından (O(E))**:  
  Her düğüm işlenirken komşuları for v in ns: döngüsüyle kontrol edilir. Tüm düğümler üzerinden bakıldığında komşuluk listelerinin toplam uzunluğu kenar sayısıyla orantılıdır. Bu nedenle komşu kontrolü adımı toplamda O(E) zaman alır. (Yönsüz graflarda her kenar iki düğümün komşuluk listesinde görülebilir; bu durum sabit katsayı farkı yaratır, ancak asimptotik ifade yine O(E) olarak kalır.)

- **Komşuları ters çevirme adımı (reverse) (O(E))**:  
  Kodda DFS ziyaret sırasını daha tutarlı hale getirmek için komşular listeye çevrilip ters çevrilmektedir (ns = list(...), ns.reverse()). Bu işlem, her düğüm için o düğümün derece değeri kadar çalışır. Tüm düğümler için derece toplamı kenar sayısıyla orantılı olduğundan, bu adım da toplamda O(E) mertebesindedir.

Sonuç olarak, düğüm işleme maliyeti O(V) ve komşuluk/kenar taraması maliyeti O(E) olduğundan toplam zaman karmaşıklığı **O(V + E)** olarak ifade edilir.

**Bellek Karmaşıklığı: O(V)**  
Algoritmanın ek bellek kullanımı düğüm sayısıyla orantılıdır:
- `visited` kümesi en fazla V düğüm tutar.
- `parent` sözlüğü her düğüm için en fazla bir ebeveyn bilgisi saklar (en fazla V kayıt).
- `order` listesi ziyaret edilen düğümleri tutar (en fazla V eleman).
- `stack` yığını, en kötü durumda V düğüme kadar büyüyebilir.

Bu nedenle DFS’nin ek bellek karmaşıklığı **O(V)**’dir.

### 2.3 Dijkstra - Ağırlıklı Graf İçin En KIsa Yol

Dijkstra algoritması, ağırlıklı bir graf üzerinde bir başlangıç düğümünden diğer düğümlere (veya belirli bir hedef düğüme) giden **en düşük toplam maliyetli (en kısa) yolları** bulmak için kullanılan klasik bir yöntemdir. Algoritma, her adımda geçici olarak en küçük mesafeye sahip düğümü seçerek bu düğümün mesafesini “kesinleştirir” ve komşu düğümler için daha iyi bir maliyet bulunup bulunmadığını kontrol eder (relaxation).

 Dijkstra, **negatif ağırlıklı** kenarlar bulunduğunda doğru sonuç garantisi vermez. Bu nedenle uygulamada negatif ağırlık kullanımına izin verilmemesi beklenir.

 #### 2.3.1





