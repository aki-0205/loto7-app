import random
import pandas as pd
import streamlit as st

# ページ基本設定
st.set_page_config(page_title="ロト7 厳選予測アプリ", page_icon="🎲", layout="centered")

st.title("🎲 ロト7 厳選予測アプリ")
st.write("軸数字や条件を設定して、狙い目の組み合わせを自動生成します。")

# サイドバー設定
st.sidebar.header("⚙️ 条件設定")

algo = st.sidebar.selectbox(
    "抽出モード",
    ["バランス重視 (奇偶3:4〜4:3)", "高頻度重視 (データ連動)", "完全ランダム"]
)

# 初期値を「1口（厳選1選）」に設定
count = st.sidebar.slider("生成口数", min_value=1, max_value=10, value=1)

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

# 生成ボタン
if st.button("厳選数字を予測・生成する", type="primary"):
    results = []
    
    # 擬似重みデータ（1〜37）
    weights = [10 + int(abs(hash(str(i*7))) % 20) for i in range(1, 38)]
    
    for _ in range(count * 20): # 試行回数
        selected = list(fixed_nums)
        pool = [i for i in range(1, 38) if i not in selected and i not in exclude_nums]
        
        if len(pool) < (7 - len(selected)):
            st.warning("候補となる数字が足りません。除外数字を減らしてください。")
            break

        while len(selected) < 7:
            if "高頻度重視" in algo:
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
            else:
                picked = random.choice(pool)
                pool.remove(picked)
                selected.append(picked)

        selected.sort()
        
        # バランス重視フィルター
        if "バランス重視" in algo:
            odd_count = sum(1 for n in selected if n % 2 != 0)
            if odd_count < 3 or odd_count > 4:
                continue

        odd = sum(1 for n in selected if n % 2 != 0)
        even = 7 - odd
        total_sum = sum(selected)
        
        results.append((selected, odd, even, total_sum))
        if len(results) >= count:
            break

    # 結果出力
    st.subheader("🎯 厳選予想結果")
    for idx, (res, odd, even, total) in enumerate(results, 1):
        # ボール風表示
        balls_html = " ".join([f"<span style='background-color:#1e3a8a; color:white; padding:6px 10px; border-radius:50%; font-weight:bold; margin-right:4px;'>{n:02d}</span>" for n in res])
        st.markdown(f"**第 {idx} 候補**", unsafe_allow_html=True)
        st.markdown(balls_html, unsafe_allow_html=True)
        st.caption(f"奇偶比率: {odd}:{even} | 数字の合計: {total}")
        st.divider()
