"""E3–E9 — Sağlamlık analizleri (EK_ANALIZ_PLANI.md). Her analiz iki ölçü için yapılır:
CV_ana (önceden belirlenmiş birincil) ve CV_cop (E2, COP tabanlı dönüş ayıklamalı)."""
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.multitest import multipletests
from ortak import cv
from e2b_donus_tespiti_v2 import donus_disi

TOHUM, TEKRAR = 4011, 2000
t = pd.read_csv("kisi_cv_tum_e2.csv")
t["PD"] = (t.Grup == "PD").astype(int)
t["UPDRS10"], t["UPDRSM10"] = t.UPDRS / 10, t.UPDRSM / 10

# E9 — iki ayak birleşik CV (ana yöntem ve dönüş ayıklamalı)
with open("adim_olaylari.pkl", "rb") as f:
    ol = pickle.load(f)
with open("e2_donus_v2.pkl", "rb") as f:
    don = pickle.load(f).set_index("ID")
t["CV_iki_ayak"] = t.ID.map(lambda k: cv(np.r_[ol[k]["sol_tek_destek"][:, 1], ol[k]["sag_tek_destek"][:, 1]]))
t["CV_iki_ayak_cop"] = t.ID.map(lambda k: cv(np.r_[donus_disi(ol[k]["sol_tek_destek"], don.loc[k, "pencereler"])[:, 1],
                                                   donus_disi(ol[k]["sag_tek_destek"], don.loc[k, "pencereler"])[:, 1]]))
t.to_csv("kisi_cv_tum_e2.csv", index=False)
pdg = t[t.PD == 1]
OLCU = ["CV_ana", "CV_cop", "CV_iki_ayak", "CV_iki_ayak_cop"]

def fit(f, v):
    return smf.ols(f, data=v).fit(cov_type="HC3", use_t=True)

def k(m, terim):
    a, b = m.conf_int().loc[terim]
    return f"{m.params[terim]:.3f} [{a:.3f}; {b:.3f}] p={m.pvalues[terim]:.3g}"

def baslik(s):
    print("\n" + "=" * 8 + " " + s + " " + "=" * 8)

# ---------- Çekirdek analizler her ölçüyle ----------
baslik("ÇEKİRDEK ANALİZLER (Hücre 4–6 tekrarı)")
es = t[t.Patoz_araliginda]
cekirdek = []
for y in OLCU:
    a, b = es.loc[es.PD == 1, y], es.loc[es.PD == 0, y]
    st = stats.ttest_ind(a, b)
    sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    ic, dis = pdg[pdg.Patoz_araliginda][y], pdg[~pdg.Patoz_araliginda][y]
    m_bir = fit(f"{y} ~ UPDRS10 + Speed_01 + C(Study)", pdg.dropna(subset=["UPDRS"]))
    ikincil = {"UPDRS motor": fit(f"{y} ~ UPDRSM10 + Speed_01 + C(Study)", pdg.dropna(subset=["UPDRSM"])).pvalues["UPDRSM10"],
               "Hoehn-Yahr": fit(f"{y} ~ HoehnYahr + Speed_01 + C(Study)", pdg).pvalues["HoehnYahr"]}
    holm = multipletests(list(ikincil.values()), method="holm")[1]
    cekirdek.append({"Ölçü": y,
                     "PD ort / Kontrol ort (tüm)": f"{t[t.PD == 1][y].mean():.2f} / {t[t.PD == 0][y].mean():.2f}",
                     "Eşleştirilmiş (Student)": f"{a.mean() - b.mean():.3f} p={st.pvalue:.3g} d={(a.mean() - b.mean()) / sp:.2f}",
                     "M0": k(fit(f"{y} ~ PD + C(Study)", t), "PD"),
                     "M1 (hız ayarlı)": k(fit(f"{y} ~ PD + Speed_01 + C(Study)", t), "PD"),
                     "Dışarıda − aralıkta (PD)": f"{dis.mean() - ic.mean():.3f} Welch p={stats.ttest_ind(dis, ic, equal_var=False).pvalue:.3g}",
                     "Birincil şiddet (10 UPDRS)": k(m_bir, "UPDRS10"),
                     "İkincil Holm p (motor, H&Y)": ", ".join(f"{h:.3g}" for h in holm)})
