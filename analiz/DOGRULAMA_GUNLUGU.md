# Doğrulama günlüğü — genişletilmiş analiz

Her adımda ne çalıştırıldı, nasıl doğrulandı, ne değişti. Kod: bu klasördeki `hucreN_*.py`; çıktılar: `hucreN_cikti*.txt`.
Ortam: yerel Python 3.12 (pandas 3.1.0, statsmodels 0.15.0, scipy, matplotlib). Hücre 1–2 ayrıca Colab Pro'da çalıştırılıp aynı sonuç alındı; kullanıcı 23 Ekim'de sonraki adımların yerelde yapılmasını onayladı.

## Hücre 1 — veri kontrolü (23 Ekim 2026)
- Sonuç: hız dolu 92 PD + 73 kontrol; Patoz aralığında (1,0–1,3 m/s) 54 PD + 42 kontrol; dışarıda 38 PD + 31 kontrol.
- Doğrulama: Önceden saf Python ile yapılan sayımla ve Colab çıktısıyla birebir aynı. 54 PD, Patoz 2023'ün sayısıyla aynı.
- Bulgu: `Juc010` demografide var, veri tabanında JuCo10 adına hiçbir kayıt yok (S3 listesi kontrol edildi). → Analiz örneklemi 92 PD + 72 kontrol = 164.

## Hücre 2 — ön işleme ve olay kontrolü (GaPt04)
- Eski yöntem 94 aralık CV %15,85; Patoz ön işlemesi 89 aralık CV %11,55.
- Doğrulama: Şekil 3'te olaylar sinyal üzerinde gözle kontrol edildi; Colab çıktısı yerelle aynı.

## Hücre 3 — 164 kişinin CV'si
### İlk çalıştırma (`hucre3_cikti_ilk_calistirma.txt`)
- Doğrulama 1: Eski yöntemle Ga alt grubu 13 Ekim Colab sonucunu birebir verdi (PD %23,071, kontrol %15,535) → kod eski analizle tutarlı.
- Doğrulama 2: Kişi bazlı uç değer taraması iki sorun buldu:
  - **JuPt25** (ort. tek destek 0,23 s, CV %64): Salınımda ayak sürtmesi 20 N eşiğini anlık geçip sahte basış/kalkış üretiyor (`kontrol_grafikleri/JuPt25.png`).
  - **SiCo15** (dönüş ayıklamalı CV %0,013): 10 ms çözünürlükte aralıkların yarıdan fazlası aynı → MAD = 0 → kural verinin %48'ini atıyor.
### Düzeltme (grup karşılaştırması yapılmadan, tüm kişilere aynı)
- Kalite kuralı: 0,10 s'den kısa yer teması / havada kalma gürültü sayılır.
- Dönüş ayıklamada ölçekli MAD alt sınırı 0,01 s.
- Kuralsız ana yöntem de `CV_kuralsiz` sütununda tutuluyor (duyarlılık analizi için).
### İkinci çalıştırma (`hucre3_cikti.txt`, tablo `kisi_cv_tum.csv`)
- Kural 48 kişide CV'yi 0,5 puandan fazla değiştirdi (her iki grupta).
- Doğrulama 3: Kuralın etkisi 3 kişide grafikle kontrol edildi (`kontrol_grafikleri/*_kural.png`):
  - GaPt24, SiCo04: eşiği anlık geçen küçük tepeler artık olay sayılmıyor (en kısa aralık 0,01 s → 0,12 / 0,23 s).
  - GaPt25: CV arttı (8,62 → 12,31) çünkü yanlışlıkla ikiye bölünmüş gerçek uzun salınım (0,67 s) birleştirildi — doğru davranış.
- Doğrulama 4: 164 satır, tekrar eden kimlik yok, eksik CV yok; eski yöntem yeniden üretimi hâlâ birebir; dönüş ayıklama artık en çok %18,5 aralık atıyor (medyan %5,6).
- Not: Kuvvet salınımda 20 N'un altına hiç inmeyen (ayağı tam kaldırmadan sürüme) adımlar olay olarak bulunamıyor (ör. GaPt25 22,5 s ve 23,5–24 s). Bu, eşik yönteminin sınırlılığıdır; Patoz yöntemi için de geçerlidir → raporda sınırlılık.

