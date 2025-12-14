import streamlit as st
import pandas as pd
import plotly.express as px
import json
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="BIGLABO 運営シミュレーター(修正完了版v2)", layout="wide")

# --- CSSスタイル定義 ---
st.markdown("""
<style>
    .inc-text { color: #1565C0; font-weight: bold; font-size: 1.1em; } /* 濃い青 */
    .exp-text { color: #C62828; font-weight: bold; font-size: 1.1em; } /* 濃い赤 */
</style>
""", unsafe_allow_html=True)

# --- デフォルト値の定義 ---
default_values = {
    "creator_name": "担当者",
    # 基礎収支
    "inc_manage": 10000000, "inc_misc": 100000,
    "exp_wages": 5200000, "exp_utility": 1300000, "exp_maint": 1100000,
    "exp_ops_base": 1440000, "exp_insurance": 100000,
    # 施設利用
    "atelier_price": 10000, "atelier_rate": 80, 
    "ground_price": 300, "ground_count": 100,
    "memo_facility": "（例）アトリエは満室稼働を目指す。",
    # あそびっグラボ
    "asobi_price_daily": 300, "asobi_price_annual": 3000,
    "asobi_daily_users": 500, "asobi_annual_users": 50, "asobi_mat_cost": 50000,
    "memo_asobi": "（例）土日祝のみ開館想定。",
    # ショップ
    "sales_agri": 50000, "rate_agri": 10,
    "sales_craft": 100000, "rate_craft": 20,
    "sales_art": 50000, "rate_art": 30,
    "gacha_units": 2, "gacha_per_day": 3,
    "ws_users": 500, "ws_price": 500, "ws_mat_rate": 30,
    "memo_shop": "（例）農産物は地元農家5軒と契約予定。",
    # 宿泊
    "camp_groups": 50, "camp_price": 15000, "camp_option": 100000,
    "night_staff_cost": 5000, "camp_maint_cost": 50000,
    "memo_camp": "（例）繁忙期は8月と10月を想定。",
    # 企画展
    "ex_visitors": 1000, "ex_fee": 500,
    "ex_rental_cost": 50000, "ex_mat_cost": 30000,
    "ex_ad_cost": 50000, "ex_vol_count": 5,
    "memo_ex": "（例）春は「猫展」、秋は「恐竜展」を実施。",
    # イベントリスト
    "custom_events": [] 
}

# --- 初期化処理 ---
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 読み込み処理を行うコールバック関数 ---
def load_json_file():
    """ファイルアップローダーが変更されたときに呼ばれる関数"""
    uploaded = st.session_state.upload_json # アップローダーのkeyからファイル取得
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            for k, v in data.items():
                # default_valuesにあるキーで、かつ整数であるべきものはint変換
                if k in default_values:
                    if isinstance(default_values[k], int) and isinstance(v, (float, int)):
                         st.session_state[k] = int(v)
                    else:
                         st.session_state[k] = v
            st.toast("設定を読み込みました！", icon="✅")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")

# ==========================================
# サイドバー：ファイル操作
# ==========================================
with st.sidebar:
    st.header("💾 保存・読込設定")
    
    # 1. 制作者名入力 (エラー回避のため配置順はそのまま)
    st.text_input("制作者名を入力", key="creator_name")
    
    # 2. 保存ボタン
    today_str = datetime.date.today().strftime('%Y%m%d')
    file_name = f"{st.session_state.creator_name}{today_str}.json"
    current_config = {k: st.session_state[k] for k in default_values.keys()}
    json_str = json.dumps(current_config, ensure_ascii=False, indent=2)
    st.download_button("設定を保存 (PCへ)", json_str, file_name, "application/json")
    
    st.markdown("---")
    
    # 3. 読込ボタン (コールバックを使用することでエラー回避)
    st.file_uploader(
        "設定ファイルを読込", 
        type=["json"], 
        key="upload_json",       # キーを設定
        on_change=load_json_file # 変更時に上記関数を実行
    )

