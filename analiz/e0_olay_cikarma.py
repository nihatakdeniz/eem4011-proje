"""164 kişinin adım düzeyindeki olaylarını çıkarır ve adim_olaylari.pkl'ye kaydeder.
Doğrulama: ana CV, Hücre 3'teki CV_ana ile karşılaştırılır (birebir aynı olmalı)."""
import pickle
import numpy as np
import pandas as pd
from ortak import kisi_olaylari, cv

tablo = pd.read_csv("kisi_cv_tum.csv")
olaylar = {k: kisi_olaylari(k) for k in tablo.ID}
with open("adim_olaylari.pkl", "wb") as f:
    pickle.dump(olaylar, f)
yeni = tablo.ID.map(lambda k: cv(olaylar[k]["sol_tek_destek"][:, 1]))
fark = (yeni - tablo.CV_ana).abs()
print("Kişi:", len(olaylar), "| Hücre 3 CV_ana ile en büyük fark:", round(fark.max(), 10))
print("Sağ tek destek en büyük fark:", round((tablo.ID.map(lambda k: cv(olaylar[k]["sag_tek_destek"][:, 1])) - tablo.CV_sag_tek_destek).abs().max(), 10))
print("Kişi başına duruş fazı sayısı: medyan", int(np.median([len(o["duruslar"]) for o in olaylar.values()])))
