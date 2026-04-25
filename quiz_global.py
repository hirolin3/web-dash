import streamlit as st
import json
import random

# ページ設定
st.set_page_config(page_title="日米銘柄マスタークイズ", layout="centered")

# 1. データの読み込み
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_smart_distractors(target, all_stocks):
    """
    ターゲットに対して「似た名前」または「同じ業種」の選択肢を優先的に選ぶ
    """
    distractors = []
    
    # 1. 似た名前を探す（例：三菱、三井、日本、HDなどを含むもの）
    # 最初の2文字くらいが一致するものを探す
    prefix = target['name'][:2]
    similar_names = [s for s in all_stocks if s['name'].startswith(prefix) and s['name'] != target['name']]
    distractors.extend(similar_names)
    
    # 2. 同じ業種から補充
    same_industry = [s for s in all_stocks if s.get('industry') == target.get('industry') and s not in distractors and s['name'] != target['name']]
    distractors.extend(same_industry)
    
    # それでも足りなければランダム
    if len(distractors) < 3:
        others = [s for s in all_stocks if s not in distractors and s['name'] != target['name']]
        distractors.extend(random.sample(others, 3 - len(distractors)))
    
    # 上位3つ（似た名前 or 同業）をハズレとして採用
    return random.sample(distractors[:8], 3) # 上位8件からランダムに3つ選ぶと毎回変わって良い

# 2. セッション状態の管理
if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = "question"
    st.session_state.current_q = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.user_choice = None
    st.session_state.mode = "日本株 (日経225)"

# サイドバーでモード切り替え
st.sidebar.title("🎮 設定")
mode = st.sidebar.radio("挑戦する市場を選択:", ["日本株 (日経225)", "米国株 (トップ200)"])

# モードが変わったらクイズをリセット
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.current_q = None
    st.rerun()

# ファイルパスの決定
if mode == "日本株 (日経225)":
    data_file = 'ai_stock_dictionary_ollama_quiz.json'
    code_key = 'code'
else:
    data_file = 'us_stock_dictionary_us200.json'
    code_key = 'symbol'

stocks = load_data(data_file)

def get_new_question():
    target = random.choice(stocks)
    # 同業種がいれば優先的にハズレにする（日本株のみ業種データありの場合）
    industry = target.get('industry')
    if industry:
        distractors = random.sample([s for s in stocks if s.get('industry') == industry and s[code_key] != target[code_key]], min(3, len([s for s in stocks if s.get('industry') == industry]) - 1))
        # 足りない分をランダムで補充
        if len(distractors) < 3:
            others = random.sample([s for s in stocks if s[code_key] != target[code_key] and s not in distractors], 3 - len(distractors))
            distractors += others
    else:
        distractors = random.sample([s for s in stocks if s[code_key] != target[code_key]], 3)
    
    options = [target] + distractors
    random.shuffle(options)
    
    st.session_state.current_q = target
    st.session_state.options = options
    st.session_state.quiz_state = "question"
    st.session_state.user_choice = None

# 初回・リセット時の出題
if st.session_state.current_q is None:
    get_new_question()

# --- 画面表示 ---
st.title(f"🎓 {mode} クイズ")
st.write("概要を読んで、正しい銘柄を選択してください。")

with st.container(border=True):
    st.subheader("💡 問題")
    st.write(f"### {st.session_state.current_q['simple_desc']}")

st.write("---")
if st.session_state.quiz_state == "question":
    for opt in st.session_state.options:
        label = f"{opt['name']} ({opt[code_key]})"
        if st.button(label, use_container_width=True, key=opt[code_key]):
            st.session_state.user_choice = opt
            st.session_state.quiz_state = "result"
            if opt[code_key] == st.session_state.current_q[code_key]:
                st.session_state.score += 1
            st.rerun()
else:
    # 結果表示
    is_correct = st.session_state.user_choice[code_key] == st.session_state.current_q[code_key]
    if is_correct:
        st.success("✨ 正解です！")
        st.balloons()
    else:
        st.error(f"❌ 残念！正解は {st.session_state.current_q['name']} でした。")

    st.write(f"**💡 解説:** {st.session_state.current_q['explanation']}")
    
    with st.expander("各銘柄の正体を見る"):
        for opt in st.session_state.options:
            st.write(f"**{opt['name']} ({opt[code_key]})**")
            st.caption(opt['simple_desc'])

    if st.button("次の問題へ進む ➡️", type="primary", use_container_width=True):
        get_new_question()
        st.rerun()

st.sidebar.metric("現在の正解数", f"{st.session_state.score} 点")
