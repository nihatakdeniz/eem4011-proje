"""E2 sürüm 2 — Dönüş tespiti (plandan sapma, gerekçesi DOGRULAMA_GUNLUGU.md'de).

Sürüm 1 doğrulamayı geçemedi (fazla dönüş; dönüşler arası süre beklenenin ~0,55'i).
Değişiklikler (CV sonuçlarına bakılmadan, yalnız doğrulama ölçüleri ve sinyal grafiğiyle):
  1) Dayanıklı z'de MAD alt sınırı: süreler 0,02 s, lateral COP 0,05 (çok düzenli yürüyende z patlıyordu).
  2) Bileşik skor 3 adımlık kayan ortalamayla yumuşatılır; dönüşler tepe noktası olarak bulunur.
  3) Fiziksel kısıt: iki dönüş tepe noktası arası en az 0,6 × (25 m / hız) saniye.
  4) Dönüş penceresi: tepenin iki yanında skor > 1,5 olduğu sürece (her yana en çok 4 adım) + 1 adım tampon.
Ayarlanabilir tek parametre: tepe yüksekliği ESIK (yalnız doğrulama ölçülerine göre seçilir).
"""
import pickle
import sys
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from ortak import cv

PENCERE, TAMPON, YAN_ESIK, YAN_EN_COK = 15, 1, 1.5, 4
# Koridor uzunluğu: Ga, Ju 25 m (Patoz 2023); Si 35 m (Frenkel-Toledo 2005, J NeuroEng Rehabil: "35 meter walkway")
KORIDOR = {"Ga": 25.0, "Ju": 25.0, "Si": 35.0}
TABAN = {"durus_s": 0.02, "adim_s": 0.02, "lat_cop": 0.05}
ESIK = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
AYAR = len(sys.argv) > 2 and sys.argv[2] == "ayar"

def dayanikli_z(x, taban):
    s = pd.Series(x)
    med = s.rolling(PENCERE, center=True, min_periods=5).median()
    mad = (s - med).abs().rolling(PENCERE, center=True, min_periods=5).median() * 1.4826
    return ((s - med) / mad.clip(lower=taban)).to_numpy()

def skor(duruslar):
    d = duruslar.copy()
    d["adim_s"] = d.bas_t.diff()
    z = np.column_stack([np.abs(dayanikli_z(d[c].to_numpy(), TABAN[c])) for c in TABAN])
    return d, pd.Series(np.nanmean(z, axis=1)).rolling(3, center=True, min_periods=1).mean().fillna(0).to_numpy()

def donusler(duruslar, hiz, koridor):
    d, sk = skor(duruslar)
    adim = np.nanmedian(d.adim_s)
    en_az = max(1, int(0.6 * (koridor / hiz) / adim))
    tepeler, _ = find_peaks(sk, height=ESIK, distance=en_az)
    pencereler = []
    for t in tepeler:
        a = t
        while a > 0 and t - a < YAN_EN_COK and sk[a - 1] > YAN_ESIK:
            a -= 1
        b = t
        while b < len(sk) - 1 and b - t < YAN_EN_COK and sk[b + 1] > YAN_ESIK:
            b += 1
        a, b = max(a - TAMPON, 0), min(b + TAMPON, len(d) - 1)
        pencereler.append((d.bas_t.iloc[a], d.bas_t.iloc[b] + d.durus_s.iloc[b], d.bas_t.iloc[t]))
    return pencereler

def donus_disi(araliklar, pencereler):
    bas, son = araliklar[:, 0], araliklar[:, 0] + araliklar[:, 1]
    tut = np.ones(len(araliklar), bool)
    for a, b, _ in pencereler:
        tut &= ~((bas < b) & (son > a))
    return araliklar[tut]

if __name__ == "__main__":
    olaylar = pickle.load(open("adim_olaylari.pkl", "rb"))
    tablo = pd.read_csv("kisi_cv_tum.csv")
    satir = []
    for _, r in tablo.iterrows():
        o = olaylar[r.ID]
        p = donusler(o["duruslar"], r.Speed_01, KORIDOR[r.Study])
        tepe = np.array([c for _, _, c in p])
        tut = donus_disi(o["sol_tek_destek"], p)
        satir.append({"ID": r.ID, "Study": r.Study, "Grup": r.Grup, "n_donus": len(p),
                      "beklenen": r.Speed_01 * o["sure_s"] / KORIDOR[r.Study],
                      "oran_arasi": np.median(np.diff(tepe)) / (KORIDOR[r.Study] / r.Speed_01) if len(tepe) > 1 else np.nan,
                      "n_tutulan": len(tut), "n_toplam": len(o["sol_tek_destek"]), "CV_cop": cv(tut[:, 1]), "pencereler": p})
    s = pd.DataFrame(satir)
    r_s = stats.spearmanr(s.n_donus, s.beklenen)
    print(f"Tepe eşiği = {ESIK}")
    print(f"(a) Bulunan vs beklenen: Spearman r = {r_s[0]:.3f} (p {r_s[1]:.2g}); ort. mutlak fark {(s.n_donus - s.beklenen).abs().mean():.2f}; ort. bulunan {s.n_donus.mean():.2f} / beklenen {s.beklenen.mean():.2f}")
    print("    Alt çalışmaya göre:", s.groupby("Study").apply(lambda v: f"{v.n_donus.mean():.1f}/{v.beklenen.mean():.1f}", include_groups=False).to_dict())
    print("    Grup bazında bulunan/beklenen:", s.groupby("Grup").apply(lambda v: f"{v.n_donus.mean():.1f}/{v.beklenen.mean():.1f}", include_groups=False).to_dict())
    print(f"(b) Dönüşler arası / (koridor / hız): medyan {s.oran_arasi.median():.2f}, çeyrekler {s.oran_arasi.quantile(.25):.2f}–{s.oran_arasi.quantile(.75):.2f}")
    print(f"    Atılan aralık: medyan %{100 * (1 - s.n_tutulan / s.n_toplam).median():.1f}; en az kalan {s.n_tutulan.min()}")
    if not AYAR:
        print("    Grup ortalaması CV_cop:", s.groupby("Grup").CV_cop.mean().round(2).to_dict())
        s.drop(columns="pencereler").to_csv("e2_donus_ozet_v2.csv", index=False)
        pickle.dump(s, open("e2_donus_v2.pkl", "wb"))
