import io
import numpy as np
import requests
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

URL = "https://physionet-open.s3.amazonaws.com/gaitpdb/1.0.0/"
FS = 100        # örnekleme hızı (Hz)
ESIK = 20       # olay eşiği (N)
ATLA = 5        # baştan atılan süre (s)

def kayit_oku(kimlik):
    metin = requests.get(URL + f"{kimlik}_01.txt").text
    return np.loadtxt(io.StringIO(metin))

def patoz_on_isleme(kuvvet):
    k = np.where(kuvvet < ESIK, 0, kuvvet)
    b, a = butter(4, 15 / (FS / 2))
    return filtfilt(b, a, k)

def olaylar(kuvvet):
    yerde = kuvvet > ESIK
    basis = np.where(~yerde[:-1] & yerde[1:])[0] + 1
    kalkis = np.where(yerde[:-1] & ~yerde[1:])[0] + 1
    return basis, kalkis

def tek_destek(zaman, basis, kalkis):
    sureler = []
    for k in kalkis:
        sonraki = basis[basis > k]
        if len(sonraki) > 0:
            sureler.append(zaman[sonraki[0]] - zaman[k])
    return np.array(sureler)

def cv(x):
    return 100 * x.std(ddof=1) / x.mean()

kimlik = "GaPt04"
d = kayit_oku(kimlik)
zaman, sag = d[:, 0], d[:, 18]

ham_b, ham_k = olaylar(sag)
ham_ts = tek_destek(zaman, ham_b, ham_k)

bas = zaman >= ATLA
z2, sag_f = zaman[bas], patoz_on_isleme(sag)[bas]
f_b, f_k = olaylar(sag_f)
f_ts = tek_destek(z2, f_b, f_k)

print(f"{kimlik} — sol tek destek süresi")
print(f"  Eski yöntem (filtre yok, baştan atma yok): {len(ham_ts)} aralık, ortalama {ham_ts.mean():.3f} s, CV %{cv(ham_ts):.2f}")
print(f"  Patoz ön işlemesi (20 N + 15 Hz + ilk 5 s): {len(f_ts)} aralık, ortalama {f_ts.mean():.3f} s, CV %{cv(f_ts):.2f}")
print(f"  En kısa / en uzun aralık (Patoz): {f_ts.min():.3f} s / {f_ts.max():.3f} s")

pencere = (zaman >= 10) & (zaman <= 16)
fig, eks = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
eks[0].plot(zaman[pencere], sag[pencere], color="lightgray", lw=4, label="Ham sinyal")
eks[0].plot(z2[(z2 >= 10) & (z2 <= 16)], sag_f[(z2 >= 10) & (z2 <= 16)], color="tab:blue", label="Patoz ön işlemesi")
eks[0].axhline(ESIK, color="red", ls="--", label="20 N eşik")
eks[0].set_ylabel("Sağ ayak kuvveti (N)")
eks[0].legend(loc="upper right")
eks[0].set_title(f"{kimlik}: sağ ayak kuvveti ve bulunan olaylar (10–16 s)")
eks[1].plot(z2[(z2 >= 10) & (z2 <= 16)], sag_f[(z2 >= 10) & (z2 <= 16)], color="tab:blue")
for i in f_b:
    if 10 <= z2[i] <= 16:
        eks[1].axvline(z2[i], color="green", lw=1)
for i in f_k:
    if 10 <= z2[i] <= 16:
        eks[1].axvline(z2[i], color="orange", lw=1)
eks[1].plot([], [], color="green", label="Sağ basış")
eks[1].plot([], [], color="orange", label="Sağ parmak kalkışı")
eks[1].set_xlabel("Zaman (s)")
eks[1].set_ylabel("Kuvvet (N)")
eks[1].legend(loc="upper right")
plt.tight_layout()
plt.savefig("sekil3_olay_kontrolu.png", dpi=150)
plt.show()
