import streamlit as st
import json
import random

# ページ設定
st.set_page_config(page_title="銘柄マスター・クイズ", layout="centered")

@st.cache_data
def load_data():
    with open('ai_stock_dictionary_v2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

stocks = load_data()

# セッション管理
if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = "question" # "question" or "result"
    st.session_state.current_q = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.user_choice = None

def get_new_question():
    target = random.choice(stocks)
    # 不正解肢を3つ選ぶ
    distractors = random.sample([s for s in stocks if s['code'] != target['code']], 3)
    options = [target] + distractors
    random.shuffle(options)
    
    # 問題文から名前を消す（伏せ字処理）
    question_text = target['simple_desc']
    forbidden_words = [target['name'], target['name'].replace("ホールディングス", ""), "この会社"]
    for word in forbidden_words:
        question_text = question_text.replace(word, "「この企業」")
    
    st.session_state.current_q = target
    st.session_state.q_text = question_text
    st.session_state.options = options
    st.session_state.quiz_state = "question"
    st.session_state.user_choice = None

# 初回起動
if st.session_state.current_q is None:
    get_new_question()

# --- 画面表示 ---
st.title("🎓 銘柄当てクイズ：真剣勝負")
st.write("概要を読んで、正しい銘柄を選択してください。")

# 問題エリア
with st.container(border=True):
    st.subheader("💡 問題")
    st.write(f"### {st.session_state.q_text}")

# 回答エリア
st.write("---")
if st.session_state.quiz_state == "question":
    # 選択肢をボタンで表示
    for opt in st.session_state.options:
        if st.button(f"{opt['name']} ({opt['code']})", use_container_width=True, key=opt['code']):
            st.session_state.user_choice = opt
            st.session_state.quiz_state = "result"
            if opt['code'] == st.session_state.current_q['code']:
                st.session_state.score += 1
            st.rerun()

else:
    # 結果表示エリア
    is_correct = st.session_state.user_choice['code'] == st.session_state.current_q['code']
    
    if is_correct:
        st.success("✨ 正解です！")
        st.balloons()
    else:
        st.error(f"❌ 残念！正解は {st.session_state.current_q['name']} でした。")

    st.write("### 📘 各選択肢の解説")
    
    for opt in st.session_state.options:
        with st.expander(f"{opt['name']} ({opt['code']})", expanded=True):
            if opt['code'] == st.session_state.current_q['code']:
                st.write(f"**【正解！】** {opt['simple_desc']}")
            else:
                # 不正解の理由を辞書データから生成
                st.write(f"**【不適切】** この企業は：{opt['simple_desc']}")
                st.caption("※問題文の事業内容とは一致しません。")

    if st.button("次の問題へ進む ➡️", type="primary", use_container_width=True):
        get_new_question()
        st.rerun()

# サイドバー
st.sidebar.metric("現在のスコア", f"{st.session_state.score} 点")
if st.sidebar.button("スコアをリセット"):
    st.session_state.score = 0
    get_new_question()
    st.rerun()
