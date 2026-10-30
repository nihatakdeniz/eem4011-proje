import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

tablo = pd.read_csv("kisi_cv_tum.csv")
tablo["PD"] = (tablo.Grup == "PD").astype(int)

M0 = "{y} ~ PD + C(Study)"             # hızsız, alt çalışma ayarlı
M1 = "{y} ~ PD + Speed_01 + C(Study)"  # hız ve alt çalışma ayarlı

def pd_katsayisi(veri, formul):
    m = smf.ols(formul, data=veri).fit(cov_type="HC3", use_t=True)
    alt, ust = m.conf_int().loc["PD"]
    return m.params["PD"], alt, ust, m.pvalues["PD"], m

def bootstrap(veri, y, tekrar=2000, tohum=4011):
    # Yeniden örnekleme birimi kişidir; her tekrarda iki model aynı kişilerle kurulur
    rng = np.random.default_rng(tohum)
    sonuc = []
    for _ in range(tekrar):
        o = veri.iloc[rng.integers(0, len(veri), len(veri))]
        b0 = smf.ols(M0.format(y=y), data=o).fit().params["PD"]
        b1 = smf.ols(M1.format(y=y), data=o).fit().params["PD"]
        sonuc.append((b0, b1, b1 - b0))
    return np.percentile(np.array(sonuc), [2.5, 97.5], axis=0)

satirlar = []
for y, ad in [("CV_ana", "Ana CV"), ("CV_donus_ayikli", "Dönüş ayıklamalı CV")]:
    b0, a0, u0, p0, _ = pd_katsayisi(tablo, M0.format(y=y))
    b1, a1, u1, p1, m1 = pd_katsayisi(tablo, M1.format(y=y))
    bs = bootstrap(tablo, y)
    satirlar.append({
        "Ölçü": ad,
        "M0 PD farkı [HC3 %95 GA]": f"{b0:.3f} [{a0:.3f}, {u0:.3f}]",
        "M0 p": f"{p0:.2g}",
        "M1 PD farkı [HC3 %95 GA]": f"{b1:.3f} [{a1:.3f}, {u1:.3f}]",
        "M1 p": f"{p1:.2g}",
        "M1 bootstrap %95 GA": f"[{bs[0, 1]:.3f}, {bs[1, 1]:.3f}]",
        "M1−M0": f"{b1 - b0:.3f}",
        "M1−M0 bootstrap %95 GA": f"[{bs[0, 2]:.3f}, {bs[1, 2]:.3f}]",
        "Hız katsayısı (M1)": f"{m1.params['Speed_01']:.3f} (p {m1.pvalues['Speed_01']:.2g})",
    })
sonuc = pd.DataFrame(satirlar)
print("Örneklem:", tablo.Grup.value_counts().to_dict(), "| alt çalışma:", tablo.Study.value_counts().to_dict())
print("Ortalama hız:", tablo.groupby("Grup").Speed_01.mean().round(3).to_dict())
for _, s in sonuc.iterrows():
    print("\n==", s["Ölçü"])
    for k, v in s.items():
        if k != "Ölçü":
            print(f"  {k}: {v}")

# Duyarlılık: hızın etkisi gruplar arasında farklı mı? (etkileşim terimi)
etk = smf.ols("CV_ana ~ PD * Speed_01 + C(Study)", data=tablo).fit(cov_type="HC3", use_t=True)
print(f"\nDuyarlılık — PD × hız etkileşimi (Ana CV): {etk.params['PD:Speed_01']:.3f}, p = {etk.pvalues['PD:Speed_01']:.2g}")
sonuc.to_csv("tablo_tum_orneklem_modeller.csv", index=False)
