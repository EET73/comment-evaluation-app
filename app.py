import streamlit as st
import pandas as pd

st.title("コメント可視化テスト")

df = pd.DataFrame({
    "コメント番号": [0, 1, 2],
    "関連性スコア": [1.2, 0.5, -0.3],
    "新規性_IDF": [0.8, 1.5, 0.2],
    "コメント": ["コメントA", "コメントB", "コメントC"]
})

st.dataframe(df)
