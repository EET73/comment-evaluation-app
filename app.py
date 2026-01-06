import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("コメント評価実験（可視化）")
st.markdown("""
**横軸**：楽曲との関連性(Relevance)  
**縦軸**：内容の新規性(Novelty)  
""")

# -----------------------------
# 楽曲選択
# -----------------------------
file_map = {
    "アイネクライネ": "comment2_xy.xlsx",
    "アイドル": "comment3_xy.xlsx"
}

music = st.selectbox("評価対象の楽曲を選択してください", file_map.keys())
df = pd.read_excel(file_map[music])

# 数値化
df["関連性スコア"] = pd.to_numeric(df["関連性スコア"], errors="coerce")
df["新規性_IDF"] = pd.to_numeric(df["新規性_IDF"], errors="coerce")
df = df.dropna(subset=["関連性スコア", "新規性_IDF"])

# -----------------------------
# 散布図（英語表記）
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 6))

ax.scatter(
    df["関連性スコア"],
    df["新規性_IDF"],
    alpha=0.7
)

# 点にコメント番号を小さく表示
for _, row in df.iterrows():
    ax.text(
        row["関連性スコア"],
        row["新規性_IDF"],
        str(row["コメント番号"]),
        fontsize=6,
        alpha=0.6
    )

ax.set_xlabel("Relevance")
ax.set_ylabel("Novelty")
ax.set_title("Comment Distribution")

st.pyplot(fig)

# -----------------------------
# 点選択
# -----------------------------
st.subheader("コメントを5つ選択してください（番号）")

selected = []

for num in df["コメント番号"]:
    if st.checkbox(f"コメント {num}", key=f"cb_{num}"):
        selected.append(num)

# 最大5件制限
if len(selected) > 5:
    st.warning("5つまで選択してください")

# -----------------------------
# 点選択
# -----------------------------
if len(selected) == 5:
    if st.button("OK（コメントを表示）"):
        st.subheader("選択されたコメント")

        result_df = df[df["コメント番号"].isin(selected)]

        st.table(
            result_df[["コメント番号", "コメント"]]
            .reset_index(drop=True)
        )
