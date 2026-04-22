import streamlit as st
import json
import random
import pandas as pd

# ページ設定
st.set_page_config(page_title="日経225銘柄当てクイズ", layout="centered")

# 1. データの読み込み
@st.cache_data
def load_data():
    with open('ai_stock_dictionary_v2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

stocks = load_data()

# 2. セッション状態（点数や現在の問題）の管理
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
    st.session_state.score = 0
    st.session_state.current_question = None
    st.session_state.options = []
    st.session_state.game_over = False

# 3. 新しい問題を作る関数
def next_question():
    if st.session_state.question_count >= 100:
        st.session_state.game_over = True
        return

    target = random.choice(stocks)
    # 不正解の選択肢を4つ選ぶ（自分以外からランダム）
    distractors = random.sample([s for s in stocks if s['code'] != target['code']], 4)
    
    options = [target] + distractors
    random.shuffle(options) # 順番を混ぜる
    
    st.session_state.current_question = target
    st.session_state.options = options
    st.session_state.question_count += 1

# 初回起動時
if st.session_state.current_question is None and not st.session_state.game_over:
    next_question()

# --- 画面表示 ---
st.title("🎓 銘柄マスターへの道：100本ノック")
st.write(f"第 {st.session_state.question_count} 問 / 100")
st.progress(st.session_state.question_count / 100)

if st.session_state.game_over:
    st.balloons()
    st.success(f"全100問終了！あなたのスコアは {st.session_state.score} 点でした。")
    if st.button("もう一度挑戦する"):
        st.session_state.question_count = 0
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.current_question = None
        st.rerun()

elif st.session_state.current_question:
    q = st.session_state.current_question
    
    # 問題文
    with st.chat_message("assistant"):
        st.write("### 次の会社概要に当てはまる銘柄を選んでください。")
        st.info(f"**【会社概要】**\n\n{q['simple_desc']}")

    # 選択肢ボタン
    st.write("---")
    for opt in st.session_state.options:
        if st.button(f"{opt['name']} ({opt['code']})", key=opt['code'], use_container_width=True):
            if opt['code'] == q['code']:
                st.session_state.score += 1
                st.toast(f"正解！ 🎉 (現在のスコア: {st.session_state.score})")
            else:
                st.error(f"残念！正解は **{q['name']} ({q['code']})** でした。")
            
            # 2秒待って次の問題へ
            st.session_state.current_question = None # クリアして再生成を促す
            st.rerun()

# サイドバーに現在の成績
st.sidebar.metric("現在の正解数", f"{st.session_state.score} 点")
if st.sidebar.button("リセットして最初から"):
    st.session_state.question_count = 0
    st.session_state.score = 0
    st.session_state.current_question = None
    st.rerun()
