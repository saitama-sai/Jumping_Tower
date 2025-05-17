# 🎮 Jumpy Tower



---

## Jumpy Tower Oyun Raporu
Jumpy Tower, pygame kullanılarak geliştirilmiş eğlenceli bir platform oyunudur. Oyun mekanikleri, görsel öğeler ve teknik detaylara odaklanan bu raporda projenin tüm yönlerini inceleyeceğiz.
Oyunun Genel Özellikleri
Jumpy Tower, dikey yönde ilerleyen bir platform oyunudur. Oyuncu, yükselen kulelerdeki platformlar arasında zıplayarak ilerler ve mümkün olduğunca yükseğe çıkmaya çalışır. Oyunun temel özellikleri şunlardır:

Dikey Platform Mekaniği: Oyuncu, sürekli olarak yukarı doğru hareket eden platformlar arasında zıplayarak ilerler.
Takla Sistemi: Oyuncular "power" çubuğu dolduğunda takla atabilir, bu da ekstra yükseklik ve puan kazandırır.
Combo Sistemi: Duvarlardan sekme ve takla atma ile combo yapılabilir.
Puan Sistemi: Yükseldikçe, blok atladıkça ve özel hareketler yaptıkça puan kazanılır.
Yüksek Skor Takibi: En yüksek skorlar dosyada saklanır ve oyun menüsünde gösterilir.

### Oyun Mekanikleri
#### 1. Karakter Kontrolü

Ok tuşları: Karakteri sağa ve sola hareket ettirir
Boşluk/Yukarı tuşu: Zıplama mekanizmasını tetikler
F tuşu: Power %90'ın üzerindeyken takla atmayı sağlar

#### 2. Fizik Sistemi

Yerçekimi ve zıplama fiziği gerçekçi bir şekilde uygulanmıştır
Karakter platformlara çarptığında doğru tepkiler verir
Duvarlardan sekme mekanikleri takla sırasında aktiftir

#### 3. Özel Hareketler

Takla:

Power çubuğu %90 dolduğunda F tuşuyla etkinleştirilir
Karaktere geçici uçuş yeteneği ve hız kazandırır
Takla sırasında bloklar üzerinden geçiş ekstra puan sağlar


Duvar Sekmesi:

Takla sırasında duvara çarpıldığında gerçekleşir
Combo çarpanını artırır
Hız ve manevra kabiliyeti artışı sağlar
Her sekme başına ekstra puan kazandırır



#### 4. Zorluk Artışı

Oyun ilerledikçe hız kademeli olarak artar (1.5x başlangıç hızından 2.9x'e kadar)
Platformların rastgele yerleşimi ve boyutları oyunun her seferinde farklı hissedilmesini sağlar


###### Görseller

Karakter için çoklu animasyon kareleri:

Koşma (6 kare)

Atlama (1 kare)

Düşme (1 kare)

Takla (4 kare)

Bekleme (2 kare)

Hasar alma (1 kare)


Platform ve arka plan görselleri

Takla ve combo efektleri

###### Kullanıcı Arayüzü

Ana menü ekranı

Yardım/Talimatlar ekranı

Oyun sırasında gösterilen bilgiler:

Anlık skor

Oyun hızı

Power çubuğu

Combo çarpanı (aktif olduğunda)

Atlanan blok sayısı (takla sırasında)



##### Teknik Detaylar
###### Kod Yapısı

GameManager Sınıfı: Oyun döngüsü, menü yönetimi ve yüksek skor kaydetme işlemlerini yönetir

Player Sınıfı: Karakter fiziği, animasyonları ve özel yetenekleri içerir

Block Sınıfı: Platform oluşturma ve yönetme mantığını içerir

Performans Optimizasyonu

Ekran dışında kalan platformlar yeniden konumlandırılarak bellek verimliliği sağlanır

Animasyon kareleri önbelleğe alınarak performans artırılmıştır

Kamera hareketi oyuncu hareketlerini takip eder ve akıcı bir oynanış sağlar

##### Dosya Sistemi

Yüksek skorlar "highscore.txt" dosyasında saklanır

Karakter ve platform görselleri "assets" klasöründen yüklenir

Görsel dosyalarının eksikliği durumunda basit geometrik şekiller kullanılır