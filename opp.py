import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(page_title="BIGLABO アートイベント収支シミュレーション", layout="wide")

st.title("🎨 BIGLABO 夜のアートイベント 収支シミュレーション")
st.markdown("各パラメータを調整して、収支バランスをリアルタイムで確認できます。")

# --- サイドバー：パラメータ入力 ---
st.sidebar.header("📊 シミュレーション条件設定")

# 1. 収入のパラメータ
st.sidebar.subheader("1. 収入 (Income)")
ticket_price = st.sidebar.number_input("チケット単価 (円)", value=2500, step=100)
visitors = st.sidebar.slider("想定来場者数 (人)", min_value=0, max_value=300, value=80, step=5)

merch_avg = st.sidebar.number_input("物販・飲食 客単価 (円/オーダー)", value=500, step=50)
merch_count = st.sidebar.slider("物販・飲食 購入数 (オーダー)", min_value=0, max_value=visitors, value=60)

sponsorship = st.sidebar.number_input("協賛・助成金 合計 (円)", value=20000, step=5000)
workshop_fee = st.sidebar.number_input("WS参加費 (円)", value=1000, step=100)
workshop_participants = st.sidebar.slider("WS参加人数 (人)", min_value=0, max_value=50, value=10)

# 2. 支出のパラメータ
st.sidebar.subheader("2. 支出 (Expenses)")
venue_cost = st.sidebar.number_input("会場費・光熱費 (円)", value=15000, step=1000)

staff_wage = st.sidebar.number_input("スタッフ日当 (円/人)", value=8000, step=500)
staff_count = st.sidebar.slider("スタッフ人数 (人)", min_value=1, max_value=20, value=3)

artist_fee = st.sidebar.number_input("出演・制作費 (円)", value=60000, step=5000)
decoration_cost = st.sidebar.number_input("会場装飾費 (円)", value=20000, step=1000)
ads_cost = st.sidebar.number_input("広告宣伝費 (円)", value=15000, step=1000)
misc_cost = st.sidebar.number_input("予備費・雑費 (円)", value=5000, step=1000)

# --- 計算ロジック ---
# 収入計算
inc_ticket = ticket_price * visitors
inc_merch = merch_avg * merch_count
inc_ws = workshop_fee * workshop_participants
total_income = inc_ticket + inc_merch + sponsorship + inc_ws

# 支出計算
exp_staff = staff_wage * staff_count
total_expense = venue_cost + exp_staff + artist_fee + decoration_cost + ads_cost + misc_cost

# 利益計算
profit = total_income - total_expense

# --- メイン画面表示 ---

# 1. 重要指標 (KPI)
col1, col2, col3 = st.columns(3)
col1.metric("総収入", f"¥{total_income:,}")
col2.metric("総支出", f"¥{total_expense:,}")
col3.metric("収支差益 (利益)", f"¥{profit:,}", delta_color="normal")

st.markdown("---")

# 2. グラフによる可視化
col_chart1, col_chart2 = st.columns(2)

# データフレーム作成（収入内訳）
df_inc = pd.DataFrame({
    "項目": ["チケット", "物販・飲食", "協賛・助成", "WS"],
    "金額": [inc_ticket, inc_merch, sponsorship, inc_ws]
})

# データフレーム作成（支出内訳）
df_exp = pd.DataFrame({
    "項目": ["会場費", "人件費", "出演・制作", "装飾費", "広告費", "予備費"],
    "金額": [venue_cost, exp_staff, artist_fee, decoration_cost, ads_cost, misc_cost]
})

with col_chart1:
    st.subheader("💰 収入の内訳")
    fig_inc = px.pie(df_inc, values='金額', names='項目', hole=0.4)
    st.plotly_chart(fig_inc, use_container_width=True)

with col_chart2:
    st.subheader("💸 支出の内訳")
    fig_exp = px.pie(df_exp, values='金額', names='項目', hole=0.4)
    st.plotly_chart(fig_exp, use_container_width=True)

# 3. 損益分岐点の簡易分析
st.subheader("📊 収支バランス棒グラフ")
df_balance = pd.DataFrame({
    "区分": ["収入", "支出"],
    "金額": [total_income, total_expense],
    "色": ["blue", "red"]
})
fig_bar = px.bar(df_balance, x="金額", y="区分", orientation='h', text="金額", color="区分",
                 color_discrete_map={"収入": "#4CAF50", "支出": "#FF5252"})
st.plotly_chart(fig_bar, use_container_width=True)

# アラート表示
if profit < 0:
    st.error(f"⚠️ 現在 {abs(profit):,} 円の赤字です。集客数を増やすか、経費を見直してください。")
else:
    st.success(f"🎉 現在 {profit:,} 円の黒字見込みです！")

st.markdown("---")

# --- CSV保存機能（ここを追加しました） ---
st.subheader("💾 シミュレーション結果の保存")

# 保存用のデータを作成
export_data = [
    {"区分": "収入", "項目": "チケット売上", "金額": inc_ticket, "詳細": f"単価{ticket_price}円 × {visitors}人"},
    {"区分": "収入", "項目": "物販・飲食", "金額": inc_merch, "詳細": f"客単価{merch_avg}円 × {merch_count}件"},
    {"区分": "収入", "項目": "協賛・助成", "金額": sponsorship, "詳細": "固定額"},
    {"区分": "収入", "項目": "WS参加費", "金額": inc_ws, "詳細": f"単価{workshop_fee}円 × {workshop_participants}人"},
    {"区分": "支出", "項目": "会場費", "金額": venue_cost, "詳細": "光熱費込"},
    {"区分": "支出", "項目": "人件費", "金額": exp_staff, "詳細": f"日当{staff_wage}円 × {staff_count}人"},
    {"区分": "支出", "項目": "出演・制作費", "金額": artist_fee, "詳細": ""},
    {"区分": "支出", "項目": "会場装飾費", "金額": decoration_cost, "詳細": ""},
    {"区分": "支出", "項目": "広告宣伝費", "金額": ads_cost, "詳細": ""},
    {"区分": "支出", "項目": "予備費", "金額": misc_cost, "詳細": ""},
    {"区分": "集計", "項目": "【利益】", "金額": profit, "詳細": "収入 - 支出"},
]

df_export = pd.DataFrame(export_data)

# CSV変換（Excelで開けるようにutf-8-sigを使用）
csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')

st.download_button(
    label="現在の数値をCSVでダウンロード",
    data=csv_data,
    file_name="simulation_result.csv",
    mime="text/csv"
)