import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy import stats

# Renkler: başvuru paletinin doğrulanmış ilk iki kategorik rengi; grup kimliği ayrıca işaret şekliyle de verilir
RENK = {"PD": "#eb6834", "Kontrol": "#2a78d6"}
ISARET = {"PD": "o", "Kontrol": "s"}
GRI, MUREKKEP = "#52514e", "#0b0b0b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRI, "axes.labelcolor": MUREKKEP,
                     "xtick.color": GRI, "ytick.color": GRI, "axes.spines.top": False, "axes.spines.right": False})

tablo = pd.read_csv("kisi_cv_tum.csv")
tablo["PD"] = (tablo.Grup == "PD").astype(int)
pdg = tablo[tablo.PD == 1].copy()
pdg["UPDRS10"] = pdg.UPDRS / 10
es = tablo[tablo.Patoz_araliginda]

def welch_fark(veri, y):
    a, b = veri.loc[veri.PD == 1, y], veri.loc[veri.PD == 0, y]
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    df = se ** 4 / ((a.var(ddof=1) / len(a)) ** 2 / (len(a) - 1) + (b.var(ddof=1) / len(b)) ** 2 / (len(b) - 1))
    fark = a.mean() - b.mean()
    return fark, fark - stats.t.ppf(0.975, df) * se, fark + stats.t.ppf(0.975, df) * se, stats.ttest_ind(a, b, equal_var=False).pvalue

def katsayi(veri, formul, terim):
    m = smf.ols(formul, data=veri).fit(cov_type="HC3", use_t=True)
    alt, ust = m.conf_int().loc[terim]
    return m.params[terim], alt, ust, m.pvalues[terim]

# ---------- Duyarlılık özet tablosu ----------
OLCULER = [("CV_ana", "Ana yöntem"), ("CV_donus_ayikli", "Dönüş ayıklamalı"), ("CV_kuralsiz", "Kalite kuralı yok"),
           ("CV_50N", "50 N eşik"), ("CV_sag_tek_destek", "Sağ tek destek"), ("CV_eski", "Eski yöntem (filtresiz)")]
fmt = lambda s: f"{s[0]:.2f} [{s[1]:.2f}; {s[2]:.2f}] p={s[3]:.2g}"
satirlar = []
for y, ad in OLCULER:
    satirlar.append({
        "Ölçü": ad,
        "Eşleştirilmiş fark (Welch)": fmt(welch_fark(es, y)),
        "Tüm örneklem M0": fmt(katsayi(tablo, f"{y} ~ PD + C(Study)", "PD")),
        "Tüm örneklem M1 (hız ayarlı)": fmt(katsayi(tablo, f"{y} ~ PD + Speed_01 + C(Study)", "PD")),
        "Şiddet: 10 UPDRS başına (hız ayarlı, PD)": fmt(katsayi(pdg.dropna(subset=["UPDRS"]), f"{y} ~ UPDRS10 + Speed_01 + C(Study)", "UPDRS10")),
    })
duyarlilik = pd.DataFrame(satirlar)
duyarlilik.to_csv("tablo_duyarlilik_ozeti.csv", index=False)
with pd.option_context("display.width", 250, "display.max_colwidth", 60):
    print(duyarlilik.to_string(index=False))

# ---------- Şekil 4: eşleştirme ve hız ayarı karşılaştırması ----------
p_pd, p_ko = (5.0, 2.1, 54), (3.6, 1.1, 39)
se_p = np.sqrt(p_pd[1] ** 2 / p_pd[2] + p_ko[1] ** 2 / p_ko[2])
patoz = (p_pd[0] - p_ko[0], p_pd[0] - p_ko[0] - 1.96 * se_p, p_pd[0] - p_ko[0] + 1.96 * se_p)
fig, eks = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, (y, ad) in zip(eks, [("CV_donus_ayikli", "Dönüş ayıklamalı CV"), ("CV_ana", "Ana CV (dönüşler dahil)")]):
    satir = [("Tüm örneklem, hız ayarlı (n = 164)", katsayi(tablo, f"{y} ~ PD + Speed_01 + C(Study)", "PD")),
             ("Tüm örneklem, hız ayarsız (n = 164)", katsayi(tablo, f"{y} ~ PD + C(Study)", "PD")),
             ("Hız eşleştirmeli, bu çalışma (n = 96)", welch_fark(es, y))]
    satir.append(("Hız eşleştirmeli, Patoz 2023 (n = 93)*", patoz if y == "CV_donus_ayikli" else None))
    for i, (etiket, deger) in enumerate(satir):
        if deger is None:
            ax.text(0.05, i, "makalede bu ölçü yok", va="center", color=GRI, fontsize=9)
            continue
        b, a, u = deger[:3]
        renk = GRI if "Patoz" in etiket else MUREKKEP
        ax.plot([a, u], [i, i], color=renk, lw=2, solid_capstyle="round")
        ax.plot(b, i, "o", color=renk, ms=8, mec="white", mew=2)
        ax.text(u + 0.08, i, f"{b:.2f}", va="center", color=GRI, fontsize=9)
    ax.axvline(0, color=GRI, lw=1, ls="--")
    ax.set_yticks(range(len(satir)), [s[0] for s in satir])
    ax.set_title(ad, color=MUREKKEP, fontsize=10)
    ax.set_xlabel("PD − kontrol farkı (CV yüzde puanı), %95 GA")
