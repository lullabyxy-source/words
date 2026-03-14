# 手机版背单词
import streamlit as st
import random
import json
import pandas as pd
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(page_title="背单词", page_icon="♥️")

# 极小爱心标题（不占高度）
st.markdown("<h1 style='text-align:center; margin:0; padding:0; font-size:60px;'>♥️</h1>", unsafe_allow_html=True)

# 读取Excel词库
def load_words():
    df = pd.read_excel("/Users/zhaoxiaoyi/Desktop/words.xlsx")
    return df.to_dict("records")

word_list = load_words()

# 进度文件
PROGRESS_FILE = "word_progress.json"

# 初始化进度
def init_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        memory_curve = data.get("memory_curve", {})
        today_count = data.get("today_count", 0)
        last_date = data.get("last_date", "")
        today_learned_words = data.get("today_learned_words", [])
    except:
        memory_curve = {}
        today_count = 0
        last_date = ""
        today_learned_words = []

    current_date = datetime.now().strftime("%Y-%m-%d")
    if current_date != last_date:
        today_count = 0
        last_date = current_date
        today_learned_words = []
    return memory_curve, today_count, last_date, today_learned_words

memory_curve, today_count, last_date, today_learned_words = init_progress()
daily_limit = 30
today = datetime.now().strftime("%Y-%m-%d")

# 艾宾浩斯复习计划
review_intervals = [0, 1, 2, 4, 7, 15]
review_dates = []
for d in review_intervals:
    review_date = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
    review_dates.append(review_date)

# 今天要学/复习的单词
def get_today_words():
    new_words = [w for w in word_list if w["english"] not in memory_curve]
    due_review_words = []
    for word_en, info in memory_curve.items():
        if today in info.get("review_dates", []):
            due_review_words.append(word_en)
    review_words = [w for w in word_list if w["english"] in due_review_words]
    return review_words + new_words

today_word_candidates = get_today_words() or word_list

# ===================== 同一行显示（无间距） =====================
col1, col2 = st.columns(2, gap="small")
col1.metric("今天已刷", f"{today_count}/{daily_limit}")
col2.metric("历史已刷", len(memory_curve))

# ===================== 按钮同一行（强制不换行） =====================
btn_col1, btn_col2 = st.columns(2, gap="small")
with btn_col1:
    if st.button("今日份重置", use_container_width=True):
        today_count = 0
        today_learned_words = []
        save_data = {
            "memory_curve": memory_curve,
            "today_count": today_count,
            "last_date": last_date,
            "today_learned_words": today_learned_words
        }
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        st.rerun()

with btn_col2:
    if st.button("总进度重置", use_container_width=True):
        memory_curve.clear()
        today_count = 0
        today_learned_words = []
        save_data = {"memory_curve":{},"today_count":0,"last_date":last_date,"today_learned_words":[]}
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        st.rerun()

# 去掉多余空间
st.markdown("<div style='margin:5px;'></div>", unsafe_allow_html=True)

# ===================== 单词区域（小字体，超紧凑） =====================
if "current_word" not in st.session_state or st.session_state.current_word["english"] not in [w["english"] for w in today_word_candidates]:
    st.session_state.current_word = random.choice(today_word_candidates)

word = st.session_state.current_word
en = word["english"]
cn = word["chinese"]

# 单词小字体，不占高度
st.markdown(f"<p style='font-size:17px; margin:4px 0;'>英文：{en}</p>", unsafe_allow_html=True)

if st.button("📖 查看释义", use_container_width=True):
    st.success(f"释义：{cn}")

# 操作按钮（超紧凑）
k_col, u_col = st.columns(2, gap="small")
with k_col:
    know = st.button("✔️ 过", use_container_width=True)
with u_col:
    unknown = st.button("✖️ 重来", use_container_width=True)

# 艾宾浩斯记忆逻辑
if know or unknown:
    if know:
        if en not in memory_curve:
            memory_curve[en] = {"first_learn": today, "review_dates": review_dates}
        if en not in today_learned_words and today_count < daily_limit:
            today_learned_words.append(en)
            today_count += 1
        st.toast("过")

    if unknown:
        if en in memory_curve:
            del memory_curve[en]
        st.toast("重来")

    save_data = {
        "memory_curve": memory_curve,
        "today_count": today_count,
        "last_date": last_date,
        "today_learned_words": today_learned_words
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    st.session_state.current_word = random.choice(today_word_candidates)
    st.rerun()

# 完成提示
if today_count >= daily_limit:
    st.balloons()
