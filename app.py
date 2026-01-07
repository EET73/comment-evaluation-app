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
        """マリアで崇拝されるアイドルと母の両方表してるの控えめに言って最
