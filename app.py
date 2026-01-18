import streamlit as st
import pandas as pd
import os
import csv
import uuid
from datetime import datetime
import matplotlib.pyplot as plt

# =============================
# 設定
# =============================
LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "responses_log.csv")
ADMIN_PASSWORD = "ehimecho"   # ← 追加
# =============================
# 初期化
# =============================
os.makedirs(LOG_DIR, exist_ok=True)

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())[:8]

if "confirmed" not in st.session_state:
    st.session_state.confirmed = {}

if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = {}

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "responses" not in st.session_state:
    st.session_state.responses = {}


# =============================
# タイトル・説明
# =============================
st.title("コメント評価実験")

st.markdown("""
本実験では、コメント内容の**関連性**を評価していただきます。

- 分布図から **関連性(横軸)のどちらも高いと感じる点を10個選択**
- 選択後、これら10件のコメントを **5段階で評価**
- 2つの楽曲についてこれを行ってもらいます。
- 見覚えあるコメントばかりかもだけどゆるして
""")

st.info("""
**関連性の判断基準**

- 楽曲に直接関係する内容に言及
（歌詞、MV、メロディなど）
- 感想、考察　など 
""")


# =============================
# 比較対象コメント（B側）
# =============================
# 今回はなし！

# =============================
# 楽曲ファイル
# =============================
file_map = {
    "アイネクライネ": {
        "file": "comment2_xy.xlsx",
        "url": "https://www.youtube.com/watch?v=-EKxzId_Sj4"
    },
    "アイドル": {
        "file": "comment3_xy.xlsx",
        "url": "https://www.youtube.com/watch?v=ZRtdQ81jPUQ"
    }
}

responses = []

# =============================
# 評価ループ
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)
    st.markdown(f"🎧 楽曲URL: {info['url']}")

    df = pd.read_excel(info["file"])

    # -------- コメント分布 --------
    st.subheader("コメント分布")

    TOP_N = 70
    df_show = df.sort_values("関連性_norm", ascending=False).head(TOP_N)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(
        df_show["関連性_norm"],
        df_show["新規性_norm"],
        alpha=0.7
    )

    for _, row in df_show.iterrows():
        ax.text(
            row["関連性_norm"],
            row["新規性_norm"],
            str(int(row["コメント番号"])),
            fontsize=4
        )

    ax.set_xlabel("Relevance")
    ax.set_ylabel("Novelty")

    st.pyplot(fig)

    # -------- 10件選択 --------
    st.subheader("コメント選択")

    selectable_ids = sorted(df_show["コメント番号"].astype(int).tolist())
    selected = st.multiselect(
        "番号を10個選択してください",
        selectable_ids,
        max_selections=10,
        key=f"select_{music}"
    )

    if st.button("OK", key=f"ok_{music}"):
        if len(selected) == 10:
            st.session_state.confirmed[music] = True
            st.session_state.selected_ids[music] = selected
        else:
            st.warning("10件選択してください。")

    # -------- 評価表示 --------
    if st.session_state.confirmed.get(music, False):
        st.subheader("コメント評価")

        selected_rows = df[
            df["コメント番号"].isin(st.session_state.selected_ids[music])
        ]

        for i, (_, row) in enumerate(selected_rows.iterrows()):
            st.write(row["コメント"])

            score = st.radio(
                "関連性評価",
                [1, 2, 3, 4, 5],
                index=None,
                format_func=lambda x: {
                    1: "1：まったく関連性を感じない",
                    2: "2：あまり関連性を感じない",
                    3: "3：どちらともいえない",
                    4: "4：やや関連性がある",
                    5: "5：非常に関連性がある"
                }[x],
                key=f"eval_{music}_{i}"
            )

            st.session_state.responses[(music, i)] = {
                "music": music,
                "source": "selected",
                "comment_number": int(row["コメント番号"]),
                "comment": row["コメント"],
                "score": score
            }
# =============================
# 提出
# =============================
st.divider()

if st.button("提出"):
    for music in file_map.keys():
        if not st.session_state.confirmed.get(music, False):
            st.warning("すべてのコメントを選択・評価してください。")
            st.stop()

    responses = st.session_state.responses.values()
    if any(r["score"] is None for r in responses):
        st.warning("未評価のコメントがあります。")
        st.stop()

    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow([
                "timestamp",
                "participant_id",
                "music",
                "comment_number",
                "comment",
                "relevance_score"
            ])
        for r in responses:
            writer.writerow([
                datetime.now().isoformat(),
                st.session_state.participant_id,
                r["music"],
                r["comment_number"],
                r["comment"],
                r["score"]
            ])

    st.success("ご協力ありがとうございました。")


# =============================
# 管理者用
# =============================
st.divider()
st.caption("※ 以下気にしないでください...")

pw = st.text_input("", type="password")
if st.button("　"):
    st.session_state.is_admin = (pw == ADMIN_PASSWORD)

if st.session_state.is_admin and os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        st.download_button(
            "CSVダウンロード",
            f.read(),
            "experiment_log.csv",
            "text/csv"
        )
