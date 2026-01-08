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
st.session_state.setdefault("is_admin", False)
LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "experiment_log.csv")
ADMIN_PASSWORD = "ehimecho"  # ★必ず後で変更

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

# =============================
# タイトル・説明
# =============================
st.title("コメント評価実験（新規性）")

st.markdown("""
本実験では、コメント内容の**新規性**を評価していただきます。

- 一部のコメントは分布図から **5件選択**
- 選択後、それぞれを **5段階で評価**
- 比較対象コメントも同様に評価します
""")

st.info("""
**新規性の判断基準**

・「あるある」ではない  
・ユニークな視点や表現がある  
・新しい気づき・発見がある  
""")

# =============================
# 比較対象コメント（B側）
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

# =============================
# 評価ループ
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)
    st.markdown(f"🎧 楽曲URL: {info['url']}")

    df = pd.read_excel(info["file"])

    # -----------------------------
    # 散布図
    # -----------------------------
    st.subheader("コメント分布（番号のみ表示）")

    df_show = df.sort_values("新規性_norm", ascending=False).head(70)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(df_show["関連性スコア"], df_show["新規性_IDF"], alpha=0.7)

    for _, row in df_show.iterrows():
        ax.text(
            row["関連性スコア"],
            row["新規性_IDF"],
            str(int(row["コメント番号"])),
            fontsize=4
        )

    ax.set_xlabel("Relevance")
    ax.set_ylabel("Novelty")
    st.pyplot(fig)

    # -----------------------------
    # コメント選択
    # -----------------------------
    st.subheader("コメント選択（5件）")

    selectable_ids = sorted(df_show["コメント番号"].astype(int).tolist())
    selected = st.multiselect(
        "コメント番号を5つ選択してください",
        selectable_ids,
        max_selections=5,
        key=f"select_{music}"
    )

    if st.button("OK（選択したコメントを表示）", key=f"ok_{music}"):
        if len(selected) == 5:
            st.session_state.confirmed[music] = True
            st.session_state.selected_ids[music] = selected
        else:
            st.warning("5件選択してください。")

    # -----------------------------
    # 評価
    # -----------------------------
    if st.session_state.confirmed.get(music, False):
        st.subheader("コメントの評価")

        eval_items = []

        # A側
        for cid in st.session_state.selected_ids[music]:
            row = df[df["コメント番号"] == cid].iloc[0]
            eval_items.append({
                "source": "proposed",
                "comment_number": cid,
                "comment": row["コメント"]
            })

        # B側
        for comment in BASELINE_TOP5[music]:
            eval_items.append({
                "source": "baseline",
                "comment_number": None,
                "comment": comment
            })

        for i, item in enumerate(eval_items):
            st.write(f"**コメント {i+1}**")
            st.write(item["comment"])

            if item["source"] == "proposed":
                key = f"eval_{music}_A_{item['comment_number']}"
            else:
                key = f"eval_{music}_B_{i}"

            st.radio(
                "新規性評価",
                [1, 2, 3, 4, 5],
                index=None,
                format_func=lambda x: {
                    1: "1：まったく新規性を感じない",
                    2: "2：あまり新規性を感じない",
                    3: "3：どちらともいえない",
                    4: "4：やや新規性がある",
                    5: "5：非常に新規性がある"
                }[x],
                key=key
            )

# =============================
# 提出
# =============================
st.divider()

if st.button("提出"):
    rows = []
    has_error = False

    for music in file_map.keys():
        # A側
        for cid in st.session_state.selected_ids.get(music, []):
            score = st.session_state.get(f"eval_{music}_A_{cid}")
            if score is None:
                has_error = True
            comment = (
                pd.read_excel(file_map[music]["file"])
                .query("コメント番号 == @cid")["コメント"]
                .iloc[0]
            )
            rows.append([
                datetime.now().isoformat(),
                st.session_state.participant_id,
                music,
                "proposed",
                cid,
                comment,
                score
            ])

        # B側
        for i, comment in enumerate(BASELINE_TOP5[music]):
            score = st.session_state.get(f"eval_{music}_B_{i}")
            if score is None:
                has_error = True
            rows.append([
                datetime.now().isoformat(),
                st.session_state.participant_id,
                music,
                "baseline",
                None,
                comment,
                score
            ])

    if has_error:
        st.warning("未評価のコメントがあります。")
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
                    "comment_number",
                    "comment",
                    "novelty_score"
                ])
            writer.writerows(rows)

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

        )
