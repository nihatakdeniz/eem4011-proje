"""Şekil 7 — COP tabanlı dönüş tespitinin doğrulaması."""
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from e2b_donus_tespiti_v2 import skor, KORIDOR

GRI, MUREKKEP = "#52514e", "#0b0b0b"
RENK = {"PD": "#eb6834", "Kontrol": "#2a78d6"}
ISARET = {"PD": "o", "Kontrol": "s"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRI})
with open("e2_donus_v2.pkl", "rb") as f:
    s = pickle.load(f)
with open("adim_olaylari.pkl", "rb") as f:
    ol = pickle.load(f)
s["beklenen_tam"] = np.floor(s.beklenen)
fig = plt.figure(figsize=(11, 6.5))
ax1 = fig.add_subplot(2, 2, 1)
rng = np.random.default_rng(1)
for g in ["Kontrol", "PD"]:
    v = s[s.Grup == g]
    ax1.scatter(v.beklenen_tam + rng.normal(0, 0.08, len(v)), v.n_donus + rng.normal(0, 0.08, len(v)), s=28, marker=ISARET[g],
                color=RENK[g], edgecolor="white", linewidth=0.8, label=f"{g} (n = {len(v)})")
m = int(max(s.beklenen_tam.max(), s.n_donus.max())) + 1
ax1.plot([0, m], [0, m], color=GRI, ls="--", lw=1)
ax1.set_xlabel("Beklenen dönüş (hız × süre / koridor, aşağı yuvarlanmış)")
ax1.set_ylabel("Bulunan dönüş")
ax1.legend(frameon=False, fontsize=9)
ax1.set_title(f"A. Dönüş sayısı: ±1 içinde %{100 * ((s.n_donus - s.beklenen_tam).abs() <= 1).mean():.0f}", fontsize=10, color=MUREKKEP)
ax2 = fig.add_subplot(2, 2, 2)
ax2.hist(s.oran_arasi.dropna(), bins=np.arange(0.5, 2.05, 0.05), color=GRI, edgecolor="white")
ax2.axvline(1, color=MUREKKEP, ls="--", lw=1)
ax2.set_xlabel("Dönüşler arası süre / (koridor / hız)")
ax2.set_ylabel("Kişi sayısı")
ax2.set_title(f"B. Dönüş aralığı: medyan {s.oran_arasi.median():.2f}", fontsize=10, color=MUREKKEP)
ax3 = fig.add_subplot(2, 1, 2)
k = "GaCo12"
d, sk = skor(ol[k]["duruslar"])
r = s.set_index("ID").loc[k]
ax3.plot(d.bas_t, sk, color=MUREKKEP, lw=1, label="Bileşik sapma skoru")
ax3.axhline(1.25, color=GRI, ls="--", lw=1, label="Tepe eşiği 1,25")
for i, (a, b, c) in enumerate(r.pencereler):
    ax3.axvspan(a, b, color="#eda100", alpha=0.3, label="Çıkarılan dönüş penceresi" if i == 0 else None)
ax3.set_xlabel("Zaman (s)")
ax3.set_ylabel("Skor (|z| ortalaması)")
ax3.legend(frameon=False, fontsize=9, loc="upper right", ncol=3)
ax3.set_title(f"C. Örnek: {k}, {r.n_donus} dönüş bulundu (beklenen {int(r.beklenen)})", fontsize=10, color=MUREKKEP)
plt.tight_layout()
plt.savefig("sekil7_donus_tespiti.png", dpi=160)
print("sekil7_donus_tespiti.png kaydedildi")