# ==========================================
# 1. グラフ表示エリア (トップ固定)
# ==========================================
st.title(f"🏢 BIGLABO 運営収支シミュレーター")
if st.session_state.creator_name:
    st.caption(f"作成者: {st.session_state.creator_name} ｜ 日付: {datetime.date.today()}")

top_chart_container = st.container()

# ==========================================
# 2. 入力・設定エリア
# ==========================================

# --- サイドバー：固定費 ---
st.sidebar.markdown("---")
st.sidebar.header("1. 基礎数値 (固定)")
st.sidebar.subheader("🔵 収入 (ベース)")
st.sidebar.number_input("指定管理料", step=100000, format="%d", key="inc_manage")
st.sidebar.number_input("雑収入", step=10000, format="%d", help="自販機手数料など", key="inc_misc")

st.sidebar.subheader("🔴 支出 (固定)")
st.sidebar.number_input("人件費", step=100000, format="%d", key="exp_wages")
st.sidebar.number_input("光熱水費", step=10000, format="%d", key="exp_utility")
st.sidebar.number_input("修繕・通信", step=10000, format="%d", key="exp_maint")
st.sidebar.number_input("事務運営費", step=10000, format="%d", key="exp_ops_base")
st.sidebar.number_input("保険料", step=5000, format="%d", key="exp_insurance")

base_income = st.session_state.inc_manage + st.session_state.inc_misc
base_expense = (st.session_state.exp_wages + st.session_state.exp_utility + 
                st.session_state.exp_maint + st.session_state.exp_ops_base + 
                st.session_state.exp_insurance)

# --- メイン：事業収支 ---
tab_asobi, tab_facility, tab_shop, tab_camp, tab_ex, tab_custom = st.tabs([
    "🎨 あそびっグラボ", "🏢 施設利用(アトリエ等)", "🛍️ 常設・ショップ", "⛺ 宿泊・体験", "🖼️ 企画展", "🎪 カスタムイベント"
])

# ① あそびっグラボ
with tab_asobi:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown('<p class="inc-text">🔵 収入項目</p>', unsafe_allow_html=True)
        c_daily1, c_daily2 = st.columns([1, 2])
        c_daily1.number_input("1日利用料", step=100, format="%d", key="asobi_price_daily")
        c_daily2.slider("年間利用者数(人)", 0, 5000, key="asobi_daily_users")
        
        st.markdown("---")
        c_annual1, c_annual2 = st.columns([1, 2])
        c_annual1.number_input("年パス料金", step=1000, format="%d", key="asobi_price_annual")
        # ★ここを変更: 最大値を2000に変更
        c_annual2.slider("年間購入者数(人)", 0, 2000, key="asobi_annual_users")

    with col_a2:
        st.markdown('<p class="exp-text">🔴 支出項目</p>', unsafe_allow_html=True)
        st.number_input("材料費など (年額)", step=10000, format="%d", key="asobi_mat_cost")

    asobi_income = (st.session_state.asobi_price_daily * st.session_state.asobi_daily_users) + \
                   (st.session_state.asobi_price_annual * st.session_state.asobi_annual_users)
    asobi_expense = st.session_state.asobi_mat_cost
    
    st.markdown("---")
    st.text_area("📝 メモ・備考", key="memo_asobi")
    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("収入計", f"¥{asobi_income:,.0f}")
    bc2.metric("支出計", f"¥{asobi_expense:,.0f}")
    bc3.metric("利益", f"¥{asobi_income - asobi_expense:,.0f}")

