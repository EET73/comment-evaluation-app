import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import japanize_matplotlib

st.set_page_config(layout="wide")
st.title("コメント評価実験（可視化）")

# -----------------------------
# 楽曲選択
# -----------------------------
file_map = {
    "楽曲A": "comment2_xy.xlsx",
    "楽曲B": "comment3_xy.xlsx"
}

music = st.selectbox("評価対象の楽曲を選択してください", file_map.keys())
df = pd.read_excel(file_map[music])

# 数値化（安全対策）
df["関連性スコア"] = pd.to_numeric(df["関連性スコア"], errors="coerce")
df["新規性_IDF"] = pd.to_numeric(df["新規性_IDF"], errors="coerce")
df = df.dropna(subset=["関連性スコア", "新規性_IDF"])

# -----------------------------
# 散布図
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 6))

ax.scatter(
    df["関連性スコア"],
    df["新規性_IDF"],
    alpha=0.7
)

ax.set_xlabel("関連性スコア")
ax.set_ylabel("新規性スコア")
ax.set_title("コメント分布（本文非表示）")

st.pyplot(fig)
