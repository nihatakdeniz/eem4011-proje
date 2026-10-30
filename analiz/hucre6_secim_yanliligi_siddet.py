import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

tablo = pd.read_csv("kisi_cv_tum.csv")
pdg = tablo[tablo.Grup == "PD"].copy()
pdg["Hiz_grubu"] = np.select([pdg.Speed_01 < 1.0, pdg.Speed_01 > 1.3], ["yavaş (<1,0)", "hızlı (>1,3)"], "aralıkta")

# ---------- (c) Seçim yanlılığı: hız eşleştirmesine giren ve dışarıda kalan PD hastaları ----------
print("(c) SEÇİM YANLILIĞI — PD hastaları")
print("Hız grubuna göre sayı:", pdg.Hiz_grubu.value_counts().to_dict())
ozet = pdg.groupby("Hiz_grubu")[["UPDRS", "UPDRSM", "HoehnYahr", "Age", "CV_ana", "CV_donus_ayikli"]].agg(["mean", "count"]).round(2)
print(ozet.to_string())

ic, dis = pdg[pdg.Patoz_araliginda], pdg[~pdg.Patoz_araliginda]
print("\nAralıkta (n = %d) ve dışarıda (n = %d) karşılaştırma:" % (len(ic), len(dis)))
for olcu in ["UPDRS", "UPDRSM", "HoehnYahr", "Age", "CV_ana", "CV_donus_ayikli"]:
    a, b = dis[olcu].dropna(), ic[olcu].dropna()
    w = stats.ttest_ind(a, b, equal_var=False)
    mw = stats.mannwhitneyu(a, b)
    print(f"  {olcu:16s} dışarıda {a.mean():6.2f} | aralıkta {b.mean():6.2f} | fark {a.mean() - b.mean():6.2f} | Welch p {w.pvalue:.3g} | Mann-Whitney p {mw.pvalue:.3g}")
yavas = pdg[pdg.Hiz_grubu == "yavaş (<1,0)"]
for olcu in ["UPDRS", "HoehnYahr"]:
    a, b = yavas[olcu].dropna(), ic[olcu].dropna()
    print(f"  Yalnız yavaşlar vs aralıkta — {olcu}: {a.mean():.2f} vs {b.mean():.2f}, Mann-Whitney p {stats.mannwhitneyu(a, b).pvalue:.3g}")

# ---------- (b) Şiddet ilişkisi: yalnız PD, hız ayarlı ----------
# Önceden belirlenen birincil analiz: CV_ana ~ UPDRS (toplam) + Speed_01 + Study. Diğerleri ikincil.
print("\n(b) ŞİDDET — yalnız PD (katsayı: 10 UPDRS puanı veya 1 H&Y basamağı başına CV değişimi)")
pdg["UPDRS10"] = pdg.UPDRS / 10
pdg["UPDRSM10"] = pdg.UPDRSM / 10

def bootstrap_katsayi(veri, formul, terim, tekrar=2000, tohum=4011):
    rng = np.random.default_rng(tohum)
    b = [smf.ols(formul, data=veri.iloc[rng.integers(0, len(veri), len(veri))]).fit().params[terim] for _ in range(tekrar)]
    return np.percentile(b, [2.5, 97.5])

satirlar = []
for y in ["CV_ana", "CV_donus_ayikli"]:
    for x, ad in [("UPDRS10", "UPDRS toplam (10 puan)"), ("UPDRSM10", "UPDRS motor (10 puan)"), ("HoehnYahr", "Hoehn-Yahr (1 basamak)")]:
        veri = pdg.dropna(subset=[x, y, "Speed_01"])
        for hiz in [False, True]:
            formul = f"{y} ~ {x}" + (" + Speed_01" if hiz else "") + " + C(Study)"
            m = smf.ols(formul, data=veri).fit(cov_type="HC3", use_t=True)
            alt, ust = m.conf_int().loc[x]
            bs = bootstrap_katsayi(veri, formul, x) if hiz else (np.nan, np.nan)
            satirlar.append({
                "Sonuç": y, "Şiddet": ad, "Hız ayarı": "var" if hiz else "yok", "n": int(m.nobs),
                "Katsayı": round(m.params[x], 3), "HC3 %95 GA": f"[{alt:.3f}, {ust:.3f}]", "p": f"{m.pvalues[x]:.3g}",
                "Bootstrap %95 GA": f"[{bs[0]:.3f}, {bs[1]:.3f}]" if hiz else "",
                "Birincil": "EVET" if (y == "CV_ana" and x == "UPDRS10" and hiz) else "",
            })
sonuc = pd.DataFrame(satirlar)
print(sonuc.to_string(index=False))

print("\nUPDRS dağılımı alt çalışmaya göre (PD):")
print(pdg.groupby("Study")[["UPDRS", "UPDRSM", "HoehnYahr"]].agg(["mean", "min", "max"]).round(1).to_string())
print("\nHız ile şiddet ilişkisi (PD): Spearman UPDRS–hız r = %.3f (p %.3g), H&Y–hız r = %.3f (p %.3g)" % (
    *stats.spearmanr(pdg.UPDRS, pdg.Speed_01, nan_policy="omit"), *stats.spearmanr(pdg.HoehnYahr, pdg.Speed_01, nan_policy="omit")))
sonuc.to_csv("tablo_siddet_modelleri.csv", index=False)
pdg.to_csv("pd_hiz_gruplari.csv", index=False)
