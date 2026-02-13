import streamlit as st
import pandas as pd
import datetime

# --- Configuration ---
st.set_page_config(
    page_title="コアラメモ",
    page_icon="koalaface.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Constants & Data ---
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQi6GZ0pWmE1A0MSJBoSyHYaKvAHkgFeBRvZPmMHqHLBh53VzAr5nyJ43qOVuTj4y2xus5nzzurKmUX/pub?gid=107153803&single=true&output=csv"

ZOO_URLS = {
    "東山": "https://www.higashiyama.city.nagoya.jp/", "東山動植物園": "https://www.higashiyama.city.nagoya.jp/",
    "多摩": "https://www.tokyo-zoo.net/zoo/tama/", "多摩動物公園": "https://www.tokyo-zoo.net/zoo/tama/",
    "埼玉": "https://www.parks.or.jp/sczoo/", "埼玉県こども": "https://www.parks.or.jp/sczoo/", "埼玉県こども動物自然公園": "https://www.parks.or.jp/sczoo/",
    "平川": "https://hirakawazoo.jp/", "平川動物公園": "https://hirakawazoo.jp/",
    "金沢": "https://www.hama-midorinokyokai.or.jp/zoo/kanazawa/", "横浜金沢": "https://www.hama-midorinokyokai.or.jp/zoo/kanazawa/", "金沢動物園": "https://www.hama-midorinokyokai.or.jp/zoo/kanazawa/", "横浜市立金沢動物園": "https://www.hama-midorinokyokai.or.jp/zoo/kanazawa/",
    "王子": "https://www.kobe-ojizoo.jp/", "神戸市王子": "https://www.kobe-ojizoo.jp/", "神戸市立王子動物園": "https://www.kobe-ojizoo.jp/",
    "淡路": "https://www.england-hill.com/", "イングランドの丘": "https://www.england-hill.com/",
    "天王寺": "https://www.tennojizoo.jp/", "天王寺動物園": "https://www.tennojizoo.jp/"
}

# --- CSS Injection ---
STYLING = """
<style>
    .stApp { background-color: #f4f7f6; color: #333; font-family: "Helvetica Neue", Arial, sans-serif; }
    .main-header { text-align: center; margin-bottom: 20px; color: #2e7d32; font-size: 1.8em; font-weight: bold; cursor: pointer; }
    .subtitle { text-align: center; color: #666; font-size: 0.8em; margin-top: -10px; margin-bottom: 20px; }
    
    /* Card Styling */
    .koala-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #2e7d32;
        margin-bottom: 10px; color: #333;
    }
    .deceased-style { background-color: #f0f0f0; border-color: #ccc !important; color: #666; }
    .parent-hero { background-color: #e8f5e9; border: 2px solid #2e7d32; }

    .koala-name { font-size: 1.2em; font-weight: bold; color: #333; display: inline-block; margin-right: 5px; }
    .badge { font-size: 0.7em; padding: 2px 6px; border-radius: 10px; color: white; vertical-align: middle; display: inline-block; margin-right: 2px;}
    .male { background-color: #4A90E2; }
    .female { background-color: #E24A8D; }
    .other { background-color: #999; }
    .age { background-color: #2ecc71; }
    .deceased-badge { background-color: #999; }

    .koala-zoo {
        display: inline-block; background-color: #e8f5e9; color: #2e7d32;
        padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;
        margin-bottom: 8px; margin-top: 5px;
    }
    .deceased-style .koala-zoo { background-color: #eee; color: #666; }

    .detail-grid { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; font-size: 0.85em; color: #444; }
    
    /* Buttons in Streamlit columns can be tight, custom styling not always applied to inner buttons easily */
    /* Birthday Section */
    .birthday-section {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 2px solid #ffcc80; text-align: center;
    }
    .birthday-title { color: #e65100; font-weight: bold; font-size: 1.1em; margin-bottom: 10px; }
    
    /* Pedigree Table */
    .pedigree-table {
        display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: repeat(4, 1fr);
        gap: 2px; border: 2px solid #2e7d32; background-color: #2e7d32; width: 100%; margin: 10px auto;
    }
    .ped-cell { background-color: #f9f9f9; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 5px 2px; text-align: center; font-size: 0.75em; }
    .ped-pos-self { font-size: 1em; background-color: #e8f5e9; font-weight: bold; }
    .ped-male { border-left: 3px solid #4A90E2; }
    .ped-female { border-left: 3px solid #E24A8D; }
    
    .ped-pos-ff { grid-column: 1; grid-row: 1; }
    .ped-pos-fm { grid-column: 1; grid-row: 2; }
    .ped-pos-mf { grid-column: 1; grid-row: 3; }
    .ped-pos-mm { grid-column: 1; grid-row: 4; }
    .ped-pos-father { grid-column: 2; grid-row: 1 / 3; }
    .ped-pos-mother { grid-column: 2; grid-row: 3 / 5; }
    .ped-pos-self { grid-column: 3; grid-row: 1 / 5; }

    /* Siblings */
    .sibling-item { padding: 5px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; font-size: 0.9em; }
    .sibling-section-title { font-weight: bold; color: #2e7d32; border-bottom: 2px solid #a5d6a7; margin-top: 10px; font-size: 0.9em; }
</style>
"""

# --- Helpers ---
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df = df[df['name'].notna() & (df['name'] != "")]
    df['id'] = df['id'].astype(str)
    df['father_id'] = df['father_id'].fillna("").astype(str).replace("nan", "").replace("0.0", "")
    df['mother_id'] = df['mother_id'].fillna("").astype(str).replace("nan", "").replace("0.0", "")
    df['father'] = df['father'].fillna("不明")
    df['mother'] = df['mother'].fillna("不明")
    df['memo'] = df['memo'].fillna("")
    df['zoo'] = df['zoo'].fillna("-")
    df['gender'] = df['gender'].fillna("不明")
    df['birthday'] = df['birthday'].fillna("-")
    df['age'] = df['age'].fillna("-")
    df['death'] = df['death'].fillna("")
    return df

def check_is_dead(row):
    return (str(row['death']).strip() != "") or (row['age'] == "没年齢不明")

def get_gender_class(gender):
    if "オス" in str(gender): return "male"
    if "メス" in str(gender): return "female"
    return "other"

def get_pedigree_style(k):
    if pd.isna(k) or k is None: return ""
    return "ped-male" if "オス" in str(k.get('gender', '')) else "ped-female"

# --- View Helpers ---
def render_koala_card(koala, section_key, is_hero=False):
    is_dead = check_is_dead(koala)
    dead_class = "deceased-style" if is_dead else ""
    hero_class = "parent-hero" if is_hero else ""
    gender_cls = get_gender_class(koala['gender'])
    
    zoo_url = ZOO_URLS.get(koala['zoo'], "")
    zoo_html = f"📍 {koala['zoo']}"
    if zoo_url:
        zoo_html = f'<a href="{zoo_url}" target="_blank" class="zoo-link">📍 {koala["zoo"]} 🔗</a>'
        
    insta_url = f"https://www.instagram.com/explore/tags/{koala['name']}/"
    
    father_name = koala['father'] if koala.get('father') else "-"
    mother_name = koala['mother'] if koala.get('mother') else "-"
    
    # HTML Card
    html = f"""
    <div class="koala-card {dead_class} {hero_class}">
        <div class="koala-header">
            <span class="koala-name">{'🌈 ' if is_dead else ''}{koala['name']}</span>
            <span class="badge {gender_cls}">{koala['gender']}</span>
            <span class="badge {'deceased-badge' if is_dead else 'age'}">{koala['age']}</span>
        </div>
        <div class="koala-zoo">{zoo_html}</div>
        <div class="detail-grid">
            <span>🎂</span> <span>{koala['birthday']}</span>
            <span>💙</span> <span>父：{father_name}</span>
            <span>🧡</span> <span>母：{mother_name}</span>
        </div>
        {f'<div style="font-size:0.8em; margin-top:5px; background:#f9f9f9; padding:5px;">{koala["memo"]}</div>' if koala['memo'] and is_hero else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    # Buttons Area
    # Use columns for buttons to keep them compact
    c1, c2, c3, c4 = st.columns(4)
    # Important: FIXED KEYS using section_key and koala ID
    with c1:
        if st.button("🧬 家族", key=f"ped_{section_key}_{koala['id']}"):
            st.session_state.modal_mode = "pedigree"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c2:
        if st.button("🍒 兄弟", key=f"sib_{section_key}_{koala['id']}"):
            st.session_state.modal_mode = "siblings"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c3:
        if st.button("🥰 子供", key=f"fam_{section_key}_{koala['id']}"):
            go_to_family(koala['id'])
    with c4:
        st.markdown(f'<a href="{insta_url}" target="_blank" style="text-decoration:none; display:flex; align-items:center; justify-content:center; height:100%;"><button style="width:100%; border:1px solid #f8bbd0; background-color:#fce4ec; color:#d81b60; padding:0.25rem 0.5rem; font-size:0.8rem; border-radius:0.25rem; cursor:pointer;">📷</button></a>', unsafe_allow_html=True)


# --- Navigation ---
def go_home():
    st.session_state.view = 'home'
    st.session_state.selected_id = None
    st.session_state.modal_mode = None
    st.rerun()

def go_to_family(id_):
    st.session_state.view = 'family'
    st.session_state.selected_id = str(id_)
    st.session_state.modal_mode = None
    st.rerun()

# --- Main App ---
def main():
    st.markdown(STYLING, unsafe_allow_html=True)
    
    # State Init
    if 'view' not in st.session_state: st.session_state.view = 'home'
    if 'selected_id' not in st.session_state: st.session_state.selected_id = None
    if 'modal_mode' not in st.session_state: st.session_state.modal_mode = None 
    if 'birthday_offset' not in st.session_state: st.session_state.birthday_offset = 0
    if 'show_dead_birthday' not in st.session_state: st.session_state.show_dead_birthday = False

    df = load_data()
    
    # Header (clickable to home)
    st.markdown('<div class="main-header">🐨 コアラメモ 🐨</div>', unsafe_allow_html=True)
    if st.button("🏠 ホームに戻る", key="home_btn", use_container_width=True):
        go_home()
    
    # --- Modals Overlay ---
    if st.session_state.modal_mode:
        k_id = st.session_state.modal_target_id
        target_rows = df[df['id'] == k_id]
        
        if not target_rows.empty:
            target = target_rows.iloc[0]
            
            # Using st.dialog (Streamlit 1.34+)
            @st.dialog("詳細情報", width="small")
            def show_modal():
                if st.session_state.modal_mode == "pedigree":
                    st.subheader(f"🧬 {target['name']} の家族さん")
                    # Pedigree Logic
                    def get_k(kid): 
                        rows = df[df['id'] == str(kid)]
                        return rows.iloc[0] if not rows.empty else None
                    
                    s = target
                    f = get_k(s['father_id'])
                    m = get_k(s['mother_id'])
                    ff = get_k(f['father_id']) if f is not None else None
                    fm = get_k(f['mother_id']) if f is not None else None
                    mf = get_k(m['father_id']) if m is not None else None
                    mm = get_k(m['mother_id']) if m is not None else None
                    
                    def pname(k): return k['name'] if k is not None else "不明"
                    def pcls(k): return get_pedigree_style(k)
                    
                    html = f"""
                    <div class="pedigree-table">
                        <div class="ped-cell ped-pos-self {pcls(s)}">{s['name']}</div>
                        <div class="ped-cell ped-pos-father {pcls(f)}">{pname(f)}</div>
                        <div class="ped-cell ped-pos-mother {pcls(m)}">{pname(m)}</div>
                        <div class="ped-cell ped-pos-ff {pcls(ff)}">{pname(ff)}</div>
                        <div class="ped-cell ped-pos-fm {pcls(fm)}">{pname(fm)}</div>
                        <div class="ped-cell ped-pos-mf {pcls(mf)}">{pname(mf)}</div>
                        <div class="ped-cell ped-pos-mm {pcls(mm)}">{pname(mm)}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                    
                elif st.session_state.modal_mode == "siblings":
                    st.subheader(f"🍒 {target['name']} のきょうだい")
                    siblings = df[df['id'] != k_id]
                    f_id = target['father_id']
                    m_id = target['mother_id']
                    
                    full = siblings[(siblings['father_id'] == f_id) & (siblings['mother_id'] == m_id) & (f_id != "") & (m_id != "")]
                    pat = siblings[(siblings['father_id'] == f_id) & (siblings['mother_id'] != m_id) & (f_id != "")]
                    mat = siblings[(siblings['mother_id'] == m_id) & (siblings['father_id'] != f_id) & (m_id != "")]
                    
                    def render_sib_list(title, sub_df):
                        if sub_df.empty: return
                        st.markdown(f"<div class='sibling-section-title'>{title}</div>", unsafe_allow_html=True)
                        for _, row in sub_df.sort_values("birthday").iterrows():
                             icon_color = '#4A90E2' if 'オス' in row['gender'] else '#E24A8D'
                             nm = row['name'] + (' 🌈' if check_is_dead(row) else '')
                             st.markdown(f"""
                             <div class="sibling-item">
                                <div><span style="color:{icon_color}">●</span> {nm}</div>
                                <div style="color:#e65100;">{row['birthday']}</div>
                             </div>""", unsafe_allow_html=True)

                    if f_id == "" and m_id == "":
                        st.write("両親の情報がないため表示できません")
                    else:
                        render_sib_list(f"💖 全きょうだい ({target['father']}&{target['mother']})", full)
                        render_sib_list(f"🧡 お母さん ({target['mother']})", mat)
                        render_sib_list(f"💙 お父さん ({target['father']})", pat)
            
            show_modal()

    # --- Router ---
    if st.session_state.view == 'home':
        
        # Birthday
        with st.container():
            st.markdown('<div class="birthday-section">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            c_month = datetime.datetime.now().month
            n_month = (datetime.datetime.now().replace(day=1) + datetime.timedelta(days=32)).month
            m_target = c_month if st.session_state.birthday_offset == 0 else n_month
            
            with col1:
                if st.button(f"今月 ({c_month}月)", key="btn_this_month", type="primary" if st.session_state.birthday_offset == 0 else "secondary"):
                    st.session_state.birthday_offset = 0
                    st.rerun()
            with col2:
                if st.button(f"来月 ({n_month}月)", key="btn_next_month", type="primary" if st.session_state.birthday_offset == 1 else "secondary"):
                    st.session_state.birthday_offset = 1
                    st.rerun()

            st.markdown(f'<div class="birthday-title">🎉 {m_target}月のお誕生日 🎉</div>', unsafe_allow_html=True)
            
            def is_bday_match(bday_str):
                if not bday_str or bday_str == '-': return False
                parts = bday_str.replace('/', '-').split('-')
                if len(parts) >= 2: return int(parts[1]) == m_target
                return False
                
            bd_koalas = df[df['birthday'].apply(is_bday_match)]
            dead_cnt = len([k for _, k in bd_koalas.iterrows() if check_is_dead(k)])
            
            if not st.session_state.show_dead_birthday:
                bd_koalas = bd_koalas[bd_koalas.apply(lambda x: not check_is_dead(x), axis=1)]
                
            if bd_koalas.empty:
                st.write("該当するコアラはいません")
            else:
                # Birthday Horizontal List
                cols = st.columns(min(len(bd_koalas), 4))
                for idx, (_, k) in enumerate(bd_koalas.iterrows()):
                    with cols[idx % 4]:
                        d_style = "deceased-style" if check_is_dead(k) else ""
                        st.markdown(f"""
                        <div class="koala-card {d_style}" style="padding:10px; font-size:0.9em; border-left:3px solid #ff9800;">
                            <div style="font-weight:bold;">{k['name']}</div>
                            <div style="font-size:0.8em;color:#666;">{k['zoo']}</div>
                            <div style="color:#e65100;">{k['birthday']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            if dead_cnt > 0:
                btn_txt = "✕ 元気な子のみ表示" if st.session_state.show_dead_birthday else f"🌈 虹のむこうの子（{dead_cnt}頭）も表示"
                if st.button(btn_txt, key="btn_toggle_dead"):
                    st.session_state.show_dead_birthday = not st.session_state.show_dead_birthday
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Search
        st.markdown("### 🔍 コアラを探す")
        search_name = st.text_input("なまえで検索", placeholder="例：こまち、きらら...", key="search_input")
        zoos = [""] + sorted(list(set(df['zoo'].dropna())))
        search_zoo = st.selectbox("動物園から探す", zoos, key="search_zoo")
        
        results = df.copy()
        is_search = False
        
        if search_name:
            is_search = True
            results = results[results['name'].str.contains(search_name, case=False, na=False) | results['memo'].str.contains(search_name, case=False, na=False)]
        elif search_zoo:
            is_search = True
            results = results[results['zoo'] == search_zoo]
        else:
            # Recommendations
            is_search = False
            
            # 1日2回（午前・午後）の更新に抑制するためのシード値を生成
            now = datetime.datetime.now()
            am_pm = "AM" if now.hour < 12 else "PM"
            time_seed = f"{now.strftime('%Y-%m-%d')}-{am_pm}"
            
            # シードを使ってサンプリングを固定
            living = df[df.apply(lambda x: not check_is_dead(x), axis=1)]
            dead = df[df.apply(lambda x: check_is_dead(x), axis=1)]
            
            # livingから2頭、deadから1頭を時間帯固定でサンプリング
            recs_living = living.sample(n=min(len(living), 2), random_state=hash(time_seed) % (2**32))
            recs_dead = dead.sample(n=min(len(dead), 1), random_state=hash(time_seed + "dead") % (2**32))
            
            recommended_ids = [str(r['id']) for r in recs_living.to_dict('records')] + \
                             [str(r['id']) for r in recs_dead.to_dict('records')]
            
            # 結果をフィルタリングして表示
            results = df[df['id'].isin(recommended_ids)]
            st.markdown("### 🌿 今日のおすすめコアラ")

        if is_search: st.markdown(f"**結果: {len(results)}件**")
        
        if not results.empty:
            results['is_dead'] = results.apply(check_is_dead, axis=1)
            results = results.sort_values('is_dead')
            
            COLS_PER_ROW = 3
            rows = [results.iloc[i:i+COLS_PER_ROW] for i in range(0, len(results), COLS_PER_ROW)]
            
            for r_idx, row_data in enumerate(rows):
                cols = st.columns(COLS_PER_ROW)
                for c_idx, (_, koala) in enumerate(row_data.iterrows()):
                    with cols[c_idx]:
                        # Section Key is important for uniqueness
                        render_koala_card(koala, section_key=f"list_{r_idx}_{c_idx}")

    elif st.session_state.view == 'family':
        target = df[df['id'] == st.session_state.selected_id]
        if target.empty: go_home()
        else:
            p = target.iloc[0]
            children = df[(df['father_id'] == p['id']) | (df['mother_id'] == p['id'])]
            
            st.markdown(f"### 🥰 {p['name']} の家系 (こども {len(children)}頭)")
            render_koala_card(p, section_key="hero", is_hero=True)
            
            st.divider()
            if children.empty:
                st.write("記録されている子供はいません")
            else:
                children = children.sort_values('birthday')
                COLS = 3
                child_rows = [children.iloc[i:i+COLS] for i in range(0, len(children), COLS)]
                for r_idx, row_data in enumerate(child_rows):
                    cols = st.columns(COLS)
                    for c_idx, (_, child) in enumerate(row_data.iterrows()):
                        with cols[c_idx]:
                            render_koala_card(child, section_key=f"child_{r_idx}_{c_idx}")

if __name__ == "__main__":
    main()