import pandas as pd
import requests

URL = "https://physionet-open.s3.amazonaws.com/gaitpdb/1.0.0/"

dem = pd.read_csv(URL + "demographics.txt", sep="\t", usecols=range(20))
dem = dem[dem.ID.notna()]
dem["Grup"] = dem.Group.map({1: "PD", 2: "Kontrol"})

for sutun in ["Speed_01", "UPDRS", "HoehnYahr"]:
    print(f"\n{sutun} dolu / toplam:")
    print(dem.groupby(["Study", "Grup"])[sutun].agg(lambda s: f"{s.notna().sum()}/{len(s)}").unstack())

hizli = dem[dem.Speed_01.notna()].copy()
hizli["Patoz_araliginda"] = hizli.Speed_01.between(1.0, 1.3)
print("\nHızı dolu kişi:", hizli.Grup.value_counts().to_dict())
print("Patoz aralığında (1,0-1,3 m/s):")
print(hizli.groupby(["Grup", "Patoz_araliginda"]).size().unstack())

eksik_dosya = [k for k in hizli.ID if requests.head(URL + f"{k}_01.txt").status_code != 200]
print("\n_01 dosyası bulunamayan kişiler:", eksik_dosya)
