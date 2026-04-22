import streamlit as st
import json
import pandas as pd
from fuzzywuzzy import fuzz

# ページ設定
st.set_page_config(page_title="日経225 意味で検索エンジン", layout="wide")

st.title("🔍 日経225「意味で検索」デモ")
st.caption("AIとWikipediaの力で、うろ覚えの言葉から銘柄を探し出します。")

# 1. データの読み込み
@st.cache_data
def load_data():
    with open('ai_stock_dictionary_v2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

stocks = load_data()

# 2. 検索インターフェース
query = st.text_input("キーワードを入力してください（例：ドンキ、旧帝石、魚のちくわ、ゲームの会社）", placeholder="何をしている会社ですか？")

if query:
    # 3. 検索ロジック（あいまい検索）
    results = []
    for s in stocks:
        # 名前 + 説明 + キーワードを合算してスコアリング
        search_target = f"{s['name']} {s['simple_desc']} {s['keywords']}"
        score = fuzz.token_set_ratio(query, search_target)
        results.append({"data": s, "score": score})
    
    # スコアが高い順にソート
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # 4. 結果表示
    st.subheader(f"「{query}」の検索結果")
    
    # 上位6件をグリッドで表示
    cols = st.columns(3)
    for i, res in enumerate(results[:6]):
        if res['score'] > 30: # 関連性が低いものは除外
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {res['data']['name']}")
                    st.code(res['data']['code'])
                    st.write(f"**AI解説:** {res['data']['simple_desc']}")
                    with st.expander("関連キーワード"):
                        st.write(res['data']['keywords'])
                    st.progress(res['data'].get('score', res['score']) / 100, text=f"関連度: {res['score']}%")
else:
    st.info("検索窓に言葉を入力して、AI辞書の威力を確かめてみてください。")

# サイドバーに現在の登録状況を表示
st.sidebar.header("📊 辞書のステータス")
st.sidebar.write(f"現在の登録銘柄数: **{len(stocks)}** / 225")