import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
ADMIN_PASSWORD = "ehimecho"

st.set_page_config(layout="wide")

# =============================
# 初期化
# =============================
os.makedirs(LOG_DIR, exist_ok=True)

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())[:8]

if "condition" not in st.session_state:
    st.session_state.condition = random.choice(["①", "②", "③"])

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "confirmed" not in st.session_state:
    st.session_state.confirmed = {}

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =============================
# タイトル
# =============================
st.title("コメント評価実験")

st.markdown("""
**横軸**：楽曲との関連性 (Relevance)  
**縦軸**：内容の新規性 (Novelty)
""")

# =============================
# 楽曲選択
# =============================
file_map = {
    "アイネクライネ": "comment2_xy.xlsx",
    "アイドル": "comment3_xy.xlsx"
}

music = st.selectbox("評価対象の楽曲を選択してください", file_map.keys())
df = pd.read_excel(file_map[music])

df["関連性スコア"] = pd.to_numeric(df["関連性スコア"], errors="coerce")
df["新規性_IDF"] = pd.to_numeric(df["新規性_IDF"], errors="coerce")
df = df.dropna(subset=["関連性スコア", "新規性_IDF"])

# =============================
# 実験条件
# =============================
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

# =============================
# 散布図
# =============================
st.subheader("コメント分布（番号のみ表示）")

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

# =============================
# コメント選択
# =============================
st.subheader("コメント選択")

selectable_ids = sorted(df_show["コメント番号"].astype(int).tolist())

selected_ids = st.multiselect(
    "コメント番号を5つ選択してください",
    selectable_ids,
    max_selections=5,
    key=f"select_{music}"
)

# ===== ここが重要 =====
# 選択が変わったら confirmed をリセット
if f"last_selected_{music}" not in st.session_state:
    st.session_state[f"last_selected_{music}"] = selected_ids

if st.session_state[f"last_selected_{music}"] != selected_ids:
    st.session_state.confirmed[music] = False
    st.session_state[f"last_selected_{music}"] = selected_ids

confirmed = st.session_state.confirmed.get(music, False)

if st.button("OK（コメント内容を表示）"):
    if len(selected_ids) == 5:
        st.session_state.confirmed[music] = True
        confirmed = True
    else:
        st.warning("5件選択してください。")

if confirmed:
    st.caption("※ セルをダブルクリックすると全文を確認できます。")
    st.dataframe(
        df[df["コメント番号"].isin(selected_ids)][["コメント番号", "コメント"]],
        hide_index=True,
        use_container_width=True
    )
# =============================
# 評価順 Top5（仮）
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
st.subheader("評価順Top5")
st.dataframe(
    pd.DataFrame({
        "順位": [1, 2, 3, 4, 5],
        "コメント": EVAL_TOP5[music]
    }),
    hide_index=True,
    use_container_width=True
)
# =============================
# 設問
# =============================
q1 = st.radio(
    "Q1. 条件に合っているのはどちらですか？",[
        "評価順の方が良い",
        "評価順の方がやや良い",
        "どちらともいえない",
        "グラフで選んだものがやや良い",
        "グラフで選んだものが良い"],
    key=f"q1_{music}",
    disabled=not confirmed
)
q2 = st.text_area(
    "Q2. その他気になったこと・気づいたこと",
    key=f"q2_{music}",
    disabled=not confirmed
)
if not confirmed:
    st.info("※ コメント内容を表示（OK）した後に回答できます。")

if st.button("この楽曲の回答を保存", disabled=not confirmed):
    if not q1:
        st.warning("Q1に回答してください。")
    else:
        st.session_state.responses[music] = {
            "selected_ids": selected_ids,
            "q1": q1,
            "q2": q2
        }
        st.success(f"{music} の回答を保存しました。")
# =============================
# 回答状況
# =============================
st.subheader("回答状況")
for m in file_map.keys():
    st.write("✅" if m in st.session_state.responses else "⬜", m)
# =============================
# 最終送信（CSV追記）
# =============================
if st.button("最終送信"):
    if len(st.session_state.responses) != len(file_map):
        st.warning("すべての楽曲を評価してください。")
    else:
        new_file = not os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["timestamp", "participant_id", "condition", "music", "selected_ids", "Q1", "Q2"])
            for music, res in st.session_state.responses.items():
                writer.writerow([
                    datetime.now().isoformat(),
                    st.session_state.participant_id,
                    st.session_state.condition,
                    music,
                    ",".join(map(str, res["selected_ids"])),
                    res["q1"],
                    res["q2"]
                ])
        st.success("回答ありがとうございました。")

# =============================
# 管理者（目立たない）
# =============================
st.divider()
st.caption("※ 以下気にしないでください。")
pw = st.text_input("", type="password")
if st.button("　"):
    st.session_state.is_admin = (pw == ADMIN_PASSWORD)

if st.session_state.is_admin and os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        st.download_button("CSVダウンロード", f.read(), "experiment_log.csv", "text/csv")
