import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.family"] = "IPAexGothic"

st.set_page_config(layout="wide")
st.title("コメント評価実験（可視化）")

# -----------------------------
# データ読み込み（1ファイル）
# -----------------------------
data_path = "comment2_xy.xlsx"
df = pd.read_excel(data_path)

# 数値化（安全対策）
df["関連性スコア"] = pd.to_numeric(df["関連性スコア"], errors="coerce")
df["新規性_IDF"] = pd.to_numeric(df["新規性_IDF"], errors="coerce")
df = df.dropna(subset=["関連性スコア", "新規性_IDF"])

st.subheader("データ確認")
st.write(df.head())

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
