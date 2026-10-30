# E11 — Olay tespiti eşiğine duyarlılık: önceden kayıtlı plan

Yazıldığı tarih: 29 Ekim 2026. Bu plan, eşik taraması çalıştırılmadan önce yazıldı ve git ile zaman damgalandı.
Gerekçe: Danışman geri bildirimi (Aşama 3 formu): "başlıktaki olay tespiti etkisi için eşik duyarlılığı yok". Projede şimdiye kadar yalnız 20 N (ana) ve 50 N (duyarlılık) vardı.

## Değişen tek şey: olay eşiği
Ön işleme her varyantta ana yöntemle **birebir aynı** kalır: 20 N altı sıfırlanır, 15 Hz 4. derece Butterworth (filtfilt) uygulanır, ilk 5 s atılır, 0,10 s kalite kuralı uygulanır. Ölçü, sol tek destek süresinin CV'sidir (`CV_ana` tanımı; dönüşler dahil).

Eşik varyantları:
- **Mutlak eşikler:** 10, 15, 20 (ana), 30, 40, 50, 75 ve 100 N.
- **Vücut ağırlığına göre göreli eşikler:** kişinin ağırlığının %2,5, %5 ve %10'u (ağırlık × 9,81 × oran). Ağırlığı eksik 3 kişi bu varyantlarda dışarıda kalır; sayısı raporlanır.

## Her varyantta raporlanacaklar
1. CV hesaplanabilen kişi sayısı ve medyan aralık sayısı.
2. Grup ortalaması CV (PD, kontrol).
3. Hız eşleştirmeli fark: 1,0–1,3 m/s aralığındakilerde, Welch testi.
4. Tüm örneklem M0 `CV ~ PD + C(Study)` ve M1 `CV ~ PD + Speed_01 + C(Study)` için PD katsayısı. OLS, HC3, `use_t=True`.
5. Birincil şiddet modeli (yalnız PD): `CV ~ UPDRS/10 + Speed_01 + C(Study)`.

Eşik başına bootstrap yapılmaz; GA'lar HC3 GA'larıdır.

## Doğrulama (önceden belirlendi)
- 20 N satırı, mevcut ana sonuçları birebir vermeli: M0 1,98; M1 1,28; şiddet 0,98 (`tablo_duyarlilik_ozeti.csv`).
- 50 N satırı mevcut 50 N sonuçlarını vermeli: M0 2,28; M1 1,82; şiddet 0,55.
- Eşik yükseldikçe ortalama tek destek süresinin uzaması beklenir, çünkü kalkış erken, basış geç bulunur. Bu gidiş kontrol edilir.

## Yorum kuralı (önceden)
- Ana sonuç 20 N'dir; eşik taraması sonucu değiştirmez.
- PD–kontrol farkının yönü tüm eşiklerde aynıysa ve hız ayarlı GA'ların çoğu 0'ı dışarıda bırakıyorsa, bulgu "eşiğe dayanıklı" diye yazılır.
- Değilse, hangi eşik aralığında değiştiği olduğu gibi raporlanır.
- Şiddet katsayısı için de aynı kural uygulanır. 50 N'de GA'nın 0'ı kapsadığı zaten bilinmektedir; bu da raporlanır.
