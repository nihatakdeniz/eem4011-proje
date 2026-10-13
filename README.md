# Parkinson’da Sol Tek Destek Süresi Değişkenliği

## Veri seti

Gait in Parkinson’s Disease (GaitPDB), v1.0.0: https://physionet.org/content/gaitpdb/1.0.0/

Ham veri dosyaları bu depoda yoktur. Notebook, gerekli açık veri dosyalarını çalışma sırasında PhysioNet aynasından okur. Kaynak veri lisansı: Open Data Commons Attribution License (ODC-By) 1.0.

## Çalıştırma

1. parkinson_tek_destek_cv.ipynb dosyasını Google Colab’da açın.
2. İnternet bağlantısı açıkken Çalışma zamanı → Tümünü çalıştır seçin.

Kod, Ga grubunda Speed_01 bilgisi bulunan kişilerin _01.txt kayıtlarını işler. Sağ toplam kuvvet sinyalinde 20 N eşik geçişleriyle sağ basış ve parmak kalkışı bulunur; bunlardan sol tek destek süresi ve kişi başına CV hesaplanır.

## Ana sonuç

Parkinson eksi kontrol CV farkı, ham karşılaştırmada **7.536 yüzde puan**; Speed_01 için ayarlanan doğrusal modelde **9.522 yüzde puan** bulundu. Bunlar bu veri ve yöntemle elde edilmiş grup karşılaştırmalarıdır; tanı sonucu değildir.

## Depodaki dosyalar

- parkinson_tek_destek_cv.ipynb: analiz kodu; kod hücresi çıktıları temizlenmiştir.
- sekil1.png: ham CV farkı.
- sekil2.png: hız ayarlı CV farkı.
- colab_calisirken.png: Colab çalışırken alınan sonuç ekran görüntüsü.

