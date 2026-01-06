import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("コメント評価実験（試作版）")

# -----------------------------
# セッション状態初期化
# -----------------------------
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = []

# -----------------------------
# 入力設定
# -----------------------------
VIDEO_SHEET = st.selectbox(
    "動画を選択してください",
    options=["Sheet2", "Sheet3"]
)

# -----------------------------
# データ読み込み
# -----------------------------
@st.cache_data
def load_data(sheet_name):
    df_rel = pd.read_excel(
        "comment_relevance_score.xlsx",
        sheet_name=sheet_name
    )
    df_idf = pd.read_excel(
        "comment_idf_score2.xlsx",
        sheet_name=sheet_name
    )

    df = pd.merge(
        df_rel[["コメント番号", "関連性スコア", "コメント"]],
        df_idf[["コメント番号", "新規性_IDF"]],
        on="コメント番号",
        how="inner"
    )
    return df

df = load_data(VIDEO_SHEET)

# -----------------------------
# 散布図作成（コメント非表示）
# -----------------------------
fig = px.scatter(
    df,
    x="関連性スコア",
    y="新規性_IDF",
)

# hover完全無効化
fig.update_traces(
    hoverinfo="skip",
    marker=dict(size=10, line=dict(width=0))
)

# 選択中の点を赤枠に
if st.session_state.selected_ids:
    selected_df = df[df["コメント番号"].isin(st.session_state.selected_ids)]
    fig.add_scatter(
        x=selected_df["関連性スコア"],
        y=selected_df["新規性_IDF"],
        mode="markers",
        marker=dict(
            size=14,
            color="rgba(0,0,0,0)",
            line=dict(color="red", width=2)
        ),
        hoverinfo="skip",
        showlegend=False
    )

st.subheader("散布図（コメントは表示されません）")
click_data = st.plotly_chart(
    fig,
    use_container_width=True,
    key="scatter"
)

# -----------------------------
# クリック処理
# -----------------------------
if click_data and "points" in click_data:
    point = click_data["points"][0]
    clicked_x = point["x"]
    clicked_y = point["y"]

    row = df[
        (df["関連性スコア"] == clicked_x) &
        (df["新規性_IDF"] == clicked_y)
    ]

    if not row.empty:
        cid = int(row.iloc[0]["コメント番号"])

        if cid in st.session_state.selected_ids:
            st.session_state.selected_ids.remove(cid)
        else:
            if len(st.session_state.selected_ids) < 5:
                st.session_state.selected_ids.append(cid)

# -----------------------------
# 選択状況表示
# -----------------------------
st.write(f"選択数：{len(st.session_state.selected_ids)} / 5")

# -----------------------------
# OKボタン後にコメント表示
# -----------------------------
if len(st.session_state.selected_ids) == 5:
    if st.button("OK（コメントを表示）"):
        result_df = df[df["コメント番号"].isin(st.session_state.selected_ids)]
        st.subheader("選択されたコメント")
        st.dataframe(
            result_df[["コメント番号", "関連性スコア", "新規性_IDF", "コメント"]],
            use_container_width=True
        )
