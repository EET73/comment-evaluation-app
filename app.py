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
st.title("コメント評価実験（新規性）")

st.markdown("""
本実験では、楽曲に付与された**個々のコメントの新規性**について評価していただきます。

各楽曲について **10件のコメント** が提示されます。  
それぞれのコメントを読み、  
**内容がどの程度ユニークで新規性があると感じるか**を5段階で評価してください。
""")

st.info("""
**新規性の判断基準**

・「あるある」ではなく独自性がある  
・ユニークな視点や表現がある  
・自分にはなかった知識・発見がある  
""")

# =============================
# B由来コメント（固定）
# =============================
BASELINE_TOP5 = {
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
# A由来コメント（新規性上位）
# =============================
def get_proposed_top5(df):
    return (
        df.sort_values("新規性_norm", ascending=False)
          .head(5)["コメント"]
          .tolist()
    )

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

all_responses = []

# =============================
# 評価ループ
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)
    st.markdown(f"🎧 楽曲URL: {info['url']}")

    df = pd.read_excel(info["file"])

    proposed = get_proposed_top5(df)
    baseline = BASELINE_TOP5[music]

    comments = (
        [{"source": "proposed", "text": c} for c in proposed] +
        [{"source": "baseline", "text": c} for c in baseline]
    )

    st.caption("以下の各コメントについて、新規性を評価してください。")

    for i, item in enumerate(comments):
        st.markdown(f"**コメント {i+1}**")
        st.write(item["text"])

        score = st.radio(
            "新規性の評価",
            [1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1：まったく新規性を感じない",
                2: "2：あまり新規性を感じない",
                3: "3：どちらともいえない",
                4: "4：やや新規性がある",
                5: "5：非常に新規性がある"
            }[x],
            key=f"{music}_{i}"
        )

        all_responses.append({
            "music": music,
            "source": item["source"],
            "comment": item["text"],
            "score": score
        })

# =============================
# 送信
# =============================
st.divider()

if st.button("提出"):
    if not all_responses:
        st.warning("評価が未入力です。")
    else:
        new_file = not os.path.exists(LOG_FILE)

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow([
                    "timestamp",
                    "participant_id",
                    "music",
                    "source",
                    "comment",
                    "novelty_score"
                ])

            for r in all_responses:
                writer.writerow([
                    datetime.now().isoformat(),
                    st.session_state.participant_id,
                    r["music"],
                    r["source"],
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