cek = pd.DataFrame(cekirdek)
for _, r in cek.iterrows():
    print("\n--", r["Ölçü"])
    for c in cek.columns[1:]:
        print(f"   {c}: {r[c]}")
cek.to_csv("tablo_e_cekirdek.csv", index=False)

# ---------- E3 tanılar ----------
baslik("E3 MODEL TANILARI")
for y in ["CV_ana", "CV_cop"]:
    for ad, f, v in [("M1", f"{y} ~ PD + Speed_01 + C(Study)", t), ("Şiddet", f"{y} ~ UPDRS10 + Speed_01 + C(Study)", pdg.dropna(subset=["UPDRS"]))]:
        m = smf.ols(f, data=v).fit()
        X = m.model.exog
        vif = max(variance_inflation_factor(X, i) for i in range(1, X.shape[1]))
        terim = "PD" if ad == "M1" else "UPDRS10"
        spline = fit(f.replace("Speed_01", "cr(Speed_01, df=3, constraints=\"center\")"), v)
        logm = fit(f.replace(f"{y} ~", f"np.log({y}) ~"), v)
        print(f"{y} {ad}: Shapiro p={stats.shapiro(m.resid).pvalue:.3g} | Breusch-Pagan p={het_breuschpagan(m.resid, X)[1]:.3g} | "
              f"en büyük VIF={vif:.2f} | en büyük Cook={m.get_influence().cooks_distance[0].max():.3f}")
        print(f"      hız spline (df=3): {terim} {k(spline, terim)}")
        print(f"      log(CV): {terim} {logm.params[terim]:.4f} → %{100 * (np.exp(logm.params[terim]) - 1):.1f} değişim, p={logm.pvalues[terim]:.3g}")

# ---------- E4 heterojenlik ----------
baslik("E4 ALT ÇALIŞMA HETEROJENLİĞİ")
def dl_meta(b, se):
    w = 1 / se ** 2
    sabit = (w * b).sum() / w.sum()
    Q = (w * (b - sabit) ** 2).sum()
    df = len(b) - 1
    tau2 = max(0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum()))
    wr = 1 / (se ** 2 + tau2)
    est = (wr * b).sum() / wr.sum()
    se_r = np.sqrt(1 / wr.sum())
    return est, est - 1.96 * se_r, est + 1.96 * se_r, Q, stats.chi2.sf(Q, df), max(0, (Q - df) / Q) * 100 if Q > 0 else 0
for y in ["CV_ana", "CV_cop"]:
    for ad, f, terim, v in [("M1 PD farkı", f"{y} ~ PD + Speed_01", "PD", t), ("Şiddet eğimi", f"{y} ~ UPDRS10 + Speed_01", "UPDRS10", pdg.dropna(subset=["UPDRS"]))]:
        b, se, metin = [], [], []
        for s in ["Ga", "Ju", "Si"]:
            m = fit(f, v[v.Study == s])
            b.append(m.params[terim]); se.append(m.bse[terim]); metin.append(f"{s} {m.params[terim]:.2f}±{m.bse[terim]:.2f}")
        est, lo, hi, Q, pQ, I2 = dl_meta(np.array(b), np.array(se))
        etk = fit(f.replace(terim, f"{terim} * C(Study)"), v)
        etk_p = etk.f_test([c for c in etk.params.index if ":" in c] and np.eye(len(etk.params))[[i for i, c in enumerate(etk.params.index) if ":" in c]]).pvalue
        print(f"{y} {ad}: {', '.join(metin)} | DL birleşik {est:.2f} [{lo:.2f}; {hi:.2f}] | Q p={pQ:.3g}, I²=%{I2:.0f} | etkileşim F p={float(etk_p):.3g}")

