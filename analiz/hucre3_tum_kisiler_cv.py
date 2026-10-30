import io
import numpy as np
import pandas as pd
import requests
from scipy.signal import butter, filtfilt

URL = "https://physionet-open.s3.amazonaws.com/gaitpdb/1.0.0/"
FS, ATLA = 100, 5
B, A = butter(4, 15 / (FS / 2))

# Bu kurallar grup sonuçlarına bakılmadan önce yazıldı ve sonradan değiştirilmez.
# Ana yöntem: Patoz ön işlemesi (20 N altı sıfır, 15 Hz Butterworth, ilk 5 s atılır), 20 N olay eşiği.
# Duyarlılık: eski yöntem; 50 N olay eşiği; dönüş ayıklama (medyan ± 3 × ölçekli MAD dışı aralıklar atılır); sağ tek destek.
# Kalite kuralları (23 Ekim, ilk çalıştırmadaki kişi bazlı kontrolden sonra eklendi; grup karşılaştırması yapılmadan):
#  - 0,10 s'den kısa yer teması veya havada kalma gürültü sayılır (JuPt25'te salınımda ayak sürtmesi sahte olay üretiyordu).
#  - Dönüş ayıklamada ölçekli MAD en az 0,01 s alınır (10 ms çözünürlükte MAD = 0 olabiliyordu; SiCo15).
EN_KISA = 10    # örnek = 0,10 s

def kayit_oku(kimlik):
    return np.loadtxt(io.StringIO(requests.get(URL + f"{kimlik}_01.txt").text))

def on_isleme(kuvvet):
    return filtfilt(B, A, np.where(kuvvet < 20, 0, kuvvet))

def kisa_parcalari_sil(yerde, deger):
    # deger durumundaki EN_KISA'dan kısa ardışık parçaları karşı duruma çevirir
    yerde = yerde.copy()
    i = 0
    while i < len(yerde):
        if yerde[i] == deger:
            j = i
            while j < len(yerde) and yerde[j] == deger:
                j += 1
            if j - i < EN_KISA and i > 0 and j < len(yerde):
                yerde[i:j] = not deger
            i = j
        else:
            i += 1
    return yerde

def olaylar(kuvvet, esik, kural=True):
    yerde = kuvvet > esik
    if kural:
        yerde = kisa_parcalari_sil(kisa_parcalari_sil(yerde, True), False)
    basis = np.where(~yerde[:-1] & yerde[1:])[0] + 1
    kalkis = np.where(yerde[:-1] & ~yerde[1:])[0] + 1
    return basis, kalkis

def tek_destek(zaman, kuvvet_karsi, esik, kural=True):
    # Bir bacağın tek destek süresi = karşı ayağın kalkışından sonraki basışına kadar geçen süre
    basis, kalkis = olaylar(kuvvet_karsi, esik, kural)
    sureler = []
    for k in kalkis:
        sonraki = basis[basis > k]
        if len(sonraki) > 0:
            sureler.append(zaman[sonraki[0]] - zaman[k])
    return np.array(sureler)

def cv(x):
    return 100 * x.std(ddof=1) / x.mean() if len(x) > 2 else np.nan

def donus_ayikla(x):
    mad = max(1.4826 * np.median(np.abs(x - np.median(x))), 0.01)
    return x[np.abs(x - np.median(x)) <= 3 * mad]

dem = pd.read_csv(URL + "demographics.txt", sep="\t", usecols=range(20))
dem = dem[dem.ID.notna() & dem.Speed_01.notna() & (dem.ID != "Juc010")].copy()
dem["Grup"] = dem.Group.map({1: "PD", 2: "Kontrol"})

satirlar = []
for kimlik in dem.ID:
    d = kayit_oku(kimlik)
    zaman, sol, sag = d[:, 0], d[:, 17], d[:, 18]
    bas = zaman >= ATLA
    z, sol_f, sag_f = zaman[bas], on_isleme(sol)[bas], on_isleme(sag)[bas]
    ana = tek_destek(z, sag_f, 20)
    satirlar.append({
        "ID": kimlik,
        "n_aralik": len(ana),
        "ort_s": ana.mean(),
        "CV_ana": cv(ana),
        "CV_eski": cv(tek_destek(zaman, sag, 20, kural=False)),
        "CV_kuralsiz": cv(tek_destek(z, sag_f, 20, kural=False)),
        "CV_50N": cv(tek_destek(z, sag_f, 50)),
        "CV_donus_ayikli": cv(donus_ayikla(ana)),
        "n_donus_ayikli": len(donus_ayikla(ana)),
        "CV_sag_tek_destek": cv(tek_destek(z, sol_f, 20)),
        "kayit_s": zaman[-1],
    })

tablo = dem.merge(pd.DataFrame(satirlar), on="ID")
tablo["Patoz_araliginda"] = tablo.Speed_01.between(1.0, 1.3)
tablo.to_csv("kisi_cv_tum.csv", index=False)

print("Kişi sayısı:", tablo.Grup.value_counts().to_dict())
print("\nAralık sayısı (ana yöntem): en az", tablo.n_aralik.min(), "| medyan", int(tablo.n_aralik.median()), "| en çok", tablo.n_aralik.max())
print("30'dan az aralığı olan kişiler:", tablo.loc[tablo.n_aralik < 30, ["ID", "n_aralik", "kayit_s"]].values.tolist())
print("\nGrup ortalamaları (CV %):")
print(tablo.groupby("Grup")[["CV_ana", "CV_kuralsiz", "CV_eski", "CV_50N", "CV_donus_ayikli", "CV_sag_tek_destek"]].mean().round(2).T)
degisen = tablo[(tablo.CV_ana - tablo.CV_kuralsiz).abs() > 0.5]
print("\nKalite kuralının CV'yi 0,5 puandan fazla değiştirdiği kişiler:", len(degisen))
print(degisen[["ID", "CV_kuralsiz", "CV_ana"]].round(2).values.tolist())
print("\nAlt çalışmaya göre ana CV ortalaması:")
print(tablo.groupby(["Study", "Grup"]).CV_ana.mean().round(2).unstack())