# ② 施設利用
with tab_facility:
    st.info("貸しアトリエとグランド利用の収入計算です。")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.markdown('<p class="inc-text">🔵 貸しアトリエ (全7部屋)</p>', unsafe_allow_html=True)
        st.number_input("1部屋 月額(円)", step=1000, format="%d", key="atelier_price")
        st.slider("入居率 (%)", 0, 100, key="atelier_rate")
        
        atelier_income = 7 * st.session_state.atelier_price * 12 * (st.session_state.atelier_rate / 100)
        st.metric("アトリエ年間収入", f"¥{atelier_income:,.0f}", help="7部屋×月額×12ヶ月×入居率")

    with col_f2:
        st.markdown('<p class="inc-text">🔵 グランド利用</p>', unsafe_allow_html=True)
        st.number_input("1回あたり単価(円)", step=100, format="%d", key="ground_price")
        st.number_input("年間利用回数", step=10, format="%d", key="ground_count")
        
        ground_income = st.session_state.ground_price * st.session_state.ground_count
        st.metric("グランド年間収入", f"¥{ground_income:,.0f}")
        
    facility_income_total = atelier_income + ground_income
    
    st.markdown("---")
    st.text_area("📝 メモ・備考", key="memo_facility")
    
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("収入計", f"¥{facility_income_total:,.0f}")
    fc2.metric("支出計", "¥0")
    fc3.metric("利益", f"¥{facility_income_total:,.0f}")

# ③ 常設・ショップ
with tab_shop:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<p class="inc-text">🔵 収入項目 (委託販売)</p>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([2, 1])
        col_s1.number_input("🍅 農産物 売上(月)", step=5000, format="%d", key="sales_agri")
        col_s2.number_input("手数料(%)", min_value=0, max_value=100, step=1, format="%d", key="rate_agri")
        
        col_s3, col_s4 = st.columns([2, 1])
        col_s3.number_input("🧶 工芸品 売上(月)", step=5000, format="%d", key="sales_craft")
        col_s4.number_input("手数料(%)", min_value=0, max_value=100, step=1, format="%d", key="rate_craft")

        col_s5, col_s6 = st.columns([2, 1])
        col_s5.number_input("🎨 美術品 売上(月)", step=5000, format="%d", key="sales_art")
        col_s6.number_input("手数料(%)", min_value=0, max_value=100, step=1, format="%d", key="rate_art")

    with c2:
        st.markdown('<p class="inc-text">🔵 収入項目 (その他)</p>', unsafe_allow_html=True)
        st.number_input("ガチャ台数", step=1, format="%d", key="gacha_units")
        st.slider("ガチャ回転/日", 0, 30, key="gacha_per_day")
        
        st.caption("※旧WS項目(不要なら0)")
        st.number_input("WS利用者数/年", step=10, format="%d", key="ws_users")
        st.number_input("WS単価", step=100, format="%d", key="ws_price")
    
    # 計算
    shop_inc_total = (st.session_state.sales_agri * 12) + (st.session_state.sales_craft * 12) + (st.session_state.sales_art * 12) + \
                     (500 * st.session_state.gacha_units * st.session_state.gacha_per_day * 250) + \
                     (st.session_state.ws_users * st.session_state.ws_price)
                     
    shop_exp_total = (st.session_state.sales_agri * 12 * (1 - st.session_state.rate_agri/100)) + \
                     (st.session_state.sales_craft * 12 * (1 - st.session_state.rate_craft/100)) + \
                     (st.session_state.sales_art * 12 * (1 - st.session_state.rate_art/100)) + \
                     (500 * st.session_state.gacha_units * st.session_state.gacha_per_day * 250 * 0.8) + \
                     (st.session_state.ws_users * st.session_state.ws_price * (st.session_state.ws_mat_rate/100))

    st.markdown("---")
    st.text_area("📝 メモ・備考", key="memo_shop")
    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("収入計", f"¥{shop_inc_total:,.0f}")
    bc2.metric("支出計", f"¥{shop_exp_total:,.0f}")
    bc3.metric("利益", f"¥{shop_inc_total - shop_exp_total:,.0f}")

