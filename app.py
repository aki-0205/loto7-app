import random
import datetime
import pandas as pd
import streamlit as st

# ページ基本設定
st.set_page_config(page_title="ロト7 厳選1口予測", page_icon="🎯", layout="centered")

st.title("🎯 ロト7 本日の厳選1口")
st.write("本日の日付から導き出された、唯一の厳選組み合わせを表示します。")

# 本日の日付を取得 (YYYYMMDD)
today_str = datetime.date.today().strftime("%Y%m%d")
st.info(f"📅 予測対象日: {datetime.date.today().strftime('%Y年%m月%d日')}")

# サイドバー設定
st.sidebar.header("⚙️ 条件設定")

fixed_input = st.sidebar.text_input(
    "軸数字 (固定したい数字)", 
    placeholder="例: 7, 15"
)

exclude_input = st.sidebar.text_input(
    "除外数字 (出ないと予想する数字)", 
    placeholder="例: 1, 13"
)

# 入力テキストの数値化関数
def parse_numbers(text):
    if not text.strip():
        return []
    nums = []
    for x in text.split(","):
        x = x.strip()
        if x.isdigit():
            val = int(x)
            if 1 <= val <= 37:
                nums.append(val)
    return list(set(nums))

fixed_nums = parse_numbers(fixed_input)
exclude_nums = parse_numbers(exclude_input)

# エラー表示
if len(fixed_nums) > 6:
    st.error("軸数字は最大6個まで設定可能です。")
elif set(fixed_nums) & set(exclude_nums):
    st.error("軸数字と除外数字に同じ番号が含まれています。")

# 今日の日付 + 設定値から決定論的なシード（種）を生成
seed_value = int(today_str) + sum(fixed_nums) * 100 - sum(exclude_nums)

# ボタンまたは初期表示で確定
if st.button("本日の厳選1口を表示する", type="primary"):
    # 乱数シードを固定（これで何度押しても今日一日同じ結果になる）
    random.seed(seed_value)
    
    selected = list(fixed_nums)
    pool = [i for i in range(1, 38) if i not in selected and i not in exclude_nums]
    
    if len(pool) < (7 - len(selected)):
        st.warning("候補となる数字が足りません。除外数字を減らしてください。")
    else:
        # 重み付けデータ
        weights = [10 + int(abs(hash(str(i*7))) % 20) for i in range(1, 38)]
        
        while len(selected) < 7:
            total_w = sum(weights[n-1] for n in pool)
            r = random.uniform(0, total_w)
            current = 0
            picked = pool[0]
            for n in pool:
                current += weights[n-1]
                if current >= r:
                    picked = n
                    break
            pool.remove(picked)
            selected.append(picked)

        selected.sort()
        
        odd = sum(1 for n in selected if n % 2 != 0)
        even = 7 - odd
        total_sum = sum(selected)

        # 厳選結果表示
        st.subheader("🔥 本日の厳選買い目 (1口)")
        
        # ボール風表示
        balls_html = " ".join([f"<span style='background-color:#1e3a8a; color:white; padding:8px 12px; border-radius:50%; font-weight:bold; font-size:1.1em; margin-right:6px;'>{n:02d}</span>" for n in selected])
        st.markdown(balls_html, unsafe_allow_html=True)
        st.write("")
        st.caption(f"奇偶比率: {odd}:{even} | 数字の合計: {total_sum}")
        st.success("※本日中は何回押してもこの厳選1口が固定で表示されます。")
