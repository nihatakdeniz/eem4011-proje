# Parkinson Hastalığında Tek Destek Süresi Değişkenliği: Yürüme Hızı, Hız Eşleştirmesinin Seçim Yanlılığı ve Hastalık Şiddeti

EEM4011 Biyomedikal Uygulamalarında Programlama dersi projesi · Nihat Akdeniz · Ekim 2026

Bu depoda yalnız kod, çıktılı analiz defteri, şekiller ve özet tablolar vardır. **Ham veri yoktur.** Kod veriyi çalışırken PhysioNet'ten belleğe okur.

## Soru

Parkinson hastaları hem daha yavaş hem de daha düzensiz adımlarla yürür. Ancak yavaş yürümek de düzensizliği artırır. Bu projede açık bir veri setinde şu üç soru incelendi:

1. **(b, birincil)** Parkinson grubunda sol tek destek süresinin değişim katsayısı (CV) hastalık şiddetiyle (UPDRS) ilişkili mi? Yürüme hızı ve kohort ayarlandığında ilişki sürüyor mu?
2. **(c)** Önceki bir çalışmanın (Patoz ve ark., 2023) 1,0–1,3 m/s hız eşleştirmesi, daha ağır hastaları dışarıda bırakıyor mu?
3. **(a)** Hasta–kontrol farkı hız ayarlandığında sürüyor mu? (Yeniden üretim; bu soru daha önce yanıtlanmıştır.)

## Veri

*Gait in Parkinson's Disease* (GaitPDB), PhysioNet, v1.0.0 — https://physionet.org/content/gaitpdb/1.0.0/
Lisans: Open Data Commons Attribution License (ODC-By) 1.0. Atıf:
- PhysioNet, "Gait in Parkinson's Disease (version 1.0.0)," 2008.
- Goldberger AL ve ark., "PhysioBank, PhysioToolkit, and PhysioNet," *Circulation* 101(23):e215–e220, 2000. doi:10.1161/01.CIR.101.23.e215

Analiz örneklemi: 164 kişi (92 Parkinson, 72 kontrol; üç kohort: Ga, Ju, Si). Çıkarılanlar: GaPt03 (hız bilgisi yok), Juc010 (kayıt dosyası yok). Şiddet analizi UPDRS'i dolu 90 hasta ile yapıldı.

## Yöntem (kısaca)

- **Ön işleme (Patoz 2023):** sağ ayak toplam kuvvetinde 20 N altı sıfırlanır; 15 Hz 4. derece Butterworth (filtfilt); ilk 5 s atılır; basış ve parmak kalkışı 20 N eşikle bulunur; 0,10 s'den kısa temas ya da uçuş gürültü sayılır.
- **Ölçü:** sol tek destek süresi = sağ parmak kalkışından sonraki sağ basışa kadar geçen süre. Kişi başına CV = 100 × SS / ortalama.
  - `CV_ana` (birincil): dönüşler dahil.
  - `CV_cop` (ikincil): basınç merkezi tabanlı, fiziksel ölçütlerle doğrulanmış dönüş tespitiyle dönüşler ayıklanmış.
- **Modeller:** `CV ~ PD + kohort` ve `CV ~ PD + hız + kohort`; şiddet: `CV ~ UPDRS/10 + hız + kohort`. En küçük kareler, HC3 dayanıklı standart hata. Bootstrap'ta birim kişidir (2000 tekrar, tohum 4011).
- **Ek analizler:** güvenilirlik (ICC), aracılık, örtüşme ağırlıklandırması, kohort bazında birleştirme (DerSimonian-Laird), spline, Holm düzeltmesi, 11 olay eşiğinde duyarlılık.
- Analiz planı sonuçlardan önce git ile zaman damgalı kaydedildi (`analiz/EK_ANALIZ_PLANI.md`, `analiz/E11_ESIK_DUYARLILIGI_PLANI.md`). Her sonuç `analiz/DOGRULAMA_GUNLUGU.md` dosyasında ikinci bir yoldan doğrulandı.

## Ana sonuçlar

CV yüzde puanı; köşeli parantez HC3 %95 güven aralığı.