# ④ 宿泊・体験
with tab_camp:
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown('<p class="inc-text">🔵 収入項目</p>', unsafe_allow_html=True)
        st.number_input("利用組数/年", step=1, format="%d", key="camp_groups")
        st.number_input("宿泊単価", step=1000, format="%d", key="camp_price")
        st.number_input("オプション収入", step=1000, format="%d", key="camp_option")
    with cc2:
        st.markdown('<p class="exp-text">🔴 支出項目</p>', unsafe_allow_html=True)
        st.number_input("夜間手当/回", step=1000, format="%d", key="night_staff_cost")
        st.number_input("設備維持費(年)", step=1000, format="%d", key="camp_maint_cost")
    
    camp_inc = (st.session_state.camp_groups * st.session_state.camp_price) + st.session_state.camp_option
    camp_exp = (st.session_state.camp_groups * st.session_state.night_staff_cost) + st.session_state.camp_maint_cost
    
    st.markdown("---")
    st.text_area("📝 メモ・備考", key="memo_camp")
    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("収入計", f"¥{camp_inc:,.0f}")
    bc2.metric("支出計", f"¥{camp_exp:,.0f}")
    bc3.metric("利益", f"¥{camp_inc - camp_exp:,.0f}")

# ⑤ 企画展
with tab_ex:
    ce1, ce2 = st.columns(2)
    with ce1:
        st.markdown('<p class="inc-text">🔵 収入項目</p>', unsafe_allow_html=True)
        st.number_input("観覧料 (円)", step=100, format="%d", key="ex_fee")
        st.number_input("有料入場者数 (人)", step=10, format="%d", key="ex_visitors")
        ex_inc = st.session_state.ex_visitors * st.session_state.ex_fee
    with ce2:
        st.markdown('<p class="exp-text">🔴 支出項目</p>', unsafe_allow_html=True)
        st.number_input("1. 作品賃借料", step=10000, format="%d", key="ex_rental_cost")
        st.number_input("2. 材料費", step=5000, format="%d", key="ex_mat_cost")
        st.number_input("3. 広告宣伝費", step=10000, format="%d", key="ex_ad_cost")
        st.number_input("4. ボランティア人数(1万円/人)", step=1, format="%d", key="ex_vol_count")
        ex_exp = st.session_state.ex_rental_cost + st.session_state.ex_mat_cost + st.session_state.ex_ad_cost + (st.session_state.ex_vol_count * 10000)

    st.markdown("---")
    st.text_area("📝 メモ・備考", key="memo_ex")
    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("収入計", f"¥{ex_inc:,.0f}")
    bc2.metric("支出計", f"¥{ex_exp:,.0f}")
    bc3.metric("利益", f"¥{ex_inc - ex_exp:,.0f}")