### Grup ortalamaları (CV %, betimsel; çıkarım değil)
| Yöntem | Kontrol | PD |
|---|---|---|
| Ana (Patoz ön işlemesi + kalite kuralı) | 7,82 | 9,89 |
| Kalite kuralı olmadan | 9,60 | 12,45 |
| Eski yöntem | 15,97 | 20,27 |
| 50 N eşik | 6,96 | 9,33 |
| Dönüş ayıklamalı | 3,57 | 5,15 |
| Sağ tek destek | 8,07 | 9,65 |

Patoz 2023 (eşleştirilmiş, dönüşler elle çıkarılmış): kontrol %3,6, PD %5,0 → bizim dönüş ayıklamalı değerlerimiz bu düzeye en yakın; dönüş adımlarının CV'yi şişirdiğini destekliyor. Bu karşılaştırma betimseldir; örneklemler aynı değil.

**Önceden belirlenen ana ölçü değişmedi:** `CV_ana`. Dönüş ayıklamalı ölçü, Patoz'un dönüşleri çıkarmış olması nedeniyle Patoz tekrarında ikincil ölçü olarak raporlanacak; bu tercih grup ortalamaları görüldükten sonra yazıldığı için raporda açıkça belirtilmeli.

## Hücre 4 — Patoz 2023'ü yeniden üretme (`hucre4_cikti.txt`, `tablo_patoz_tekrari.csv`)
- Eşleştirilmiş örneklem (1,0–1,3 m/s): 54 PD + 42 kontrol (Patoz: 54 + 39; 3 kontrol farkının nedeni makalede yok → bilinmiyor). Hızlar benzer (1,146 / 1,168 m/s, p = 0,20).
- Dönüş ayıklamalı CV: PD 4,20 ± 1,81, kontrol 3,52 ± 0,95; fark 0,68; Student p = 0,029; Cohen d = 0,46.
  Patoz: PD 5,0 ± 2,1, kontrol 3,6 ± 1,1; fark 1,4; p < 0,001; d ≈ 0,80.
- Ana CV: PD 9,16 ± 3,18, kontrol 7,92 ± 2,52; p = 0,042; d = 0,42. Sağ tek destek CV: p = 0,23 (anlamlı değil).
- Ortalama tek destek süresi PD'de kısa (0,37 / 0,40 s, p = 0,0016) — Patoz'un "mutlak tek destek süresi PD'de kısa" bulgusuyla aynı yön.
- Yorum: **Kısmi yeniden üretim.** Yön ve kontrol düzeyi tutuyor; PD değeri ve etki büyüklüğü Patoz'dan küçük. Olası nedenler: dönüşler elle değil kuralla ayıklandı; Patoz'un iki ayağı nasıl birleştirdiği ve hangi 39 kontrolü aldığı bilinmiyor.
- Doğrulama: Student t-testi kütüphane kullanılmadan elle yeniden hesaplandı (aralık bağımsız olarak yeniden seçildi): t = 2,214, df = 94, p = 0,0293, d = 0,455 → kütüphane sonucuyla aynı.