# ---------- E5 aracılık ----------
baslik("E5 ARACILIK (PD → hız → CV)")
rng = np.random.default_rng(TOHUM)
for y in ["CV_ana", "CV_cop"]:
    def parcalar(v):
        a = smf.ols("Speed_01 ~ PD + C(Study)", data=v).fit().params["PD"]
        m = smf.ols(f"{y} ~ PD + Speed_01 + C(Study)", data=v).fit()
        top = smf.ols(f"{y} ~ PD + C(Study)", data=v).fit().params["PD"]
        return top, m.params["PD"], a * m.params["Speed_01"]
    top, dog, dol = parcalar(t)
    bs = np.array([parcalar(t.iloc[rng.integers(0, len(t), len(t))]) for _ in range(TEKRAR)])
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    print(f"{y}: toplam {top:.3f} [{lo[0]:.3f}; {hi[0]:.3f}] | doğrudan {dog:.3f} [{lo[1]:.3f}; {hi[1]:.3f}] | dolaylı (hız üzerinden) {dol:.3f} [{lo[2]:.3f}; {hi[2]:.3f}] | aracılık oranı %{100 * dol / top:.0f}")

# ---------- E6 seçim yanlılığı ----------
baslik("E6 SEÇİM YANLILIĞININ NİCELLEŞTİRİLMESİ")
ps = smf.logit("PD ~ Speed_01 + C(Study)", data=t).fit(disp=0).predict(t)
t["w_overlap"] = np.where(t.PD == 1, 1 - ps, ps)
for y in ["CV_ana", "CV_cop"]:
    wls = smf.wls(f"{y} ~ PD", data=t, weights=t.w_overlap).fit(cov_type="HC3", use_t=True)
    ar = fit(f"{y} ~ PD * Patoz_araliginda + Speed_01 + C(Study)", t)
    print(f"{y}: örtüşme ağırlıklı PD farkı {k(wls, 'PD')} | aralık dışı PD'de ek fark (PD×dışarıda) {(-ar.params['PD:Patoz_araliginda[T.True]']):.3f}, p={ar.pvalues['PD:Patoz_araliginda[T.True]']:.3g}")
for s in ["UPDRS", "HoehnYahr"]:
    m = fit(f"{s} ~ Patoz_araliginda + Age + C(Study)", pdg.dropna(subset=[s]))
    print(f"Aralıktaki − dışarıdaki PD, yaş+çalışma ayarlı {s}: {k(m, 'Patoz_araliginda[T.True]')}")
for y in ["CV_ana", "CV_cop"]:
    m = fit(f"{y} ~ UPDRS10 * Patoz_araliginda + Speed_01 + C(Study)", pdg.dropna(subset=["UPDRS"]))
    print(f"{y} şiddet eğimi aralık içi/dışı farklı mı (UPDRS10×aralık): {k(m, 'UPDRS10:Patoz_araliginda[T.True]')}")

# ---------- E8 kesinlik ----------
baslik("E8 KESİNLİK / DUYARLILIK GÜCÜ (birincil şiddet modeli)")
for y in ["CV_ana", "CV_cop"]:
    m = fit(f"{y} ~ UPDRS10 + Speed_01 + C(Study)", pdg.dropna(subset=["UPDRS"]))
    se = m.bse["UPDRS10"]
    mde = (stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) * se
    sd_y = pdg[y].std()
    print(f"{y}: n={int(m.nobs)}, eğim SE={se:.3f} → %80 güçle saptanabilecek en küçük eğim ≈ {mde:.3f} CV puanı / 10 UPDRS (= {mde / sd_y:.2f} SS); bulunan {m.params['UPDRS10']:.3f}")
