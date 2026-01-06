import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("コメント評価実験")
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
# 実験条件
# -----------------------------
condition = st.selectbox(
    "評価条件",
    ["① 関連性が高い", "② 新規性が高い", "③ 両方が高い"]
)

if condition.startswith("①"):
    df_show = df.sort_values("関連性スコア", ascending=False).head(50)
elif condition.startswith("②"):
    df_show = df.sort_values("新規性_IDF", ascending=False).head(50)
else:
    df_show = df.sort_values(
        ["関連性スコア", "新規性_IDF"],
        ascending=False
    ).head(50)

# -----------------------------
# 散布図（英語表記）
# -----------------------------
st.subheader("コメント分布（番号のみ表示）")
fig, ax = plt.subplots(figsize=(6, 6))

ax.scatter(
    df["関連性スコア"],
    df["新規性_IDF"],
    alpha=0.7
)

# 点にコメント番号を小さく表示
for _, row in df_show.iterrows():
    ax.text(
        row["関連性スコア"],
        row["新規性_IDF"],
        str(int(row["コメント番号"])),
        fontsize=7,
        alpha=1.0
    )

ax.set_xlabel("関連性Relevance")
ax.set_ylabel("新規性Novelty")
ax.set_title("Comment Distribution")
st.pyplot(fig)

# -----------------------------
# 番号選択
# -----------------------------
st.subheader("コメント選択")

selected_ids = st.multiselect(
    "グラフを見てコメント番号を5つ選択してください",
    df_show["コメント番号"].tolist(),
    max_selections=5
)

# -----------------------------
# 本文表示
# -----------------------------
if st.button("OK"):
    if len(selected_ids) != 5:
        st.warning("5件選択してください。")
    else:
        st.success("選択完了")

        st.subheader("選択されたコメント本文")
        st.table(
            df[df["コメント番号"].isin(selected_ids)][
                ["コメント番号", "コメント"]
            ]
        )
