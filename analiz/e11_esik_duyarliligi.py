"""E11 — Olay tespiti eşiğine duyarlılık (plan: E11_ESIK_DUYARLILIGI_PLANI.md).

Ön işleme ana yöntemle aynı (ortak.py); yalnız olay eşiği değişir.
1. aşama: her kişi ve her eşik için sol tek destek CV'si → e11_kisi_cv_esik.csv
2. aşama: her eşikte grup ortalamaları, eşleştirmeli Welch farkı, M0/M1 PD katsayısı, şiddet katsayısı
          → tablo_e11_esik_duyarliligi.csv, sekil8_esik_duyarliligi.png
Çalıştırma: python e11_esik_duyarliligi.py   (1. aşama dosyası varsa veri yeniden okunmaz)
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ortak import ATLA, kayit_oku, on_isleme, temas, tek_destek_araliklari, cv

MUTLAK = [10, 15, 20, 30, 40, 50, 75, 100]      # N
GORELI = [0.025, 0.05, 0.10]                     # vücut ağırlığı oranı
KISI_DOSYA = "e11_kisi_cv_esik.csv"

tablo = pd.read_csv("kisi_cv_tum.csv")           # Hücre 3 örneklemi (164 kişi) ve demografi

# ---------- 1. aşama: kişi bazlı CV ----------
if not os.path.exists(KISI_DOSYA):
    satirlar = []
    for i, s in tablo.iterrows():
        d = kayit_oku(s.ID)
        zaman = d[:, 0]
        bas = zaman >= ATLA
        z, sag_f = zaman[bas], on_isleme(d[:, 18])[bas]
        esikler = [(f"{e}N", e) for e in MUTLAK]
        if pd.notna(s.Weight):
            esikler += [(f"%{100 * o:g}VA", s.Weight * 9.81 * o) for o in GORELI]
        for ad, e in esikler:
            _, basis, kalkis = temas(sag_f, esik=e)
            sure = tek_destek_araliklari(z, basis, kalkis)[:, 1]
            satirlar.append({"ID": s.ID, "esik": ad, "esik_N": e, "n_aralik": len(sure),
                             "ort_s": sure.mean() if len(sure) else np.nan, "CV": cv(sure)})
        if i % 20 == 0:
            print(f"{i + 1}/{len(tablo)} kişi okundu", flush=True)
    pd.DataFrame(satirlar).to_csv(KISI_DOSYA, index=False)

kisi = pd.read_csv(KISI_DOSYA)

# ---------- 2. aşama: modeller ----------
tablo["PD"] = (tablo.Grup == "PD").astype(int)
tablo["UPDRS10"] = tablo.UPDRS / 10

def katsayi(veri, formul, terim):
    m = smf.ols(formul, data=veri).fit(cov_type="HC3", use_t=True)
    alt, ust = m.conf_int().loc[terim]
    return m.params[terim], alt, ust, m.pvalues[terim]

sira = [f"{e}N" for e in MUTLAK] + [f"%{100 * o:g}VA" for o in GORELI]
sonuc = []
for ad in sira:
    v = tablo.drop(columns=["n_aralik", "ort_s"]).merge(kisi[kisi.esik == ad][["ID", "esik_N", "n_aralik", "ort_s", "CV"]], on="ID").dropna(subset=["CV"])
    es = v[v.Patoz_araliginda]
    pd_e, ko_e = es[es.PD == 1].CV, es[es.PD == 0].CV
    w = stats.ttest_ind(pd_e, ko_e, equal_var=False)
    wf = pd_e.mean() - ko_e.mean()
    wa, wu = w.confidence_interval()
    m0 = katsayi(v, "CV ~ PD + C(Study)", "PD")
    m1 = katsayi(v, "CV ~ PD + Speed_01 + C(Study)", "PD")
    pdg = v[(v.PD == 1) & v.UPDRS.notna()]
    sd = katsayi(pdg, "CV ~ UPDRS10 + Speed_01 + C(Study)", "UPDRS10")
    sonuc.append({
        "Eşik": ad, "Eşik N (medyan)": round(v.esik_N.median(), 1), "n": len(v), "n PD": int(v.PD.sum()),
        "Medyan aralık sayısı": int(v.n_aralik.median()), "Ort. tek destek (s)": round(v.ort_s.mean(), 3),
        "CV PD": round(v[v.PD == 1].CV.mean(), 2), "CV kontrol": round(v[v.PD == 0].CV.mean(), 2),
        "Eşleştirmeli fark": wf, "E alt": wa, "E üst": wu, "E p": w.pvalue,
        "M0": m0[0], "M0 alt": m0[1], "M0 üst": m0[2], "M0 p": m0[3],
        "M1": m1[0], "M1 alt": m1[1], "M1 üst": m1[2], "M1 p": m1[3],
        "Şiddet": sd[0], "Ş alt": sd[1], "Ş üst": sd[2], "Ş p": sd[3], "n şiddet": len(pdg),
    })
s = pd.DataFrame(sonuc)
s.round(4).to_csv("tablo_e11_esik_duyarliligi.csv", index=False)

pd.set_option("display.width", 250)
print("\nEşik başına özet (fark ve katsayılar CV yüzde puanı; [HC3 veya Welch %95 GA])")
for _, r in s.iterrows():
    print(f"{r['Eşik']:>7} (~{r['Eşik N (medyan)']:>5} N) n={r.n:3d} aralık={r['Medyan aralık sayısı']:3d} "
          f"ort={r['Ort. tek destek (s)']:.3f}s | CV PD {r['CV PD']:5.2f} K {r['CV kontrol']:5.2f} | "
          f"Eşl {r['Eşleştirmeli fark']:5.2f} [{r['E alt']:5.2f};{r['E üst']:5.2f}] p={r['E p']:.2g} | "
          f"M0 {r.M0:5.2f} [{r['M0 alt']:5.2f};{r['M0 üst']:5.2f}] p={r['M0 p']:.2g} | "
          f"M1 {r.M1:5.2f} [{r['M1 alt']:5.2f};{r['M1 üst']:5.2f}] p={r['M1 p']:.2g} | "
          f"Şiddet {r['Şiddet']:5.2f} [{r['Ş alt']:5.2f};{r['Ş üst']:5.2f}] p={r['Ş p']:.2g}")

# ---------- Doğrulama (planda önceden belirlenen) ----------
print("\nDoğrulama:")
ana = s.set_index("Eşik")
for ad, beklenen in [("20N", (1.98, 1.28, 0.98)), ("50N", (2.28, 1.82, 0.55))]:
    bulunan = tuple(round(ana.loc[ad, k], 2) for k in ["M0", "M1", "Şiddet"])
    print(f"  {ad}: beklenen M0/M1/şiddet {beklenen}, bulunan {bulunan} → {'TAMAM' if bulunan == beklenen else 'FARKLI'}")
eski = pd.read_csv("kisi_cv_tum.csv").set_index("ID")
k20 = kisi[kisi.esik == "20N"].set_index("ID").CV
k50 = kisi[kisi.esik == "50N"].set_index("ID").CV
print(f"  Kişi bazlı en büyük fark: 20N vs CV_ana {np.nanmax(np.abs(k20 - eski.CV_ana.reindex(k20.index))):.2e}, "
      f"50N vs CV_50N {np.nanmax(np.abs(k50 - eski.CV_50N.reindex(k50.index))):.2e}")
m = s.iloc[:len(MUTLAK)]["Ort. tek destek (s)"].values
print("  Mutlak eşik yükseldikçe ortalama tek destek süresi artıyor mu:", bool(np.all(np.diff(m) > 0)), m.round(3).tolist())
print("  PD–kontrol farkının yönü (M0, M1, eşleştirmeli) tüm eşiklerde pozitif mi:",
      bool((s[["M0", "M1", "Eşleştirmeli fark"]] > 0).all().all()))
print("  M1 GA'sı 0'ı dışarıda bırakan eşik sayısı:", int((s["M1 alt"] > 0).sum()), "/", len(s))
print("  Şiddet GA'sı 0'ı dışarıda bırakan eşik sayısı:", int((s["Ş alt"] > 0).sum()), "/", len(s))

# ---------- Şekil 8 ----------
fig, eksen = plt.subplots(1, 3, figsize=(13, 4.2), sharex=True)
x = np.arange(len(s))
paneller = [("M0", "M0 alt", "M0 üst", "A. PD − kontrol, hızsız (M0)"),
            ("M1", "M1 alt", "M1 üst", "B. PD − kontrol, hız ayarlı (M1)"),
            ("Şiddet", "Ş alt", "Ş üst", "C. 10 UPDRS puanı başına (PD, hız ayarlı)")]
for ax, (k, a, u, baslik) in zip(eksen, paneller):
    renk = ["#C0392B" if e == "20N" else ("#555555" if e.endswith("N") else "#2E86C1") for e in s["Eşik"]]
    for xi, (_, r), c in zip(x, s.iterrows(), renk):
        ax.errorbar(xi, r[k], yerr=[[r[k] - r[a]], [r[u] - r[k]]], fmt="o", color=c, capsize=3)
    ax.axhline(0, color="k", lw=0.8, ls="--")
    ax.axvline(len(MUTLAK) - 0.5, color="#BBBBBB", lw=0.8)
    ax.set_title(baslik, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([e.replace("VA", " VA") for e in s["Eşik"]], rotation=45, fontsize=8)
    ax.set_xlabel("Olay eşiği (mutlak N | vücut ağırlığı oranı)", fontsize=8)
eksen[0].set_ylabel("Tahmin, CV yüzde puanı (%95 GA)")
fig.text(0.5, -0.04, "Kırmızı: ana yöntem (20 N). Ön işleme tüm varyantlarda aynı; yalnız olay eşiği değişir. "
         "GA: HC3 dayanıklı standart hata, t dağılımı.", ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("sekil8_esik_duyarliligi.png", dpi=200, bbox_inches="tight")
print("\nKaydedildi: tablo_e11_esik_duyarliligi.csv, sekil8_esik_duyarliligi.png")
