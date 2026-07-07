import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# pip install windrose
from windrose import WindroseAxes


# =========================
# 1. read csv file
# =========================
csv_path = "../data/synoptic.kan.csv"
df = pd.read_csv(csv_path)

df["date"] = pd.to_datetime(
    df["caseName"].str.extract(r"(\d{8})")[0],
    format="%Y%m%d"
)

print(df.head())
print(df[["caseName", "date", "WS925", "WD925"]].describe())
ncase=df.date.size

# =========================
# 2. draw WS925 / WD925 windrose
# =========================
fig = plt.figure(figsize=(9, 7))
ax = WindroseAxes.from_ax(fig=fig)

ax.bar(df["WD925"],df["WS925"],normed=True,opening=0.8,edgecolor="white",bins=np.arange(0, 16, 2))

ax.set_legend(title="WS (m/s)",loc="lower right",bbox_to_anchor=(1.25, 0.0))
ax.set_title(f"Initial Conditions of TaiwanVVM Lee-Vortex Cases (n={ncase})\nMean WS/WD below 925hPa",fontsize=14)
plt.tight_layout()
plt.savefig("windrose_WS925_WD925_all1476.png", dpi=300, bbox_inches="tight")
plt.show()


# =========================
# 3. filter out last five years
# =========================
latest_date = df["date"].max()
start_date = latest_date - pd.DateOffset(years=5)

df_recent = df[
    (df["date"] >= start_date) &
    (df["date"] <= latest_date)
].copy()

print(f"Latest date in file: {latest_date:%Y-%m-%d}")
print(f"Recent 5-year period: {start_date:%Y-%m-%d} to {latest_date:%Y-%m-%d}")
print(f"Number of cases in recent 5 years: {len(df_recent)}")


# =========================
# 4. sample 16 cases for draw simulation results later
# =========================
df_candidates = df_recent[
    (df_recent["WS925"] >= 4.0) &
    (df_recent["WS925"] <= 10.0) &
    (df_recent["WD925"] >= 30.0) &
    (df_recent["WD925"] <= 180.0)
].copy()

print(f"Number of candidate cases: {len(df_candidates)}")

n_select = 16

if len(df_candidates) < n_select:
    raise ValueError(
        f"Only {len(df_candidates)} candidate cases found, "
        f"but {n_select} cases were requested."
    )

df_selected = df_candidates.sample(
    n=n_select,
    random_state=42
).sort_values("date")

print(df_selected[["caseName", "date", "WS925", "WD925", "IVT", "LTS"]])

df_selected[["caseName", "date", "WS925", "WD925", "IVT", "LTS"]].to_csv("../data/selected_16_cases_WS4-10_WD30-180_recent5yr.csv", index=False)
