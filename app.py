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
本実験では、コメント内容の**関連性と新規性**を評価していただきます。

- 分布図から **関連性(横軸)と新規性(横軸)のどちらも高いと感じる点を10個選択**
- 選択後、20件のコメントを **5段階で評価**
- 2つの楽曲についてこれを行ってもらいます。
""")

st.info("""
**関連性の判断基準**

- 楽曲に直接関係する内容に言及
（歌詞、MV、メロディなど）
- 感想、考察　など 

**新規性の判断基準**

-「あるある」な内容ではない  
-ユニークな視点や表現がある  
-新しい気づき・発見がある　など 
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
        '"いつか来るお別れを育てて歩く"この表現すごい...',
        """歌詞
作詞：Kenshi Yonezu
作曲：Kenshi Yonezu
あたしあなたに会えて本当に嬉しいのに
当たり前のようにそれらすべてが悲しいんだ
今痛いくらい幸せな思い出が
いつか来るお別れを育てて歩く

誰かの居場所を奪い生きるくらいならばもう
あたしは石ころにでもなれたらいいな
だとしたら勘違いも戸惑いもない
そうやってあなたまでも知らないままで

あなたにあたしの思いが全部伝わってほしいのに
誰にも言えない秘密があって嘘をついてしまうのだ
あなたが思えば思うよりいくつもあたしは意気地ないのに
どうして

消えない悲しみも綻びもあなたといれば
それでよかったねと笑えるのがどんなに嬉しいか
目の前の全てがぼやけては溶けてゆくような
奇跡であふれて足りないや
あたしの名前を呼んでくれた

あなたが居場所を失くし彷徨うくらいならばもう
誰かが身代わりになればなんて思うんだ
今 細やかで確かな見ないふり
きっと繰り返しながら笑い合うんだ

何度誓っても何度祈っても惨憺たる夢を見る
小さな歪みがいつかあなたを呑んでなくしてしまうような
あなたが思えば思うより大げさにあたしは不甲斐ないのに
どうして

お願い いつまでもいつまでも超えられない夜を
超えようと手をつなぐこの日々が続きますように
閉じた瞼さえ鮮やかに彩るために
そのために何ができるかな
あなたの名前を呼んでいいかな

産まれてきたその瞬間にあたし
「消えてしまいたい」って泣き喚いたんだ
それからずっと探していたんだ
いつか出会える あなたのことを

消えない悲しみも綻びもあなたといれば
それでよかったねと笑えるのがどんなに嬉しいか
目の前の全てがぼやけては溶けてゆくような
奇跡であふれて足りないや
あたしの名前を呼んでくれた

あなたの名前を呼んでいいかな
(コピペ)""",
        """Lemonに加えてアイネクライネまで
Top100に入り込んでくるとは。
やっぱ昔の曲がまだまだ人気なのいいよな""",
        "「嬉し涙」のことを「目の前の全てがぼやけては溶けていくような奇跡」って表現する才能が凄まじい…",
        "Lemonが24位、アイネクライネが89位に復帰してるの恐ろしいな",
        "ふと急にアイネクライネが聴きたくなる時あるよね。"
    ],
    "アイドル": [
        "また良い曲作りましたなAyase氏",
        "「ああやっと言えた、これは絶対嘘じゃない、愛してる」のところめっちゃ感動",
        "急に聞きたくなって戻ってきちゃった",
        "もう2年か...",
        "マリアで崇拝されるアイドルと母の両方表してるの控えめに言って最高",
        "推しの子が好きすぎてオファー来る前から勝手に曲作ってたぐらいですって話聞いて、この原作とのシンクロ感にめっちゃ納得",
        "2番はただの妬みだと思ってたけどニノのところ読んでからメンバーからも偶像として完璧を求められてたんだなと苦しくなる。「弱いとこなんて見せちゃダメダメ」「唯一無二じゃなくちゃいやいや」「それこそ本物の愛（アイ）」って歪んだ感情すぎて好きすぎる。ヒット曲なのに闇深いところが大好き。",
        """「やっと言えた｣
｢これは絶対嘘じゃない｣
｢愛してる｣
これを最後に持ってくるの天才すぎる""",
        """アイドルという曲名にそぐわない不気味さを兼ね備えた｢推しの子｣という作品をしっかり取入れた神曲
控えめに言って最強""",
        "ayaseの作曲センス限界突破しててやばい"
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

responses = []

# =============================
# 評価ループ
# =============================
for music, info in file_map.items():
    st.divider()
    st.subheader(music)
    st.markdown(f"🎧 楽曲URL: {info['url']}")

    df = pd.read_excel(info["file"])

    # -------- コメント分布（番号のみ） --------
    st.subheader("コメント分布")

    TOP_N = 70
    df_show = df.sort_values("両立スコア", ascending=False).head(TOP_N)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(df_show["関連性_norm"], df_show["新規性_norm"], alpha=0.7)

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

        eval_items = []

        # 選択コメント
        selected_rows = df[df["コメント番号"].isin(st.session_state.selected_ids[music])]
        for _, row in selected_rows.iterrows():
            eval_items.append({
                "music": music,
                "source": "proposed",
                "comment_number": int(row["コメント番号"]),
                "comment": row["コメント"]
            })

        # 比較コメント
        for c in BASELINE_TOP5[music]:
            eval_items.append({
                "music": music,
                "source": "baseline",
                "comment_number": None,
                "comment": c
            })

        # 表示（区別しない）
        for i, item in enumerate(eval_items):
            st.write(item["comment"])

            score = st.radio(
                "条件(関連性＋新規性)評価",
                [1, 2, 3, 4, 5],
                index=None,   # ★ 未選択状態
                format_func=lambda x: {
                    1: "1：まったく条件に合わない",
                    2: "2：あまり条件に合わない",
                    3: "3：どちらともいえない",
                    4: "4：やや条件に合う",
                    5: "5：非常に条件に合う"
                }[x],
                key=f"eval_{music}_{i}"
            )

            st.session_state.responses[(music, i)] = {
                "music": music,
                "source": item["source"],
                "comment_number": item["comment_number"],
                "comment": item["comment"],
                "score": score
            }

            # responses.append({
            #     "music": music,
            #     "source": item["source"],
            #     "comment_number": item["comment_number"],
            #     "comment": item["comment"],
            #     "score": score
            # })

# =============================
# 提出
# =============================
st.divider()

if st.button("提出"):
    # 評価画面がまだ出ていない楽曲がある場合
    for music in file_map.keys():
        if not st.session_state.confirmed.get(music, False):
            st.warning("すべてのコメントを選択・評価してください。")
            st.stop()

    # スコア未入力チェック
    responses = st.session_state.responses.values()
    if any(r["score"] is None for r in responses):
        st.warning("未評価のコメントがあります。")
        st.stop()

    # 保存
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
        for r in responses:
            writer.writerow([
                datetime.now().isoformat(),
                st.session_state.participant_id,
                r["music"],
                r["source"],
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
