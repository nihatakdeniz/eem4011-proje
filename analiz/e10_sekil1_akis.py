"""Şekil 1 — Katılımcı akış şeması (STROBE 13a). Sayılar demografi ve kisi_cv_tum_e2.csv'den hesaplanır."""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

URL = "https://physionet-open.s3.amazonaws.com/gaitpdb/1.0.0/"
dem = pd.read_csv(URL + "demographics.txt", sep="\t", usecols=range(20))
dem = dem[dem.ID.notna()]
t = pd.read_csv("kisi_cv_tum_e2.csv")
n = lambda v, g: int((v.Group == g).sum())
hiz_yok = dem[dem.Speed_01.isna()]
kutu = [
    (0.5, 0.92, f"GaitPDB v1.0.0 demografi\n{len(dem)} kişi ({n(dem, 1)} PD, {n(dem, 2)} kontrol)"),
    (0.5, 0.66, f"Olağan yürüyüş hızı (Speed_01) dolu\n{len(dem) - len(hiz_yok)} kişi"),
    (0.5, 0.40, f"Analiz örneklemi\n{len(t)} kişi ({(t.Grup == 'PD').sum()} PD, {(t.Grup == 'Kontrol').sum()} kontrol)\nGa {int((t.Study == 'Ga').sum())} · Ju {int((t.Study == 'Ju').sum())} · Si {int((t.Study == 'Si').sum())}"),
    (0.25, 0.12, f"Hız eşleştirmesi (1,0–1,3 m/s)\n{int((t.Patoz_araliginda & (t.Grup == 'PD')).sum())} PD + {int((t.Patoz_araliginda & (t.Grup == 'Kontrol')).sum())} kontrol"),
    (0.75, 0.12, f"Şiddet analizi (yalnız PD, UPDRS dolu)\n{int(((t.Grup == 'PD') & t.UPDRS.notna()).sum())} PD"),
]
dis = [(0.86, 0.79, f"Çıkarıldı: hız eksik\n{len(hiz_yok)} PD ({', '.join(hiz_yok.ID)})"),
       (0.86, 0.53, "Çıkarıldı: kayıt dosyası yok\n1 kontrol (Juc010)")]
fig, ax = plt.subplots(figsize=(8, 6.5))
ax.axis("off")
for x, y, s in kutu + dis:
    ax.add_patch(FancyBboxPatch((x - 0.2, y - 0.07), 0.4 if (x, y, s) in kutu else 0.26, 0.14, boxstyle="round,pad=0.01",
                                fc="#fcfcfb", ec="#52514e", lw=1, transform=ax.transAxes) if (x, y, s) in kutu else
                 FancyBboxPatch((x - 0.13, y - 0.06), 0.26, 0.12, boxstyle="round,pad=0.01", fc="#f0efec", ec="#52514e", lw=1, transform=ax.transAxes))
    ax.text(x, y, s, ha="center", va="center", fontsize=9, transform=ax.transAxes)
for (y0, y1) in [(0.85, 0.73), (0.59, 0.47)]:
    ax.annotate("", xy=(0.5, y1), xytext=(0.5, y0), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#52514e"))
for y in [0.79, 0.53]:
    ax.annotate("", xy=(0.73, y), xytext=(0.5, y), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#52514e"))
for x in [0.25, 0.75]:
    ax.annotate("", xy=(x, 0.19), xytext=(0.5, 0.33), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#52514e"))
plt.tight_layout()
plt.savefig("sekil1_katilimci_akisi.png", dpi=160)
print("Sayılar:", [s.replace("\n", " | ") for _, _, s in kutu + dis])