| Bulgu | Sonuç |
|---|---|
| Dönüş ayıklama ölçüm güvenilirliğini artırdı | ICC 0,52 → 0,77 |
| Hız eşleştirmeli örneklem (54 hasta, 42 kontrol), dönüş ayıklamalı CV farkı | 1,28; p = 0,007 |
| Eşleştirmenin dışarıda bıraktığı 38 hasta | Daha yaşlı (70,3'e karşı 63,2 yıl; p = 0,0002); yaş ve kohort ayarlı UPDRS +6,0 (p = 0,023); CV'leri daha yüksek |
| Tüm örneklem, hız ayarsız → hız ayarlı fark (`CV_ana`) | 1,98 [1,08; 2,89] → 1,28 [0,30; 2,27], p = 0,011 |
| Aynısı, `CV_cop` | 1,95 → 0,86 [0,04; 1,68], p = 0,041 |
| **Şiddet: 10 UPDRS puanı başına, hız ve kohort ayarlı (`CV_ana`, n = 90)** | **0,98 [0,35; 1,62], p = 0,003** |
| Olay eşiği duyarlılığı (11 eşik) | Hız ayarlı fark 11 eşiğin 11'inde 0'dan büyük (1,24–1,90). Şiddet eğimi her eşikte pozitif (0,52–1,02), ama GA yalnız 5 eşikte 0'ı dışarıda bırakıyor → şiddet ilişkisinin kesinliği eşiğe bağlı |

Bulgular kesitseldir; tanı ya da neden-sonuç amacı taşımaz.

## Çalıştırma

Gerekenler: Python 3.12, numpy, pandas, scipy, statsmodels, matplotlib, jupyter. İnternet bağlantısı gerekir (veri PhysioNet'ten okunur).

1. Depoyu indirin; `eem4011_parkinson_analiz.ipynb`, `ortak.py` ve `e2b_donus_tespiti_v2.py` aynı klasörde olmalı.
2. Defteri Jupyter ya da Google Colab'da açıp tüm hücreleri çalıştırın.

Defter boş bir klasörde baştan çalıştırıldı: 17 kod hücresi hatasız çalıştı ve ürettiği 9 sonuç tablosunun hepsi `tablolar/` klasöründekilerle birebir aynı çıktı.

## Dosyalar

| Dosya / klasör | İçerik |
|---|---|
| `eem4011_parkinson_analiz.ipynb` | Çıktılı analiz defteri (tüm adımlar, açıklamalar, şekiller) |
| `ortak.py`, `e2b_donus_tespiti_v2.py` | Defterin kullandığı ortak fonksiyonlar ve dönüş tespiti |
| `analiz/` | Adım adım analiz betikleri, önceden kayıtlı analiz planları, doğrulama günlüğü |
| `sekiller/` | Şekil 1, 3–8 (katılımcı akışı, olay kontrolü, eşleştirme ile hız ayarı, seçim yanlılığı, CV–UPDRS, dönüş tespiti, eşik duyarlılığı) |
| `tablolar/` | Özet sonuç tabloları (CSV) |
| `eski_asama2/` | **Geçersiz** ilk analiz (Aşama 2) — aşağıya bakın |

## Eski Aşama 2 sonucu hakkında

Depodaki ilk analiz (`eski_asama2/`) yalnız Ga kohortunu, süzgeçsiz sinyali ve dönüşler dahil adımları kullanıyordu. O analizde hız ayarı farkı büyütmüş görünüyordu (7,536 → 9,522 yüzde puan). Doğru ön işlemeyle aynı kişilerde hız ayarı farkı **küçültmektedir** (2,07 → 0,99). Eski sonuç gürültüden etkilenmiştir ve geçersizdir; karşılaştırma için saklanmıştır.

## Kaynaklar

- Patoz A, Malatesta D, Burtscher J. Isolating the speed factor is crucial in gait analysis for Parkinson's disease. *Front Neurosci* 17:1119390, 2023. doi:10.3389/fnins.2023.1119390
- Frenkel-Toledo S ve ark. Effect of gait speed on gait rhythmicity in Parkinson's disease. *J NeuroEng Rehabil* 2:23, 2005. doi:10.1186/1743-0003-2-23
- Lopes JF ve ark. Association between Parkinson's disease functional disability staging and gait kinematics parameters. *Braz J Motor Behav* 19(1):e465, 2025. doi:10.20338/bjmb.v19i1.465