fig.text(0.01, 0.01, "* Patoz için GA, makaledeki ortalama ± SS değerlerinden yaklaşık hesaplandı.", fontsize=8, color=GRI)
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig("sekil4_eslestirme_vs_hiz_ayari.png", dpi=160)
plt.close()

# ---------- Şekil 5: hız eşleştirmesinin dışarıda bıraktıkları ----------
fig, eks = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1.6, 1]})
ax = eks[0]
ax.axvspan(1.0, 1.3, color="#f0efec", zorder=0)
ax.text(1.15, tablo.CV_donus_ayikli.max() * 0.97, "Patoz aralığı\n1,0–1,3 m/s", ha="center", va="top", color=GRI, fontsize=9)
for g in ["Kontrol", "PD"]:
    v = tablo[tablo.Grup == g]
    ax.scatter(v.Speed_01, v.CV_donus_ayikli, s=40, marker=ISARET[g], color=RENK[g], edgecolor="white", linewidth=1, label=f"{g} (n = {len(v)})", zorder=2)
ax.set_xlabel("Yürüme hızı, Speed_01 (m/s)")
ax.set_ylabel("Dönüş ayıklamalı tek destek CV (%)")
ax.legend(frameon=False, loc="center right", bbox_to_anchor=(1.02, 0.66))
ax.set_title("Hız eşleştirmesi kimleri dışarıda bırakıyor?", color=MUREKKEP, fontsize=10)
ax = eks[1]
gruplar = [("aralıkta", pdg[pdg.Patoz_araliginda]), ("dışarıda", pdg[~pdg.Patoz_araliginda])]
for i, (ad, v) in enumerate(gruplar):
    x = np.random.default_rng(i).normal(i, 0.06, len(v))
    ax.scatter(x, v.Age, s=30, marker="o", color=RENK["PD"], alpha=0.75, edgecolor="white", linewidth=0.8)
    ax.plot([i - 0.2, i + 0.2], [v.Age.mean()] * 2, color=MUREKKEP, lw=2)
ax.set_xticks([0, 1], [f"Aralıkta\n(n = {len(gruplar[0][1])})", f"Dışarıda\n(n = {len(gruplar[1][1])})"])
ax.set_ylabel("Yaş (yıl)")
ax.set_title(f"PD hastalarının yaşı (Welch p = {stats.ttest_ind(gruplar[1][1].Age, gruplar[0][1].Age, equal_var=False).pvalue:.4f})", color=MUREKKEP, fontsize=10)
plt.tight_layout()
plt.savefig("sekil5_secim_yanliligi.png", dpi=160)
plt.close()

# ---------- Şekil 6: CV ile UPDRS (hız ve alt çalışma ayarlı kısmi ilişki) ----------
v = pdg.dropna(subset=["UPDRS"]).copy()
v["CV_art"] = smf.ols("CV_ana ~ Speed_01 + C(Study)", data=v).fit().resid
v["UPDRS_art"] = smf.ols("UPDRS10 ~ Speed_01 + C(Study)", data=v).fit().resid
m = smf.ols("CV_art ~ UPDRS_art", data=v).fit()
xs = np.linspace(v.UPDRS_art.min(), v.UPDRS_art.max(), 100)
tah = m.get_prediction(pd.DataFrame({"UPDRS_art": xs})).summary_frame()
b, a, u, p = katsayi(v, "CV_ana ~ UPDRS10 + Speed_01 + C(Study)", "UPDRS10")
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.fill_between(xs * 10, tah.mean_ci_lower, tah.mean_ci_upper, color=RENK["PD"], alpha=0.15, lw=0)
ax.plot(xs * 10, tah["mean"], color=RENK["PD"], lw=2)
ax.scatter(v.UPDRS_art * 10, v.CV_art, s=40, color=RENK["PD"], edgecolor="white", linewidth=1)
ax.axhline(0, color=GRI, lw=0.8, ls=":")
ax.set_xlabel("UPDRS toplam (hız ve alt çalışmaya göre ayarlı, puan)")
ax.set_ylabel("Ana tek destek CV (ayarlı, yüzde puan)")
ax.set_title(f"PD (n = {len(v)}): 10 UPDRS puanı başına {b:.2f} [{a:.2f}; {u:.2f}], p = {p:.3f}", color=MUREKKEP, fontsize=10)
plt.tight_layout()
plt.savefig("sekil6_cv_updrs.png", dpi=160)
plt.close()
print("\nKısmi regresyon eğimi (Frisch–Waugh kontrolü):", round(m.params.UPDRS_art, 3), "| tam model:", round(b, 3))
print("Kaydedildi: sekil4_eslestirme_vs_hiz_ayari.png, sekil5_secim_yanliligi.png, sekil6_cv_updrs.png, tablo_duyarlilik_ozeti.csv")
