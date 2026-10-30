import numpy as np
import pandas as pd
from scipy import stats

# Patoz ve ark. 2023: 1,0–1,3 m/s hızdaki katılımcılar, iki yönlü eşleştirilmemiş Student t-testi.
# Bildirilen tek destek süresi CV'si: PD %5,0 ± 2,1 (n = 54), kontrol %3,6 ± 1,1 (n = 39), p < 0,001.
PATOZ = {"PD": (5.0, 2.1, 54), "Kontrol": (3.6, 1.1, 39)}

tablo = pd.read_csv("kisi_cv_tum.csv")
es = tablo[tablo.Patoz_araliginda]

def cohen_d(a, b):
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp

print("Eşleştirilmiş örneklem:", es.Grup.value_counts().to_dict())
print("Ortalama hız (m/s):", es.groupby("Grup").Speed_01.mean().round(3).to_dict())
print("Hız farkı t-testi p =", round(stats.ttest_ind(es[es.Grup == "PD"].Speed_01, es[es.Grup == "Kontrol"].Speed_01).pvalue, 3))

satirlar = []
for olcu, ad in [("CV_donus_ayikli", "Dönüş ayıklamalı CV"), ("CV_ana", "Ana CV"), ("CV_sag_tek_destek", "Sağ tek destek CV"), ("ort_s", "Ortalama tek destek (s)")]:
    pd_ = es.loc[es.Grup == "PD", olcu]
    ko = es.loc[es.Grup == "Kontrol", olcu]
    student = stats.ttest_ind(pd_, ko)
    welch = stats.ttest_ind(pd_, ko, equal_var=False)
    satirlar.append({
        "Ölçü": ad,
        "PD ort ± SS": f"{pd_.mean():.2f} ± {pd_.std(ddof=1):.2f}",
        "Kontrol ort ± SS": f"{ko.mean():.2f} ± {ko.std(ddof=1):.2f}",
        "Fark": round(pd_.mean() - ko.mean(), 3),
        "Student p": f"{student.pvalue:.2g}",
        "Welch p": f"{welch.pvalue:.2g}",
        "Cohen d": round(cohen_d(pd_, ko), 2),
    })
sonuc = pd.DataFrame(satirlar)
print("\n" + sonuc.to_string(index=False))

pd_p, ko_p = PATOZ["PD"], PATOZ["Kontrol"]
sp = np.sqrt(((pd_p[2] - 1) * pd_p[1] ** 2 + (ko_p[2] - 1) * ko_p[1] ** 2) / (pd_p[2] + ko_p[2] - 2))
print(f"\nPatoz 2023 (bildirilen): PD {pd_p[0]} ± {pd_p[1]}, kontrol {ko_p[0]} ± {ko_p[1]}, fark {pd_p[0] - ko_p[0]:.1f}, Cohen d ≈ {(pd_p[0] - ko_p[0]) / sp:.2f}")
sonuc.to_csv("tablo_patoz_tekrari.csv", index=False)
