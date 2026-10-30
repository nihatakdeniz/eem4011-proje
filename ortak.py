"""Ek analizler (E1–E10) için ortak fonksiyonlar.

Ön işleme ve olay kuralları Hücre 3 ile birebir aynıdır (20 N, 15 Hz Butterworth,
ilk 5 s, 0,10 s kalite kuralı). Ham kayıt yalnız bellekte işlenir; diske yalnız
kişi bazlı türetilmiş olay tabloları yazılır (adim_olaylari.pkl).
"""
import io
import numpy as np
import pandas as pd
import requests
from scipy.signal import butter, filtfilt

URL = "https://physionet-open.s3.amazonaws.com/gaitpdb/1.0.0/"
FS, ATLA, ESIK, EN_KISA = 100, 5, 20, 10
B, A = butter(4, 15 / (FS / 2))
# format.txt'teki algılayıcı X koordinatları (L1–L8, R1–R8); |X| büyüdükçe dış (lateral) taraf
X_SOL = np.array([-500, -700, -300, -700, -300, -700, -300, -500])
X_SAG = np.array([500, 700, 300, 700, 300, 700, 300, 500])


def kayit_oku(kimlik):
    return np.loadtxt(io.StringIO(requests.get(URL + f"{kimlik}_01.txt").text))


def on_isleme(kuvvet):
    return filtfilt(B, A, np.where(kuvvet < ESIK, 0, kuvvet))


def kisa_parcalari_sil(yerde, deger):
    yerde = yerde.copy()
    i = 0
    while i < len(yerde):
        if yerde[i] == deger:
            j = i
            while j < len(yerde) and yerde[j] == deger:
                j += 1
            if j - i < EN_KISA and i > 0 and j < len(yerde):
                yerde[i:j] = not deger
            i = j
        else:
            i += 1
    return yerde


def temas(kuvvet, esik=ESIK):
    """Kalite kurallı yer teması dizisi ve basış / kalkış örnek numaraları."""
    yerde = kisa_parcalari_sil(kisa_parcalari_sil(kuvvet > esik, True), False)
    basis = np.where(~yerde[:-1] & yerde[1:])[0] + 1
    kalkis = np.where(yerde[:-1] & ~yerde[1:])[0] + 1
    return yerde, basis, kalkis


def tek_destek_araliklari(zaman, karsi_basis, karsi_kalkis):
    """Karşı ayağın kalkışından sonraki basışına kadar: (başlangıç zamanı, süre)."""
    sonuc = []
    for k in karsi_kalkis:
        sonraki = karsi_basis[karsi_basis > k]
        if len(sonraki):
            sonuc.append((zaman[k], zaman[sonraki[0]] - zaman[k]))
    return np.array(sonuc).reshape(-1, 2)


def durus_fazlari(zaman, basis, kalkis, ham_algilayici, x):
    """Her tam duruş fazı: başlangıç, süre, ortalama lateral COP indeksi (|COPx| − 500) / 200."""
    sonuc = []
    for b in basis:
        k = kalkis[kalkis > b]
        if not len(k):
            break
        k = k[0]
        f = np.clip(ham_algilayici[b:k], 0, None)
        toplam = f.sum(axis=1)
        gecerli = toplam > 0
        copx = (f[gecerli] @ x) / toplam[gecerli] if gecerli.any() else np.array([np.nan])
        sonuc.append((zaman[b], zaman[k] - zaman[b], (np.abs(np.nanmean(copx)) - 500) / 200))
    return pd.DataFrame(sonuc, columns=["bas_t", "durus_s", "lat_cop"])


def kisi_olaylari(kimlik):
    d = kayit_oku(kimlik)
    zaman = d[:, 0]
    bas = zaman >= ATLA
    z = zaman[bas]
    sol_f, sag_f = on_isleme(d[:, 17])[bas], on_isleme(d[:, 18])[bas]
    _, sol_b, sol_k = temas(sol_f)
    _, sag_b, sag_k = temas(sag_f)
    sol_alg, sag_alg = d[bas, 1:9], d[bas, 9:17]
    sol_d = durus_fazlari(z, sol_b, sol_k, sol_alg, X_SOL).assign(ayak="sol")
    sag_d = durus_fazlari(z, sag_b, sag_k, sag_alg, X_SAG).assign(ayak="sag")
    return {
        "ID": kimlik,
        "sure_s": z[-1] - z[0],
        "sol_tek_destek": tek_destek_araliklari(z, sag_b, sag_k),   # ana ölçü
        "sag_tek_destek": tek_destek_araliklari(z, sol_b, sol_k),
        "duruslar": pd.concat([sol_d, sag_d]).sort_values("bas_t").reset_index(drop=True),
    }


def cv(x):
    x = np.asarray(x)
    return 100 * x.std(ddof=1) / x.mean() if len(x) > 2 else np.nan