# ⑥ カスタムイベント
custom_event_income = 0
custom_event_expense = 0
custom_event_memos = []
with tab_custom:
    with st.form("add_event", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        n = c1.text_input("イベント名")
        c2.markdown('<span class="inc-text">🔵 収入</span>', unsafe_allow_html=True)
        i = c2.number_input("金額", step=10000, format="%d", key="cust_i")
        c3.markdown('<span class="exp-text">🔴 支出</span>', unsafe_allow_html=True)
        e = c3.number_input("金額", step=10000, format="%d", key="cust_e")
        m = c4.text_input("メモ・備考")
        if st.form_submit_button("追加"):
            if n:
                st.session_state.custom_events.append({"name":n, "inc":i, "exp":e, "memo":m})
                st.rerun()
    
    if st.session_state.custom_events:
        st.markdown("---")
        for idx, ev in enumerate(st.session_state.custom_events):
            custom_event_income += ev['inc']
            custom_event_expense += ev['exp']
            memo_text = ev.get('memo', '')
            if memo_text: custom_event_memos.append(f"{ev['name']}({memo_text})")
            else: custom_event_memos.append(f"{ev['name']}")
            
            col_a, col_b, col_c, col_d, col_e = st.columns([2, 1, 1, 2, 0.5])
            col_a.write(f"**{ev['name']}**")
            col_b.write(f"収: ¥{ev['inc']:,}")
            col_c.write(f"支: ¥{ev['exp']:,}")
            col_d.caption(f"📝 {memo_text}")
            if col_e.button("削除", key=f"del_{idx}"):
                st.session_state.custom_events.pop(idx)
                st.rerun()

# ==========================================
# 3. 集計・チャート・詳細テーブル
# ==========================================
total_revenue = base_income + asobi_income + facility_income_total + shop_inc_total + camp_inc + ex_inc + custom_event_income
total_expense = base_expense + asobi_expense + shop_exp_total + camp_exp + ex_exp + custom_event_expense
profit = total_revenue - total_expense

# --- トップチャート ---
with top_chart_container:
    k1, k2, k3 = st.columns(3)
    k1.metric("総収入", f"¥{total_revenue:,.0f}")
    k2.metric("総支出", f"¥{total_expense:,.0f}")
    k3.metric("最終収支", f"¥{profit:,.0f}", delta_color="normal" if profit >= 0 else "inverse")

    g1, g2, g3 = st.columns([1,1,1.5])
    
    df_inc_chart = pd.DataFrame({
        "カテゴリ": ["基礎(指定管理+雑)", "あそびっグラボ", "施設利用(アトリエ等)", "常設・ショップ", "宿泊・体験", "企画展", "カスタムイベント"],
        "金額": [base_income, asobi_income, facility_income_total, shop_inc_total, camp_inc, ex_inc, custom_event_income]
    })
    fig_inc = px.pie(df_inc_chart, values='金額', names='カテゴリ', title="収入内訳", hole=0.4)
    fig_inc.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0))
    g1.plotly_chart(fig_inc, use_container_width=True)

    df_exp_chart = pd.DataFrame({
        "カテゴリ": ["基礎(人件費等)", "あそびグラボ費", "ショップ原価", "宿泊費", "企画展費", "イベント費"],
        "金額": [base_expense, asobi_expense, shop_exp_total, camp_exp, ex_exp, custom_event_expense]
    })
    fig_exp = px.pie(df_exp_chart, values='金額', names='カテゴリ', title="支出内訳", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Reds_r)
    fig_exp.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0))
    g2.plotly_chart(fig_exp, use_container_width=True)

    df_balance = pd.DataFrame({
        "種別": ["収入", "支出"],
        "金額": [total_revenue, total_expense]
    })
    fig_bar = px.bar(df_balance, x="金額", y="種別", orientation='h', color="種別", title="全体収支バランス",
                     color_discrete_map={"収入":"#1f77b4", "支出":"#C62828"}, text_auto=',.0f')
    fig_bar.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0))
    g3.plotly_chart(fig_bar, use_container_width=True)

# --- ページ下部：詳細収支テーブル ---
st.markdown("### 📋 カテゴリ別 収支明細表")
custom_events_str = "、".join(custom_event_memos) if custom_event_memos else "なし"
detail_data = [
    ["基礎数値(指定管理・雑)", base_income, base_expense, base_income - base_expense, "-"],
    ["あそびっグラボ", asobi_income, asobi_expense, asobi_income - asobi_expense, st.session_state.memo_asobi],
    ["施設利用(アトリエ等)", facility_income_total, 0, facility_income_total, st.session_state.memo_facility],
    ["常設・ショップ", shop_inc_total, shop_exp_total, shop_inc_total - shop_exp_total, st.session_state.memo_shop],
    ["宿泊・体験", camp_inc, camp_exp, camp_inc - camp_exp, st.session_state.memo_camp],
    ["企画展", ex_inc, ex_exp, ex_inc - ex_exp, st.session_state.memo_ex],
    ["カスタムイベント", custom_event_income, custom_event_expense, custom_event_income - custom_event_expense, custom_events_str],
    ["★ 合計", total_revenue, total_expense, profit, ""]
]
df_detail = pd.DataFrame(detail_data, columns=["項目", "収入", "支出", "収支差益", "備考"])
st.dataframe(
    df_detail.style.format({"収入": "¥{:,.0f}", "支出": "¥{:,.0f}", "収支差益": "¥{:,.0f}"})
    .applymap(lambda x: 'color: red;' if isinstance(x, (int, float)) and x < 0 else 'color: blue;' if isinstance(x, (int, float)) else '', subset=['収支差益']),
    use_container_width=True
)
