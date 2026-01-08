import streamlit as st
import pandas as pd
import random
import csv
import uuid
import os
from datetime import datetime

# =============================
# 設定
# =============================
LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "experiment_log.csv")
ADMIN_PASSWORD = "ehimecho"  # ★必ず後で変更

# st.set_page_config(layout="wide")

# =============================
# 初期化
# =============================
os.makedirs(LOG_DIR, exist_ok=True)

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())[:8]

# 管理者判定用
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =============================
# タイトル・説明
# =============================
st.title("コメント評価実験（新規性評価）")

st.markdown("""
本実験では、楽曲に付与されたコメントの  
**内容の新規性**について評価していただきます。

各楽曲について、以下の2種類のコメント群（A群・B群）が提示されます。

それぞれの一覧を確認した上で、  
**新規性の観点から適切だと感じたコメント群**を選択してください。
""")

# =============================
# 評価基準（新規性のみ）
# =============================
st.info("""
**評価基準：コメント内容の新規性**

新規性が高いコメントとは、  
・内容が「あるある」ではない  
・ユニークな視点・表現がある  
・自分にはなかった知識、気づき、発見がある  

と感じられるものを指します。
""")

# =============================
# 評価順 Top5（B群：固定）
# =============================
EVAL_TOP5 = {
    "アイネクライネ": [
        "コメント古い順追加してほしい",
        "しんどいことがあった時、友達が下校中に傘をひっくり返して「アイネクライネ！」って一発芸してくれて救われたことある。ありがとう",
        "ふと急にアイネクライネ聴きたくなる時あるよね。",
        "おそらくIRIS OUT効果でTOP100入りしてるんだろうけど、この曲の何がすごいって作詞作曲だけじゃなくてMVのイラストも米津さんなんよね。",
        '"いつか来るお別れを育てて歩く"この表現すごい...'
    ],
    "アイドル": [
        "また良い曲作りましたなAyase氏",
        "「ああやっと言えた、これは絶対嘘じゃない、愛してる」のところめっちゃ感動",
        "急に聞きたくなって戻ってきちゃった",
        "もう2年か...",
        "マリアで崇拝されるアイドルと母の両方表してるの控えめに言って最高"
    ]
}

# =============================
# A群：提案手法 Top5（新規性のみ）
# =============================
def get_proposed_top5(df):
    return (
        df.sort_values("新規性_norm", ascending=False)
          .head(5)[["コメント"]]
    )

# =============================
# 楽曲ファイル・URL
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

responses = {}

# =============================
# 楽曲ごとの評価
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)

    st.markdown(f"🎧 楽曲URL（未視聴の方はこちら）: {info['url']}")
    st.caption("※ 表はダブルクリックするとコメント全文を確認できます。")

    df = pd.read_excel(info["file"])

    proposed_top5 = get_proposed_top5(df)
    eval_top5 = EVAL_TOP5[music]

    # A群
    st.subheader("A群（新規性スコア上位）")
    st.dataframe(
        proposed_top5,
        hide_index=True,
        use_container_width=True
    )

    # B群
    st.subheader("B群（比較対象）")
    st.dataframe(
        pd.DataFrame({"コメント": eval_top5}),
        hide_index=True,
        use_container_width=True
    )

    # Q1
    q1 = st.radio(
        "Q1. 新規性の観点から、どちらが適切だと感じましたか？",
        [
            "A群の方が良い",
            "A群の方がやや良い",
            "どちらともいえない",
            "B群の方がやや良い",
            "B群の方が良い"
        ],
        index=None,
        key=f"q1_{music}"
    )

    # Q2
    q2 = st.text_area(
        "Q2. その他気づいた点（任意）",
        key=f"q2_{music}"
    )

    responses[music] = {
        "q1": q1,
        "q2": q2
    }

# =============================
# 最終送信
# =============================
st.divider()

if st.button("提出"):
    unanswered = [m for m, r in responses.items() if r["q1"] is None]

    if unanswered:
        st.warning("すべての楽曲について Q1 に回答してください。")
    else:
        new_file = not os.path.exists(LOG_FILE)

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow([
                    "timestamp",
                    "participant_id",
                    "music",
                    "Q1",
                    "Q2"
                ])

            for music, r in responses.items():
                writer.writerow([
                    datetime.now().isoformat(),
                    st.session_state.participant_id,
                    music,
                    r["q1"],
                    r["q2"]
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
