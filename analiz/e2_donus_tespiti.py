"""E2 — Basınç merkezi (COP) tabanlı dönüş tespiti ve CV'den bağımsız doğrulama.

Kural (EK_ANALIZ_PLANI.md): duruş süresi, adım süresi ve lateral COP özellikleri kişinin
kayan medyanına göre dayanıklı z'ye çevrilir (pencere 15 adım); bileşik |z| ortalaması > ESIK_Z
olan adımlar işaretlenir, aralarında ≤ 2 adım olanlar birleştirilir, iki yana 1 adım tampon eklenir.
Doğrulama: bulunan dönüş sayısı ve aralığı, 25 m koridor varsayımıyla hız × süreden beklenene karşı.
"""
import pickle
import sys
import numpy as np
import pandas as pd
from scipy import stats
from ortak import cv

PENCERE, BIRLESTIR, TAMPON, KORIDOR = 15, 2, 1, 25.0
ESIK_Z = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5

def dayanikli_z(x):
    s = pd.Series(x)
    med = s.rolling(PENCERE, center=True, min_periods=5).median()
    mad = (s - med).abs().rolling(PENCERE, center=True, min_periods=5).median() * 1.4826
    return ((s - med) / mad.clip(lower=1e-3)).to_numpy()

def donusler(duruslar):
    d = duruslar.copy()
    d["adim_s"] = d.bas_t.diff()          # karşı ayağın basışından bu basışa
    ozellik = np.column_stack([dayanikli_z(d[c].to_numpy()) for c in ["durus_s", "adim_s", "lat_cop"]])
    bilesik = np.nanmean(np.abs(ozellik), axis=1)
    isaret = np.where(bilesik > ESIK_Z)[0]
    olaylar = []
    for i in isaret:
        if olaylar and i - olaylar[-1][1] <= BIRLESTIR + 1:
            olaylar[-1][1] = i
        else:
            olaylar.append([i, i])
    pencereler = []
    for a, b in olaylar:
        a, b = max(a - TAMPON, 0), min(b + TAMPON, len(d) - 1)
        pencereler.append((d.bas_t.iloc[a], d.bas_t.iloc[b] + d.durus_s.iloc[b]))
    return pencereler

def donus_disi(araliklar, pencereler):
    if not len(araliklar):
        return araliklar
    bas, son = araliklar[:, 0], araliklar[:, 0] + araliklar[:, 1]
    tut = np.ones(len(araliklar), bool)
    for a, b in pencereler:
        tut &= ~((bas < b) & (son > a))
    return araliklar[tut]

olaylar = pickle.load(open("adim_olaylari.pkl", "rb"))
tablo = pd.read_csv("kisi_cv_tum.csv")
satir = []
for _, r in tablo.iterrows():
    o = olaylar[r.ID]
    p = donusler(o["duruslar"])
    merkez = np.array([(a + b) / 2 for a, b in p])
    tut = donus_disi(o["sol_tek_destek"], p)
    satir.append({"ID": r.ID, "Study": r.Study, "Grup": r.Grup, "n_donus": len(p),
                  "beklenen": r.Speed_01 * o["sure_s"] / KORIDOR,
                  "donus_arasi_s": np.median(np.diff(merkez)) if len(merkez) > 1 else np.nan,
                  "beklenen_arasi_s": KORIDOR / r.Speed_01,
                  "n_tutulan": len(tut), "n_toplam": len(o["sol_tek_destek"]),
                  "CV_cop": cv(tut[:, 1]), "pencereler": p})
s = pd.DataFrame(satir)
s["oran_arasi"] = s.donus_arasi_s / s.beklenen_arasi_s
r_s = stats.spearmanr(s.n_donus, s.beklenen)
print(f"Eşik z = {ESIK_Z}")
print(f"(a) Bulunan vs beklenen dönüş sayısı: Spearman r = {r_s[0]:.3f} (p {r_s[1]:.2g}); ortalama mutlak fark = {(s.n_donus - s.beklenen).abs().mean():.2f}; ortalama bulunan {s.n_donus.mean():.2f}, beklenen {s.beklenen.mean():.2f}")
print("    Alt çalışmaya göre (bulunan / beklenen ortalama):", s.groupby("Study").apply(lambda v: f"{v.n_donus.mean():.1f}/{v.beklenen.mean():.1f}").to_dict())
print(f"(b) Dönüşler arası süre / (25 m / hız): medyan {s.oran_arasi.median():.2f}, çeyrekler {s.oran_arasi.quantile(.25):.2f}–{s.oran_arasi.quantile(.75):.2f}")
print(f"    Atılan aralık oranı: medyan %{100 * (1 - s.n_tutulan / s.n_toplam).median():.1f}; en az kalan aralık {s.n_tutulan.min()}")
AYAR = len(sys.argv) > 2 and sys.argv[2] == "ayar"   # ayar modunda CV sonuçları gösterilmez
if not AYAR:
    print("    Grup ortalaması CV_cop:", s.groupby("Grup").CV_cop.mean().round(2).to_dict())
    s.drop(columns="pencereler").to_csv(f"e2_donus_ozet_z{ESIK_Z}.csv", index=False)
    pickle.dump(s, open(f"e2_donus_z{ESIK_Z}.pkl", "wb"))
