# Ek analiz planı (önceden kayıt) — 23 Ekim 2026

Bu plan, aşağıdaki analizlerin sonuçları görülmeden yazılmış ve git ile zaman damgalanmıştır. Plan dışı her değişiklik ayrıca gerekçesiyle günlüğe yazılır. Birincil sonuçlar (Hücre 4–6) değişmez; aşağıdakiler bunların sağlamlığını ve geçerliliğini sınar.

## E1 — Ölçüm güvenilirliği
- Her kişinin ana yöntem tek destek aralıkları iki yarıya bölünür: (i) ilk yarı / ikinci yarı, (ii) tek / çift sıralı aralıklar.
- İki yarının CV'leri arasında ICC(2,1) (mutlak uyum) ve Spearman-Brown düzeltmeli güvenilirlik; grup bazında ve toplam.
- Yorum eşiği (Koo & Li 2016): < 0,5 zayıf, 0,5–0,75 orta, 0,75–0,9 iyi, > 0,9 mükemmel.

## E2 — Dönüş tespiti (basınç merkezi tabanlı) ve doğrulama
- Biçim dosyasındaki algılayıcı koordinatlarından her ayak için mediolateral basınç merkezi vekili (COPx) hesaplanır.
- Adım dizisi özellikleri: sol/sağ duruş süresi, adım süresi, her ayağın duruş fazı ortalama COPx'i. Her özellik kişinin kendi kayan medyanına göre dayanıklı z-puanına çevrilir (pencere 15 adım, ölçekli MAD).
- Bileşik sapma = özelliklerin |z| ortalaması. Bileşik sapma > 2,5 olan adımlar işaretlenir; aralarında ≤ 2 adım olan işaretler tek "dönüş olayı"na birleştirilir; olayın her iki yanına 1 adım tampon eklenir.
- **Doğrulama (CV sonuçlarından bağımsız):**
  (a) Beklenen dönüş sayısı = hız × süre / 25 m (Patoz: 25 m koridor). Bulunan ile beklenen arasında Spearman korelasyonu ve ortalama mutlak fark.
  (b) Dönüşler arası süre beklenen 25 m / hız ile karşılaştırılır (oran medyanı ~1 beklenir).
  (c) Rastgele 6 kişide grafikle gözle kontrol.
- Parametreler (2,5 eşik, 15 adım pencere, 1 adım tampon) yalnız (a)–(b) doğrulamasına göre, CV sonuçlarına bakılmadan ayarlanabilir; ayarlanırsa günlüğe yazılır.
- Dönüş segmentleri çıkarılmış CV (`CV_cop`) hesaplanır ve Hücre 4–6'nın birincil analizleri bu ölçüyle tekrarlanır (duyarlılık).

## E3 — Model tanıları ve fonksiyonel biçim
- M1 ve birincil şiddet modeli için: artık normalliği (Shapiro-Wilk, Q-Q), değişen varyans (Breusch-Pagan), VIF, Cook uzaklığı.
- Hızın doğrusal olmayan etkisi: hız için doğal kübik spline (df = 3) ile M1 ve şiddet modeli tekrarlanır.
- CV sağa çarpık olduğundan log(CV) ile tekrar (katsayı yüzde değişim olarak yorumlanır).

## E4 — Alt çalışma heterojenliği
- M1 PD farkı ve şiddet eğimi her alt çalışmada ayrı tahmin edilir; DerSimonian-Laird rastgele etkiler birleştirmesi, I² ve Q testi.
- PD × Çalışma ve UPDRS × Çalışma etkileşim testleri.

## E5 — Aracılık (hız)
- Toplam etki (M0), doğrudan etki (M1), dolaylı etki = a × b (a: PD → hız, b: hız → CV | PD, Çalışma); kişi bazlı bootstrap %95 GA (2000, tohum 4011); aracılık oranı. Kesitsel veri nedeniyle nedensel yorum yapılmaz.

## E6 — Seçim yanlılığının nicelleştirilmesi
- PD–kontrol farkı dört yolla: (i) Patoz eşleştirmesi, (ii) regresyon (M1), (iii) hız + çalışmaya göre örtüşme ağırlıklandırması (overlap weights, lojistik eğilim skoru), (iv) eşleştirilmiş tahminin dışarıdaki PD'lere genellenmesi için aralık × PD etkileşimli model.
- Aralıktaki ve dışarıdaki PD'lerin UPDRS / H&Y farkı yaş ve çalışma ayarlı regresyonla.
- Şiddet eğiminin aralık içinde ve dışında farklı olup olmadığı (UPDRS × aralık etkileşimi).

## E7 — Çoklu karşılaştırma
- Birincil analiz (Hücre 6 birincil) düzeltilmez. İkincil şiddet testleri (motor UPDRS, H&Y, dönüş ayıklamalı / COP CV) Holm yöntemiyle düzeltilir.

## E8 — Kesinlik / duyarlılık gücü
- n = 90 ve birincil modelin artık SS'si ile %80 güçte saptanabilecek en küçük eğim (iki yönlü α = 0,05).

## E9 — İki ayak birleşik CV
- Sol ve sağ tek destek aralıkları birleştirilerek tek CV; Hücre 4–6 birincil analizleri bununla tekrarlanır.

## E10 — Raporlama
- STROBE (gözlemsel çalışma) kontrol listesi doldurulur; rapor güncellenir.

## Kullanıcı gerektiren (Claude yapamaz)
- Literatür elemesinde bağımsız ikinci değerlendirici (Cohen kappa).
- Scopus / Web of Science / IEEE Xplore'da aynı sorgular (üniversite erişimi).
