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

# ★ 条件は固定：新規性②
if "condition" not in st.session_state:
    st.session_state.condition = "②"

# 管理者判定用
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =============================
# 初期設定
# =============================
LOG_FILE = "responses_log.csv"

if "participant_id" not in st.session_state:
    st.session_state.participant_id = datetime.now().strftime("%Y%m%d%H%M%S")

# 条件は「② 新規性」に固定
if "condition" not in st.session_state:
    st.session_state.condition = "②"

condition = st.session_state.condition

# =============================
# タイトル・説明
# =============================
st.title("コメント評価実験")

st.markdown("""
本実験では、楽曲に付与されたコメントの提示方法について評価していただきます。

各楽曲について、以下の2種類のコメント群（A群, B群）が提示されます。

それぞれの一覧を確認した上で、  
**条件により適切だと感じたコメント群（A群 または B群）**を選択してください。
""")

# =============================
# 条件説明（新規性固定）
# =============================
condition_text = """
**条件：内容の新規性が高いコメント**  
新規性：内容が「あるある」ではなくユニークである  
　　　　自分にはなかった知識、視点、発見がある　など
"""
st.info(condition_text)

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
# A群：提案手法 Top5
# =============================
def get_proposed_top5(df):
    top = (
        df.sort_values("新規性_norm", ascending=False)
          .head(5)[["コメント"]]
    )
    return top

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
# 楽曲ごとの評価（スクロール式）
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)

    # 楽曲URL案内
    st.markdown(f"🎧 楽曲URL（未視聴の方はこちら）: {info['url']}")

    st.caption("※ 表はダブルクリックするとコメント全文を確認できます。")

    df = pd.read_excel(info["file"])

    proposed_top5 = get_proposed_top5(df)
    eval_top5 = EVAL_TOP5[music]

    # A群
    st.subheader("A群")
    st.dataframe(
        proposed_top5,
        hide_index=True,
        use_container_width=True
    )

    # B群
    st.subheader("B群")
    st.dataframe(
        pd.DataFrame({"コメント": eval_top5}),
        hide_index=True,
        use_container_width=True
    )

    # Q1
    q1 = st.radio(
        "Q1. 条件により適切だと感じたのはどちらですか？",
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
                    "timestamp", "participant_id", "condition",
                    "music", "Q1", "Q2"
                ])

            for music, r in responses.items():
                writer.writerow([
                    datetime.now().isoformat(),
                    st.session_state.participant_id,
                    condition,
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
