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

st.set_page_config(layout="wide")

# =============================
# 初期化
# =============================
os.makedirs(LOG_DIR, exist_ok=True)

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())[:8]

if "condition" not in st.session_state:
    st.session_state.condition = random.choice(["①", "②", "③"])

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =============================
# タイトル・説明
# =============================
st.title("コメント評価実験")

st.markdown("""
本実験では、楽曲に付与されたコメントの提示方法について評価していただきます。

各楽曲について、以下の2種類のコメント一覧（A, B）が提示されます。

それぞれの一覧を確認した上で、  
**条件により適切だと感じた方**を選択してください。
""")

# =============================
# 条件表示
# =============================
condition = st.session_state.condition

if condition == "①":
    condition_text = """
**条件：楽曲との関連性が高いコメント**  
（楽曲と直接関係のないコメントが混ざっていないか）
"""
elif condition == "②":
    condition_text = """
**条件：内容の新規性が高いコメント**  
（内容が「あるある」なコメントに偏っていないか）
"""
else:
    condition_text = """
**条件：関連性・新規性がどちらも高いコメント**  
（楽曲と直接関係のないコメント、内容が「あるある」なコメントが混ざっていないか）
"""

st.info(condition_text)

# =============================
# 評価順 Top5（固定）
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
        """マリアで崇拝されるアイドルと母の両方表してるの控えめに言って最高
5億再生おめでとうございます！！"""
    ]
}

# =============================
# 提案手法 Top5 取得関数
# =============================
def get_proposed_top5(df, condition):
    if condition == "①":
        col = "関連性_norm"
    elif condition == "②":
        col = "新規性_norm"
    else:
        col = "両立スコア"

    return (
        df.sort_values(col, ascending=False)
          .head(5)["コメント"]
          .tolist()
    )

# =============================
# 楽曲ごとの評価
# =============================
file_map = {
    "アイネクライネ": "comment2_xy.xlsx",
    "アイドル": "comment3_xy.xlsx"
}

responses = {}

for music, file in file_map.items():
    st.header(music)

    df = pd.read_excel(file)

    proposed_top5 = get_proposed_top5(df, condition)
    eval_top5 = EVAL_TOP5[music]

    st.subheader("タイプA")
    st.dataframe(
        pd.DataFrame({
            "順位": [1, 2, 3, 4, 5],
            "コメント": proposed_top5
        }),
        hide_index=True,
        use_container_width=True
    )

    st.subheader("タイプB")
    st.dataframe(
        pd.DataFrame({
            "順位": [1, 2, 3, 4, 5],
            "コメント": eval_top5
        }),
        hide_index=True,
        use_container_width=True
    )

    q1 = st.radio(
        "Q1. 条件により適切なのはどちらですか？",
        [
            "Aの方が良い",
            "Aの方がやや良い",
            "どちらともいえない",
            "Bの方がやや良い",
            "Bの方が良い"
        ],
        index=None,
        key=f"q1_{music}"
    )

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
st.caption("※ 管理者用")

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
