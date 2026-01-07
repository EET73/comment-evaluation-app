import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import csv
import io
import uuid

# -----------------------------
# 初期化
# -----------------------------
st.set_page_config(layout="wide")

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())[:8]

if "condition" not in st.session_state:
    st.session_state.condition = random.choice(["①", "②", "③"])

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "confirmed" not in st.session_state:
    st.session_state.confirmed = {}

if "log_rows" not in st.session_state:
    st.session_state.log_rows = []

# -----------------------------
# タイトル
# -----------------------------
st.title("コメント評価実験")

st.markdown("""
**横軸**：楽曲との関連性 (Relevance)  
**縦軸**：内容の新規性 (Novelty)
""")

# -----------------------------
# 楽曲選択
# -----------------------------
file_map = {
    "アイネクライネ": "comment2_xy.xlsx",
    "アイドル": "comment3_xy.xlsx"
}

music = st.selectbox(
    "評価対象の楽曲を選択してください",
    file_map.keys()
)

df = pd.read_excel(file_map[music])

df["関連性スコア"] = pd.to_numeric(df["関連性スコア"], errors="coerce")
df["新規性_IDF"] = pd.to_numeric(df["新規性_IDF"], errors="coerce")
df = df.dropna(subset=["関連性スコア", "新規性_IDF"])

# -----------------------------
# 実験条件
# -----------------------------
condition = st.session_state.condition

if condition == "①":
    condition_text = "楽曲との関連性が高いコメントを選んでください"
elif condition == "②":
    condition_text = "内容の新規性が高いコメントを選んでください"
else:
    condition_text = "関連性・新規性がどちらも高いコメントを選んでください"

st.info(condition_text)

TOP_N = 70
if condition == "①":
    df_show = df.sort_values("関連性_norm", ascending=False).head(TOP_N)
elif condition == "②":
    df_show = df.sort_values("新規性_norm", ascending=False).head(TOP_N)
else:
    df_show = df.sort_values("両立スコア", ascending=False).head(TOP_N)

# -----------------------------
# 散布図
# -----------------------------
st.subheader("コメント分布（番号のみ表示）")

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(
    df_show["関連性スコア"],
    df_show["新規性_IDF"],
    alpha=0.7
)

for _, row in df_show.iterrows():
    ax.text(
        row["関連性スコア"],
        row["新規性_IDF"],
        str(int(row["コメント番号"])),
        fontsize=4
    )

ax.set_xlabel("Relevance")
ax.set_ylabel("Novelty")
ax.set_title("Comment Distribution")
st.pyplot(fig)

# -----------------------------
# コメント番号選択
# -----------------------------
st.subheader("コメント選択")

selectable_ids = sorted(df_show["コメント番号"].astype(int).tolist())

selected_ids = st.multiselect(
    "グラフを見てコメント番号を5つ選択してください",
    selectable_ids,
    max_selections=5
)

# -----------------------------
# OK → コメント表示
# -----------------------------
confirmed = st.session_state.confirmed.get(music, False)

if st.button("OK（コメント内容を表示）"):
    if len(selected_ids) != 5:
        st.warning("5件選択してください。")
    else:
        st.session_state.confirmed[music] = True
        confirmed = True

if confirmed:
    st.subheader("選択されたコメント")
    st.caption("※ 表内のコメントは、セルをダブルクリックすると全文を確認できます。")
    st.dataframe(
        df[df["コメント番号"].isin(selected_ids)]
        .sort_values("コメント番号")[["コメント番号", "コメント"]],
        hide_index=True,
        use_container_width=True
    )

    # -----------------------------
    # 評価順 Top5（仮）
    # -----------------------------
    st.subheader("評価順Top5（参考）")
    st.dataframe(
        pd.DataFrame({
            "順位": [1, 2, 3, 4, 5],
            "コメント": [
                "コメント1",
                "コメント2",
                "コメント3",
                "コメント4",
                "コメント5",
            ]
        }),
        hide_index=True,
        use_container_width=True
    )

    # -----------------------------
    # 設問（OK後のみ表示）
    # -----------------------------
    q1 = st.radio(
        "Q1. 条件に合っているのはどちらですか？",
        [
            "評価順の方が良い",
            "評価順の方がやや良い",
            "どちらともいえない",
            "提案手法の方がやや良い",
            "提案手法の方が良い"
        ],
        key=f"q1_{music}"
    )

    q2 = st.text_area(
        "Q2. その他気になったこと・気づいたこと",
        key=f"q2_{music}"
    )
    if st.button("この楽曲の回答を保存"):
    if not confirmed:
        st.warning("先に OK を押してコメント内容を確認してください。")
    elif len(selected_ids) != 5:
        st.warning("5件選択してください。")
    elif not q1:
        st.warning("Q1 に回答してください。")
    else:
        st.session_state.responses[music] = {
            "selected_ids": selected_ids,
            "q1": q1,
            "q2": q2
        }
        st.success(f"{music} の回答を保存しました。")

    # if st.button("この楽曲の回答を保存"):
    #     st.session_state.responses[music] = {
    #         "selected_ids": selected_ids,
    #         "q1": q1,
    #         "q2": q2
    #     }
    #     st.success(f"{music} の回答を保存しました。")

# -----------------------------
# 回答状況
# -----------------------------
st.subheader("回答状況")
for m in file_map.keys():
    if m in st.session_state.responses:
        st.write(f"✅ {m}：回答済み")
    else:
        st.write(f"⬜ {m}：未回答")

# -----------------------------
# 最終送信
# -----------------------------
if st.button("最終送信"):
    if len(st.session_state.responses) != len(file_map):
        st.warning("すべての楽曲を評価してください。")
    else:
        for music, res in st.session_state.responses.items():
            st.session_state.log_rows.append([
                st.session_state.participant_id,
                st.session_state.condition,
                music,
                ",".join(map(str, res["selected_ids"])),
                res["q1"],
                res["q2"]
            ])
        st.success("ご協力ありがとうございました。")

# -----------------------------
# CSV ダウンロード
# -----------------------------
if st.session_state.log_rows:
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([
        "被験者ID",
        "条件",
        "楽曲",
        "選択コメント",
        "Q1_評価",
        "Q2_自由記述"
    ])
    writer.writerows(st.session_state.log_rows)

    st.download_button(
        label="実験ログをダウンロード",
        data=csv_buffer.getvalue(),
        file_name="experiment_log.csv",
        mime="text/csv"
    )