## Hücre 5 — tüm örneklem, hız ayarlı model (`hucre5_cikti.txt`, `tablo_tum_orneklem_modeller.csv`)
- Örneklem 164 (92 PD, 72 kontrol; Ga 46, Ju 54, Si 64). Ortalama hız PD 1,034, kontrol 1,239 m/s.
- Modeller: M0 `CV ~ PD + Study`, M1 `CV ~ PD + Speed_01 + Study`; HC3, t dağılımı (`use_t=True`, eski analizle aynı); kişi bazlı bootstrap 2000 tekrar, tohum 4011.
- Ana CV: M0 1,980 [1,075; 2,886]; M1 1,283 [0,295; 2,271], p = 0,011; bootstrap [0,332; 2,238]; M1−M0 = −0,698, bootstrap [−1,407; −0,019].
- Dönüş ayıklamalı CV: M0 1,547 [0,867; 2,228]; M1 0,387 [−0,174; 0,949], p = 0,17; M1−M0 = −1,160, bootstrap [−1,889; −0,506].
- Hız katsayısı negatif (hızlı yürüyende CV düşük): ana −3,45 (p = 0,029), dönüş ayıklamalı −5,73 (p = 0,0002).
- PD × hız etkileşimi (ana CV): −5,23, p = 0,068 (anlamlı değil, sınırda).
- Doğrulama 1: İlk sürümde HC3 normal dağılımla hesaplanmıştı; eski Colab'daki `use_t=True` ile aynı yapılınca eski Ga hız ayarlı sonucu birebir üretildi: 9,522 [2,717; 16,327].
- Doğrulama 2: M0 ve M1 PD katsayıları ile hız katsayısı, kütüphane kullanmadan normal denklemlerle (X'X)⁻¹X'y elle hesaplandı → aynı (1,283 / −3,446; 0,387 / −5,729; M0 1,980 / 1,547).
- Köprü kontrolü (yalnız Ga, yeni ana yöntem): hızsız 2,068 → hız ayarlı 0,989; dönüş ayıklamalı 2,227 → 0,771.
- **Önemli:** Eski analizdeki "hız ayarlanınca fark büyüyor" (7,536 → 9,522) bulgusu, filtresiz/dönüşlü eski yönteme özgü çıktı; Patoz ön işlemesiyle aynı Ga kişilerinde hız ayarı farkı küçültüyor.
- Yorum notu: Yavaş yürüme Parkinson'un kendisinin bir parçası olabilir (aracı değişken). Hız ayarlı katsayı "hızdan bağımsız kalan fark"tır, toplam hastalık farkı değildir → raporda belirtilmeli.

## Hücre 6 — seçim yanlılığı (c) ve şiddet (b) (`hucre6_cikti.txt`, `hucre6_dogrulama.txt`, `tablo_siddet_modelleri.csv`, `pd_hiz_gruplari.csv`)
### (c) Seçim yanlılığı — PD: aralıkta 54, dışarıda 38 (34 yavaş <1,0 m/s, 4 hızlı >1,3 m/s)
- Dışarıda kalanlar: daha yaşlı (70,3 / 63,2; Welch p = 0,0002), CV daha yüksek (ana 10,92 / 9,16, p = 0,020; dönüş ayıklamalı 6,48 / 4,20, p = 0,0009), şiddet eğilimi daha yüksek (UPDRS 34,3 / 29,9, p = 0,10; H&Y 2,33 / 2,19, p = 0,069).
- Yalnız yavaşlar vs aralıktakiler: H&Y 2,37 / 2,19, Mann-Whitney p = 0,024; UPDRS 35,2 / 29,9, p = 0,085.
- Yorum: Hız eşleştirmesi yaşlı, yavaş, daha değişken ve kısmen daha ağır hastaları dışarıda bırakıyor → Patoz'un yazdığı sınırlılık veride destekleniyor (şiddet farkı sınırda; yaş ve CV farkı belirgin).
### (b) Şiddet — yalnız PD, birincil analiz önceden belirlendi: `CV_ana ~ UPDRS/10 + Speed_01 + Study`
- **Birincil:** 10 UPDRS puanı başına +0,982 CV puanı [0,347; 1,617], p = 0,0028; bootstrap [0,410; 1,654]; n = 90.
- İkincil: UPDRS motor +1,289 (p = 0,014); H&Y +2,205 (p = 0,11, anlamlı değil). Dönüş ayıklamalı CV ile ilişkiler hız ayarı sonrası zayıf (UPDRS p = 0,087, motor p = 0,54, H&Y p = 0,078).
- Hız–şiddet: Spearman UPDRS–hız r = −0,07 (p = 0,49); H&Y–hız r = −0,28 (p = 0,007).
### Doğrulama
1. Patoz'un yayımladığı tek korelasyon yeniden üretildi: aralıktaki PD'de UPDRS–hız Pearson r = 0,356, p = 0,0089 (Patoz: r = 0,36, p = 0,009) → eşleştirilmiş PD örneklemimiz Patoz'unkiyle aynı.
2. Birincil katsayı elle (X'X)⁻¹X'y ile: 0,982 → aynı.
3. Yaş eklenince birincil: 0,956 [0,323; 1,588], p = 0,0035 → yaş açıklamıyor. Hücre 5 M1'e yaş eklenince: ana CV PD 1,273 (p = 0,012), dönüş ayıklamalı 0,372 (p = 0,19) → değişmiyor.
4. Birini-çıkar: katsayı 0,830–1,115 arasında; en etkili 3 kişi (JuPt13, SiPt05, JuPt18) çıkarılınca 0,756, p = 0,0047 → tek kişiye bağlı değil.
5. Sıra tabanlı kontrol: hız + çalışma ayarlı CV artıkları ile UPDRS Spearman r = 0,272, p = 0,0096 → normallik varsayımına bağlı değil.
- Not: UPDRS ortalamaları alt çalışmalar arasında farklı (Ga 33,4, Ju 24,9, Si 36,4); modelde Study ayarı var. Çoklu karşılaştırma: birincil tek analiz önceden belirlendi; ikinciller keşifsel.

## Hücre 7 — şekiller ve duyarlılık tablosu (`hucre7_cikti.txt`, `tablo_duyarlilik_ozeti.csv`, `sekil4/5/6_*.png`)
- Şekil 4: eşleştirme vs hız ayarı (orman grafiği; Patoz GA'sı makaledeki ort ± SS'den yaklaşık, dipnotta belirtildi).
- Şekil 5: hız–CV saçılımı (Patoz aralığı gölgeli) + aralıktaki/dışarıdaki PD yaşları.
- Şekil 6: hız ve çalışma ayarlı CV–UPDRS kısmi regresyon grafiği.
- Renkler: başvuru paletinin doğrulanmış ilk iki kategorik rengi; grup ayrıca işaret şekliyle (daire/kare) gösterildi. (Palet doğrulama betiği için Node.js yüklü değil; renk çifti paletin belgelenmiş doğrulanmış sıralamasından alındı.)
- Doğrulama: Tablodaki değerler önceki hücrelerle karşılaştırıldı — eşleştirilmiş Welch p (0,037 / 0,02), M0/M1 katsayıları, birincil şiddet katsayısı (0,98) birebir aynı. Şekil 6'daki kısmi regresyon eğimi (Frisch–Waugh) tam modelle aynı: 0,982. Şekiller gözle incelendi; Şekil 4'te kaybolan "Patoz 2023" etiketi ve Şekil 5'te etiket/lejant çakışması düzeltildi.
### Duyarlılık özeti — sonuçların ön işlemeye bağlılığı
| Ölçü | Eşleştirilmiş | M1 (hız ayarlı) | Şiddet (10 UPDRS) |
|---|---|---|---|
| Ana | 1,23 p=0,037 | 1,28 p=0,011 | 0,98 p=0,003 |
| Dönüş ayıklamalı | 0,68 p=0,02 | 0,39 p=0,17 | 0,38 p=0,087 |
| Kalite kuralı yok | 2,70 p=0,079 | 2,60 p=0,034 | 1,83 p=0,04 |
| 50 N | 1,49 p=0,021 | 1,82 p=0,0005 | 0,55 p=0,14 |
| Sağ tek destek | 0,72 p=0,23 | 0,88 p=0,11 | 0,87 p=0,044 |
| Eski (filtresiz) | 3,64 p=0,21 | 3,93 p=0,081 | 1,10 p=0,45 |
- Yorum: Tüm ölçülerde yön aynı (PD > kontrol; UPDRS arttıkça CV artar), ancak anlamlılık ön işlemeye bağlı. Şiddet ilişkisi 6 ölçüden 3'ünde anlamlı (ana, kalite kuralı yok, sağ tek destek), 1'inde sınırda (dönüş ayıklamalı, p = 0,087), 2'sinde anlamlı değil (50 N, eski yöntem); yönü hepsinde pozitif → raporda "ön işlemeye duyarlı" diye yazılmalı.

---
# Ek analizler (EK_ANALIZ_PLANI.md, git fdfe824 ile sonuçlardan önce kaydedildi)

## E0 — Adım düzeyi olay çıkarma (`ortak.py`, `e0_olay_cikarma.py`, `e0_cikti.txt`)
- 164 kişi; sol ve sağ tek destek CV'leri Hücre 3 ile **birebir aynı** (en büyük fark 0,0).
- Alt çalışma protokolleri `format.txt`'ten doğrulandı: Ga = Yogev 2005, Ju = Hausdorff 2007, Si = Frenkel-Toledo 2005 (Mov Disord); `_01` = olağan yürüyüş. Cinsiyet 2 = kadın (demographics.html).

## E1 — Ölçüm güvenilirliği (`e1_guvenilirlik.py`, `e1_cikti.txt`, `tablo_e1_guvenilirlik.csv`)
- CV_ana: ICC(2,1) tek/çift 0,520 [0,351; 0,648] (Spearman-Brown 0,684); ilk/ikinci yarı 0,405 (0,577). Kontrollerde daha düşük (0,25–0,29).
- CV_cop (E2 sonrası): tek/çift **0,771** [0,622; 0,861] (SB 0,871); ilk/ikinci yarı 0,631 [0,434; 0,760] (SB 0,774).
- Doğrulama: ICC fonksiyonu Shrout & Fleiss (1979) örnek verisinde yayımlanan 0,29'u verdi.
- Yorum: Dönüş adımları ölçüm gürültüsünün ana kaynağı; COP tabanlı ayıklama güvenilirliği "zayıf-orta"dan "iyi"ye çıkarıyor.

## E2 — Dönüş tespiti (`e2_donus_tespiti.py` v1, `e2b_donus_tespiti_v2.py` v2)
- **Plandan sapma 1:** v1 (sabit z eşiği) doğrulamayı geçemedi: fazla dönüş (6,9 / 4,7), dönüşler arası süre beklenenin 0,55'i; eşik 2,5–4,5 denemesi düzeltmedi (`e2_ayar_cikti.txt`). Grafik (`kontrol_grafikleri/e2_donus_inceleme.png`): çok düzenli yürüyenlerde MAD ≈ 0 → z patlıyor; gerçek dönüşler düzenli tepeler.
- **v2:** MAD tabanı (0,02 s / 0,05), 3 adım yumuşatma, tepe bulma, fiziksel aralık kısıtı (≥ 0,6 × koridor / hız), yan pencere.
- **Plandan sapma 2:** Si koridoru 35 m (Frenkel-Toledo 2005 J NeuroEng Rehabil yöntem: "the middle 10 meters of the 35 meter walkway"); Ga, Ju 25 m (Patoz 2023).
- Eşik seçimi yalnız doğrulama ölçüleriyle, CV çıktısı kapalı "ayar" modunda (`e2b_ayar_cikti*.txt`): 1,0 / 1,25 / 1,5 / 1,75 / 2,0 / 2,25. **Seçilen 1,25:** bulunan–beklenen Spearman r = 0,752; aşağı yuvarlanmış beklenene göre sapma −0,04, ortalama mutlak hata 0,55, tam isabet %54, ±1 içinde %92; dönüşler arası süre / (koridor/hız) medyan 1,06 [1,02–1,09].
- Rastgele 6 kişide gözle kontrol (`kontrol_grafikleri/e2_donus_rastgele6.png`, tohum 23): dönüşler doğru; 3 küçük fazladan pencere.
- Aralıkların medyan %11,7'si atıldı; en az kalan 29 aralık. CV_cop: kontrol 4,17, PD 6,12 (Patoz 3,6 / 5,0).

## E3–E9 (`e3_e9_saglamlik.py`, `e3_e9_cikti.txt`, `e3_e9_dogrulama.txt`, `tablo_e_cekirdek.csv`)
### Çekirdek analizler, dört ölçü
| | CV_ana (birincil) | CV_cop | İki ayak | İki ayak + COP |
|---|---|---|---|---|
| Eşleştirilmiş fark (Student) | 1,23 p=0,042 d=0,42 | 1,28 p=0,0066 d=0,57 | 1,42 p=0,011 | 1,41 p=0,005 d=0,59 |
| M1 hız ayarlı PD farkı | 1,28 [0,30; 2,27] p=0,011 | 0,86 [0,04; 1,68] p=0,041 | 1,34 p=0,009 | 1,02 p=0,028 |
| Dışarıda − aralıkta (PD) | 1,77 p=0,020 | 2,38 p=0,002 | 2,02 p=0,010 | 2,60 p=0,001 |
| Birincil şiddet (10 UPDRS) | 0,98 [0,35; 1,62] p=0,003 | 0,69 [0,08; 1,30] p=0,027 | 0,79 p=0,034 | 0,47 p=0,16 |
| İkincil (Holm) motor, H&Y | 0,027; 0,11 | 0,29; 0,29 | 0,13; 0,068 | 0,54; 0,21 |
### E3 tanılar
- Artıklar normal değil (Shapiro p < 0,01, tüm modeller) → HC3, bootstrap ve log(CV) ile karşılandı; değişen varyans yok (BP p 0,08–0,13); VIF ≤ 1,56; en büyük Cook 0,20.
- Hız spline (df = 3): PD farkı CV_ana 1,50, CV_cop 1,19; şiddet 0,86 / 0,59 (p < 0,05) → doğrusal hız varsayımı sonucu değiştirmiyor (spline ile fark biraz daha büyük).
- log(CV): PD +%18 (CV_ana) / +%23 (CV_cop); 10 UPDRS başına +%10 / +%11 (hepsi p < 0,02).
- **Plandan sapma 3:** `cr()` spline tabanı ilk sürümde sabit terimle doğrusal bağımlıydı (4 SingularMatrixWarning). `constraints="center"` ile düzeltildi; katsayılar 1,513 → 1,497 gibi yalnız üçüncü basamakta değişti. Uyarı sayısı 0.
### E4 heterojenlik
- PD farkı ve şiddet eğimi üç alt çalışmada aynı yönde; DerSimonian-Laird birleşik: CV_ana M1 1,26 [0,32; 2,19], şiddet 0,90 [0,30; 1,50]; CV_cop M1 1,09 [0,36; 1,82], şiddet 0,67 [0,11; 1,22]. I² %0–7, Q p > 0,34, etkileşim p > 0,08.
- Doğrulama: statsmodels `combine_effects` (DL) aynı sonucu verdi: 1,255 [0,317; 2,194], I² %4,5.
### E5 aracılık
- CV_ana: toplam 1,98, doğrudan 1,28, dolaylı (hız) 0,70 [0,02; 1,41] → %35. CV_cop: 1,95 / 0,86 / 1,09 [0,38; 1,84] → %56.
- Doğrulama: toplam = doğrudan + dolaylı (1,283 + 0,698 = 1,981; 0,860 + 1,089 = 1,949) — OLS özdeşliği sağlanıyor.
### E6 seçim yanlılığı
- Örtüşme ağırlıklı PD farkı: CV_ana 1,54 [0,49; 2,60]; CV_cop 1,15 [0,40; 1,89].
- Doğrulama: ağırlıklandırma sonrası ortalama hız (1,1573 / 1,1573) ve alt çalışma oranları iki grupta birebir eşit (örtüşme ağırlıklarının kuramsal özelliği).
- Yaş ve alt çalışma ayarlı: dışarıdaki PD'lerin UPDRS'i 6,0 puan yüksek [0,8; 11,2], p = 0,023 (ayarsız 4,4, p = 0,10); H&Y farkı yok (p = 0,39).
- Şiddet eğimi aralık içinde/dışında farklı değil (p = 0,45 / 0,62); PD farkı aralık dışında farklı değil (p = 0,87 / 0,32).
### E8 kesinlik
- n = 90'da %80 güçle saptanabilecek en küçük eğim ≈ 0,89 (CV_ana) / 0,86 (CV_cop) CV puanı / 10 UPDRS (≈ 0,25 SS). Bulunan CV_ana eğimi (0,98) bunun üstünde; CV_cop eğimi (0,69) altında → CV_cop için çalışma bu büyüklükte etki için yetersiz güçlü.

## E11 — Olay tespiti eşiğine duyarlılık (`e11_esik_duyarliligi.py`, `e11_cikti.txt`, `tablo_e11_esik_duyarliligi.csv`, `sekil8_esik_duyarliligi.png`)
Plan çalıştırmadan önce git'e kaydedildi (`E11_ESIK_DUYARLILIGI_PLANI.md`, commit 5e1cd40). Gerekçe: danışmanın Aşama 3 geri bildirimi ("eşik duyarlılığı yok").

Hata ve düzeltme: İlk çalıştırmada 2. aşama bir sütun adı çakışmasıyla durdu (`n_aralik`, `ort_s` iki tabloda da vardı). 1. aşamanın kişi dosyası sağlamdı. Çakışan sütunlar birleştirmeden önce atıldı; hiçbir sonuç bu düzeltmeden önce görülmedi.

### Önceden belirlenen doğrulamalar
- 20 N: M0 / M1 / şiddet = 1,98 / 1,28 / 0,98 → ana sonuçla aynı (TAMAM).
- 50 N: 2,28 / 1,82 / 0,55 → önceki 50 N sonucuyla aynı (TAMAM).
- Kişi bazlı CV farkı: 20 N'de `CV_ana` ile, 50 N'de `CV_50N` ile en büyük fark 0.
- Mutlak eşik yükseldikçe ortalama tek destek süresi tekdüze arttı: 0,369 → 0,425 s. Kalkış erken, basış geç bulunduğu için beklenen gidiş budur.

### Sonuç (plandaki yorum kuralına göre)
- **Hasta–kontrol farkı eşiğe dayanıklı.** Yön 11 eşiğin 11'inde pozitif. Hız ayarlı M1 GA'sı 11/11 eşikte 0'ı dışarıda bırakıyor (M1 1,24–1,90).
- **Şiddet eğimi eşiğe bağlı.** Tahmin her eşikte pozitif (0,52–1,02 / 10 UPDRS). GA'sı 0'ı dışarıda bırakan eşikler 5/11: 10, 15, 20, 30 N ve %2,5 VA. 40 N ve üstünde, ayrıca %5 ve %10 VA'da GA 0'ı kapsıyor (p = 0,052–0,18). Bu, sonuçta olduğu gibi raporlanmalı.
- Olası açıklama (test edilmedi): yüksek eşikte basış ve kalkış, kuvvetin yükselme ve düşme eğiminin daha dik olmayan kısmında bulunuyor. Bu durumda zamanlamaya kişinin yükleme hızındaki farklar da karışıyor. Eşikten bağımsız olay tespiti (ör. kuvvet türevi tabanlı) ileride sınanacak bir iş olarak not edildi.

## Çıktılı defter ve tam yeniden üretim testi (`12_Defter/`, 29 Ekim 2026)
- `defter_olustur.py`, betikleri dosyadan okuyarak defter hücrelerini kuruyor: hücre 1–7, E0, E1, E2b (tepe eşiği 1,25), E3–E9, E11, E10.
- Defter boş klasörde baştan çalıştırıldı (nbclient): 17 kod hücresi, hatalı hücre 0. Ham veri diske yazılmadı.
- `kisi_cv_tum_e2.csv` daha önce elle birleştirilmişti. Bu adım defterde açık bir hücre olarak yazıldı.
- Yeniden üretim: 9 tablonun 9'unda sayısal en büyük fark 0, metin sütunları aynı. Karşılaştırılan tablolar: `kisi_cv_tum`, `kisi_cv_tum_e2`, `tablo_patoz_tekrari`, `tablo_tum_orneklem_modeller`, `tablo_siddet_modelleri`, `tablo_e1_guvenilirlik`, `tablo_e_cekirdek`, `tablo_duyarlilik_ozeti`, `tablo_e11_esik_duyarliligi`.
