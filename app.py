import streamlit as st
import pandas as pd
import datetime
import zlib

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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap');

    /* Global Body Background */
    .stApp { background-color: #f4f7f6; color: #333; font-family: "Helvetica Neue", Arial, sans-serif; }
    
    /* Center the main content (approx 1000px) */
    .block-container { max-width: 1000px !important; padding-top: 2rem !important; }

    /* Header & General */
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .main-header { 
        text-align: center; margin-bottom: 0px; color: #2e7d32; 
        font-size: 1.8em; font-weight: bold; cursor: pointer;
    }
    .subtitle { text-align: center; color: #666; font-size: 0.8em; margin-top: 5px; margin-bottom: 25px; }

    /* Top Page Nav Buttons */
    div.stButton > button {
        border-radius: 20px !important;
        background-color: #666 !important;
        color: white !important;
        border: none !important;
        padding: 8px 20px !important;
        font-size: 0.9em !important;
        font-weight: normal !important;
        transition: opacity 0.2s !important;
    }
    div.stButton > button:hover { opacity: 0.8; color: white !important; }

    /* Birthday Section (Orange Box) */
    .birthday-section-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-radius: 12px; padding: 15px; margin-bottom: 30px; border: 2px solid #ffcc80; 
        text-align: center;
    }
    .birthday-title-text { color: #e65100; font-weight: bold; font-size: 1.1em; margin-bottom: 12px; }
    
    /* Search Container */
    .search-group-box {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); margin-bottom: 12px;
    }
    .search-label-text { font-size: 0.85em; font-weight: bold; color: #2e7d32; margin-bottom: 8px; display: block; }

    /* Card Styling */
    .koala-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #2e7d32;
        margin-bottom: 0px; color: #333; transition: transform 0.2s;
    }
    .deceased-style { background-color: #f0f0f0; opacity: 0.9; border-color: #ccc !important; color: #666; }
    .parent-hero { background-color: #e8f5e9; border: 2px solid #2e7d32; border-left: 5px solid #2e7d32; }

    .koala-name { font-size: 1.4em; font-weight: bold; color: #333; display: inline-block; margin-right: 8px; }
    .badge { 
        font-size: 0.75em; padding: 3px 8px; border-radius: 12px; color: white; 
        display: inline-block; font-weight: normal; margin-right: 4px;
    }
    .male { background-color: #4A90E2; }
    .female { background-color: #E24A8D; }
    .other { background-color: #999; }
    .age { background-color: #2ecc71; }
    .deceased-badge { background-color: #999; }

    .koala-zoo {
        display: inline-block; background-color: #e8f5e9; color: #2e7d32;
        padding: 4px 10px; border-radius: 4px; font-size: 0.9em; font-weight: bold;
        margin-bottom: 12px; margin-top: 8px;
    }
    .deceased-style .koala-zoo { background-color: #eee; color: #666; }

    .detail-grid { display: grid; grid-template-columns: auto 1fr; gap: 5px 10px; font-size: 0.95em; color: #444; }
    .memo-box {
        font-size: 0.9em; margin-top: 12px; background: #f9f9f9; padding: 10px; 
        border-radius: 6px; color: #555; line-height: 1.5;
    }
    
    /* Pedigree Table */
    .pedigree-table {
        display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: repeat(4, 1fr);
        gap: 4px; margin-top: 15px; border: 2px solid #2e7d32; background-color: #2e7d32; width: 100%;
    }
    .ped-cell { background-color: #f9f9f9; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8px 2px; text-align: center; font-size: 0.8em; }
    .ped-pos-self { font-size: 1.1em; background-color: #e8f5e9; font-weight: bold; }
    .ped-male { border-left: 3px solid #4A90E2; }
    .ped-female { border-left: 3px solid #E24A8D; }

    /* Custom Buttons in Cards (Approximation) */
    .stButton > button[key^="ped_"], .stButton > button[key^="sib_"], .stButton > button[key^="fam_"] {
        background-color: #fff3e0 !important;
        color: #e65100 !important;
        border: 1px solid #ffcc80 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        font-size: 0.9em !important;
        height: 38px !important;
    }
    .stButton > button[key^="ped_"]:hover, .stButton > button[key^="sib_"]:hover, .stButton > button[key^="fam_"]:hover {
        background-color: #ffe0b2 !important;
    }

    /* Fixed Birthday Scrollbar */
    .birthday-list-scroll {
        display: flex; overflow-x: auto; gap: 15px; padding: 10px 0;
        scrollbar-width: thin; scrollbar-color: #ff9800 transparent;
    }
</style>
"""

# --- Helpers ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        df = df[df['name'].notna() & (df['name'] != "")]
        df['id'] = df['id'].astype(str)
        # データの並び順を固定することで、サンプリングを安定させる
        df = df.set_index('id', drop=False).sort_index()
        
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
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()

def check_is_dead(row):
    return (str(row.get('death', '')).strip() != "") or (row.get('age') == "没年齢不明")

def get_gender_class(gender):
    if "オス" in str(gender): return "male"
    if "メス" in str(gender): return "female"
    return "other"

def get_pedigree_style(k):
    if pd.isna(k) or k is None: return ""
    return "ped-male" if "オス" in str(k.get('gender', '')) else "ped-female"

@st.cache_data(ttl=3600*12)
def get_recommended_ids_cached(df_indexed, seed_str):
    if df_indexed.empty: return []
    seed = zlib.crc32(seed_str.encode())
    
    living = df_indexed[df_indexed.apply(lambda x: not check_is_dead(x), axis=1)]
    dead = df_indexed[df_indexed.apply(lambda x: check_is_dead(x), axis=1)]
    
    recs = []
    if not living.empty:
        recs.extend(living.sample(n=min(len(living), 2), random_state=seed % (2**32))['id'].tolist())
    if not dead.empty:
        recs.extend(dead.sample(n=min(len(dead), 1), random_state=zlib.crc32((seed_str + "dead").encode()) % (2**32))['id'].tolist())
    return recs

# --- Navigation Functions ---
def navigate_to(view, koala_id=None):
    if view == 'home':
        st.query_params.clear()
        st.session_state.history = []
    elif view == 'family':
        # 履歴の更新（重複や直近の戻りなどを考慮）
        current_id = st.query_params.get("id")
        if current_id and current_id != str(koala_id):
            if 'history' not in st.session_state: st.session_state.history = []
            if not st.session_state.history or st.session_state.history[-1] != current_id:
                st.session_state.history.append(current_id)
                if len(st.session_state.history) > 10: st.session_state.history.pop(0)
        
        st.query_params.update({"view": "family", "id": str(koala_id)})
    
    # モーダルなどの状態を完全にリセット
    st.session_state.modal_mode = None
    st.session_state.modal_target_id = None
    st.rerun()

def go_back():
    if 'history' in st.session_state and st.session_state.history:
        prev_id = st.session_state.history.pop()
        st.query_params.update({"view": "family", "id": prev_id})
    else:
        st.query_params.clear()
    
    st.session_state.modal_mode = None
    st.rerun()

# --- View Components ---
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
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("家族さん", key=f"ped_{section_key}_{koala['id']}", use_container_width=True):
            st.session_state.modal_mode = "pedigree"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c2:
        if st.button("きょうだい", key=f"sib_{section_key}_{koala['id']}", use_container_width=True):
            st.session_state.modal_mode = "siblings"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c3:
        if st.button("こども", key=f"fam_{section_key}_{koala['id']}", use_container_width=True):
            navigate_to('family', koala['id'])
    with c4:
        # Insta button with specific style
        st.markdown(f'<a href="{insta_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:38px; border:1px solid #f8bbd0; border-radius:6px; background-color:#fce4ec; color:#d81b60; font-weight:bold; font-size:0.9em; cursor:pointer; display:flex; align-items:center; justify-content:center;">Insta</button></a>', unsafe_allow_html=True)

# --- Main Page Execution ---
def main():
    st.markdown(STYLING, unsafe_allow_html=True)
    
    # 1. State Initialization
    if 'history' not in st.session_state: st.session_state.history = []
    if 'birthday_offset' not in st.session_state: st.session_state.birthday_offset = 0
    if 'show_dead_birthday' not in st.session_state: st.session_state.show_dead_birthday = False
    if 'modal_mode' not in st.session_state: st.session_state.modal_mode = None

    # 2. Data Loading
    df = load_data()
    if df.empty:
        st.warning("現在データを読み込むことができません。しばらく時間をおいてから再度お試しください。")
        return

    # 3. Routing from URL (Single Source of Truth)
    view = st.query_params.get("view", "home")
    selected_id = st.query_params.get("id")

    # 4. Header & Navigation UI
    st.markdown('<div class="main-header" onclick="window.location.href=\'/\'">🐨 コアラメモ 🐨</div>', unsafe_allow_html=True)
    
    col_n1, col_n2 = st.columns([1, 4])
    with col_n1:
        if st.button("🏠 ホーム", use_container_width=True, key="global_home"):
            navigate_to('home')
    with col_n2:
        if view == 'family' and st.session_state.history:
            if st.button("⬅️ 前のページに戻る", use_container_width=True, key="global_back"):
                go_back()

    # 5. Modals (Overlays)
    if st.session_state.get('modal_mode'):
        m_id = st.session_state.get('modal_target_id')
        if m_id in df.index:
            target = df.loc[m_id]
            
            @st.dialog("詳細情報", width="small")
            def show_modal_dialog(koala):
                mode = st.session_state.modal_mode
                if mode == "pedigree":
                    st.subheader(f"🧬 {koala['name']} の家族さん")
                    
                    def get_k(kid): 
                        return df.loc[kid] if kid in df.index else None
                    
                    s = koala
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
                    
                elif mode == "siblings":
                    st.subheader(f"🍒 {koala['name']} のきょうだい")
                    siblings = df[df.index != koala['id']]
                    f_id, m_id = koala['father_id'], koala['mother_id']
                    
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
                        render_sib_list(f"💖 全きょうだい ({koala['father']}&{koala['mother']})", full)
                        render_sib_list(f"🧡 お母さん ({koala['mother']})", mat)
                        render_sib_list(f"💙 お父さん ({koala['father']})", pat)
            
            show_modal_dialog(target)
            st.session_state.modal_mode = None # Reset after triggering

    # 6. Main Routing View
    if view == 'family':
        if selected_id not in df.index:
            st.error("お探しのコアラの情報が見つかりませんでした。ホームに戻ります。")
            navigate_to('home')
        else:
            p = df.loc[selected_id]
            children = df[(df['father_id'] == p['id']) | (df['mother_id'] == p['id'])]
            
            st.markdown(f"### 🥰 {p['name']} の詳細 (こども {len(children)}頭)")
            render_koala_card(p, section_key="hero", is_hero=True)
            
            st.divider()
            if children.empty:
                st.write("記録されている子供はいません")
            else:
                children_sorted = children.sort_values('birthday')
                COLS = 3
                child_rows = [children_sorted.iloc[i:i+COLS] for i in range(0, len(children_sorted), COLS)]
                for r_idx, row_data in enumerate(child_rows):
                    cols = st.columns(COLS)
                    for c_idx, (_, child) in enumerate(row_data.iterrows()):
                        with cols[c_idx]:
                            render_koala_card(child, section_key=f"child_{r_idx}_{c_idx}")

    else: # Default Home View
        # Birthday Section
        st.markdown('<div class="birthday-section-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="birthday-title-text">🎉 {m_target}月のお誕生日 🎉</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("今月", key="btn_this_month", type="primary" if st.session_state.birthday_offset == 0 else "secondary"):
                st.session_state.birthday_offset = 0
                st.rerun()
        with col2:
            if st.button("来月", key="btn_next_month", type="primary" if st.session_state.birthday_offset == 1 else "secondary"):
                st.session_state.birthday_offset = 1
                st.rerun()

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
            
        # Search Section
        st.markdown('<div class="search-group-box">', unsafe_allow_html=True)
        st.markdown('<label class="search-label-text">🔍 なまえで検索</label>', unsafe_allow_html=True)
        search_name = st.text_input("なまえで検索", placeholder="例：こまち、きらら...", key="search_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="search-group-box">', unsafe_allow_html=True)
        st.markdown('<label class="search-label-text">📍 動物園から探す</label>', unsafe_allow_html=True)
        zoos = [""] + sorted(list(set(df['zoo'].dropna())))
        search_zoo = st.selectbox("動物園から探す", zoos, key="search_zoo", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        is_search = bool(search_name or search_zoo)
        if is_search:
            results = df.copy()
            if search_name:
                results = results[results['name'].str.contains(search_name, case=False, na=False) | results['memo'].str.contains(search_name, case=False, na=False)]
            if search_zoo:
                results = results[results['zoo'] == search_zoo]
            st.markdown(f"**結果: {len(results)}件**")
        else:
            # Recommendations
            now = datetime.datetime.now()
            am_pm = "AM" if now.hour < 12 else "PM"
            time_seed_str = f"{now.strftime('%Y-%m-%d')}-{am_pm}"
            recs_ids = get_recommended_ids_cached(df, time_seed_str)
            # 常に存在するIDのみを抽出（念のため）
            valid_recs = [rid for rid in recs_ids if rid in df.index]
            results = df.loc[valid_recs]
            st.markdown("### 🌿 今日のおすすめコアラ")

        if not results.empty:
            sorted_results = results.copy()
            sorted_results['is_dead'] = sorted_results.apply(check_is_dead, axis=1)
            sorted_results = sorted_results.sort_values(['is_dead', 'name'])
            
            COLS_PER_ROW = 3
            res_rows = [sorted_results.iloc[i:i+COLS_PER_ROW] for i in range(0, len(sorted_results), COLS_PER_ROW)]
            for r_idx, row_data in enumerate(res_rows):
                cols = st.columns(COLS_PER_ROW)
                for c_idx, (_, koala) in enumerate(row_data.iterrows()):
                    with cols[c_idx]:
                        render_koala_card(koala, section_key=f"list_{r_idx}_{c_idx}")

if __name__ == "__main__":
    main()