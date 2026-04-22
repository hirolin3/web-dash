import streamlit as st
import json
from fuzzywuzzy import fuzz
import mojimoji

# ページ設定
st.set_page_config(page_title="最強株検索", layout="wide")

@st.cache_data
def load_data():
    with open('ai_stock_dictionary_v2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

stocks = load_data()

st.title("🔎 日経225「超・意味検索」")

# 検索窓
query_raw = st.text_input("何を探していますか？", placeholder="例：ちくわ、ゲーム、スカイツリー")

if query_raw:
    # 検索語の正規化（全角→半角、ひらがな→カタカナなど）
    query = mojimoji.zen_to_han(query_raw).lower()
    # 「の」を除去して検索しやすくする
    query_clean = query.replace("の", " ")

    results = []
    for s in stocks:
        # スコア計算（3つのポイントを合計）
        # 1. 銘柄名への完全・部分一致（配点：高）
        name_score = fuzz.partial_ratio(query_clean, s['name']) * 2
        
        # 2. 説明文とキーワードへの意味的近さ（配点：中）
        desc_text = f"{s['simple_desc']} {s['keywords']}"
        desc_score = fuzz.token_set_ratio(query_clean, desc_text)
        
        # 3. 銘柄コードへの一致（配点：最高）
        code_score = 100 if query_clean in s['code'] else 0
        
        # 合計スコア
        total_score = name_score + desc_score + code_score
        results.append({"data": s, "score": total_score})

    results = sorted(results, key=lambda x: x['score'], reverse=True)

    # 表示
    st.write(f"### 「{query_raw}」の検索結果")
    cols = st.columns(3)
    for i, res in enumerate(results[:6]):
        if res['score'] > 40: # 閾値を少し調整
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {res['data']['name']}")
                    st.caption(f"コード: {res['data']['code']} / 関連度: {int(res['score'])}")
                    st.write(res['data']['simple_desc'])
                    with st.expander("AIキーワード"):
                        st.write(res['data']['keywords'])
