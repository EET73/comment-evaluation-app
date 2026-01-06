import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("コメント評価実験（可視化）")

# -----------------------------
# データ読み込み
# -----------------------------
relevance_path = "comment_relevance_score.xlsx"
novelty_path   = "comment_idf_score2.xlsx"

# どの動画（Sheet）を使うか
sheet = st.selectbox(
    "評価対象の動画を選択してください",
    ["Sheet2", "Sheet3"]
)

df_rel = pd.read_excel(relevance_path, sheet_name=sheet)
df_nov = pd.read_excel(novelty_path, sheet_name=sheet)

# merge
df = pd.merge(
    df_rel,
    df_nov,
    on="コメント番号",
    how="inner"
)

# -----------------------------
# 散布図
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 6))

ax.scatter(
    df["関連性スコア"],
    df["新規性_IDF"],
    alpha=0.7
)

ax.set_xlabel("楽曲との関連性")
ax.set_ylabel("内容の新規性")
ax.set_title("コメント分布（本文非表示）")

st.pyplot(fig)
