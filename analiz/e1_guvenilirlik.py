"""E1 — Tek destek CV'sinin yarı-bölünmüş güvenilirliği: ICC(2,1) mutlak uyum + Spearman-Brown."""
import pickle
import numpy as np
import pandas as pd
from ortak import cv

def icc_2_1(Y):
    # Y: n kişi × k ölçüm. Shrout & Fleiss ICC(2,1), iki yönlü rastgele, mutlak uyum, tek ölçüm
    n, k = Y.shape
    gm = Y.mean()
    msr = k * ((Y.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((Y.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    sse = ((Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + gm) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)

def bootstrap_icc(Y, tekrar=2000, tohum=4011):
    rng = np.random.default_rng(tohum)
    return np.percentile([icc_2_1(Y[rng.integers(0, len(Y), len(Y))]) for _ in range(tekrar)], [2.5, 97.5])

olaylar = pickle.load(open("adim_olaylari.pkl", "rb"))
tablo = pd.read_csv("kisi_cv_tum.csv")
satir = []
for k in tablo.ID:
    s = olaylar[k]["sol_tek_destek"][:, 1]
    h = len(s) // 2
    satir.append({"ID": k, "ilk": cv(s[:h]), "ikinci": cv(s[h:]), "tek": cv(s[0::2]), "cift": cv(s[1::2])})
y = tablo[["ID", "Grup"]].merge(pd.DataFrame(satir), on="ID")
sonuc = []
for bolme, (a, b) in {"İlk yarı / ikinci yarı": ("ilk", "ikinci"), "Tek / çift sıra": ("tek", "cift")}.items():
    for grup in ["Tümü", "PD", "Kontrol"]:
        v = y if grup == "Tümü" else y[y.Grup == grup]
        Y = v[[a, b]].to_numpy()
        icc = icc_2_1(Y)
        alt, ust = bootstrap_icc(Y)
        sonuc.append({"Bölme": bolme, "Grup": grup, "n": len(v), "ICC(2,1)": round(icc, 3),
                      "%95 GA (bootstrap)": f"[{alt:.3f}, {ust:.3f}]", "Spearman-Brown (tam kayıt)": round(2 * icc / (1 + icc), 3)})
sonuc = pd.DataFrame(sonuc)
print(sonuc.to_string(index=False))
sonuc.to_csv("tablo_e1_guvenilirlik.csv", index=False)
# Doğrulama: ICC fonksiyonu, Shrout & Fleiss (1979) Tablo 2'deki örnek veriyle sınanır (ICC(2,1) = 0,29)
SF = np.array([[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]], float)
print("\nDoğrulama — Shrout & Fleiss örnek verisi ICC(2,1):", round(icc_2_1(SF), 2), "(yayımlanan 0,29)")
