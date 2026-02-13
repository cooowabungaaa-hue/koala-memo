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
    @import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&family=Outfit:wght@400;700&display=swap');

    /* Global Page Styling */
    .stApp { 
        background-color: #f4f7f6; color: #333; 
        font-family: 'Zen Maru Gothic', 'Noto Sans JP', sans-serif; 
    }
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

    /* Typography Upgrades */
    h1, h2, h3, .main-header, .koala-name, .birthday-title-text, .search-label-text, button, .badge, .age, .koala-zoo, .subtitle-text {
        font-family: 'Zen Maru Gothic', 'Outfit', sans-serif !important;
    }

    /* Header Styling */
    .header-container { text-align: center; margin-bottom: 30px; }
    .main-header { 
        color: #2e7d32; font-size: 2.8em; font-weight: 700; cursor: pointer; 
        margin-bottom: 0px; letter-spacing: -0.02em;
    }
    .subtitle-text { color: #888; font-size: 0.9em; margin-bottom: 25px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; }

    /* Nav Buttons */
    div.stButton > button[key="global_home"], div.stButton > button[key="global_back"] {
        border-radius: 20px !important;
        background-color: #666 !important;
        color: white !important;
        border: none !important;
        font-size: 0.9em !important;
        height: 40px !important;
        width: auto !important;
        padding-left: 25px !important;
        padding-right: 25px !important;
        font-weight: 600 !important;
    }

    /* Birthday Section */
    .birthday-section-outer {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-radius: 16px; padding: 30px; margin-bottom: 30px; border: 2px solid #ffcc80;
        text-align: center; box-shadow: 0 4px 15px rgba(230, 81, 0, 0.05);
    }
    .birthday-title-text { color: #e65100; font-weight: 700; font-size: 1.4em; margin-bottom: 20px; }
    
    /* Search Section */
    .search-section-outer {
        background: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04); margin-bottom: 20px;
    }
    .search-label-text { font-size: 1em; font-weight: 700; color: #2e7d32; margin-bottom: 12px; display: block; }

    /* Koala Card Styling */
    .koala-card {
        background: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.05); border-left: 6px solid #2e7d32;
        margin-bottom: 15px; color: #333; position: relative;
    }
    .deceased-style { background-color: #f8f9f9; opacity: 0.95; border-color: #cbd5e0 !important; }
    .parent-hero { background-color: #f1f8f1; border: 2px solid #2e7d32; border-left: 8px solid #2e7d32; }

    .koala-name { font-size: 1.6em; font-weight: 700; color: #2e7d32; margin-bottom: 8px; display: block; border-bottom: 1px solid #edf2f7; padding-bottom: 5px; }
    .badge-container { margin-bottom: 12px; }
    .badge { font-size: 0.8em; padding: 4px 12px; border-radius: 20px; color: white; margin-right: 6px; font-weight: 600; }
    .male { background-color: #4A90E2; }
    .female { background-color: #E24A8D; }
    .age { background-color: #48bb78; }
    .deceased-badge { background-color: #a0aec0; }
    
    .koala-zoo {
        display: inline-block; background-color: #f0fff4; color: #2e7d32;
        padding: 5px 15px; border-radius: 8px; font-size: 0.9em; font-weight: 700;
        margin: 12px 0; border: 1px solid #c6f6d5;
    }
    .detail-grid { display: grid; grid-template-columns: 28px 1fr; gap: 10px; font-size: 1em; color: #4a5568; }
    
    /* Card Action Buttons */
    div.stButton > button[key*="ped_"], div.stButton > button[key*="sib_"], div.stButton > button[key*="fam_"] {
        background-color: #fffaf0 !important;
        color: #dd6b20 !important;
        border: 1px solid #fbd38d !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.85em !important;
        height: 42px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    div.stButton > button[key*="ped_"]:hover, div.stButton > button[key*="sib_"]:hover, div.stButton > button[key*="fam_"]:hover {
        background-color: #feebc8 !important;
        transform: translateY(-1px);
    }
    
    /* Birthday Filter Buttons */
    div.stButton > button[key*="btn_this_month"], div.stButton > button[key*="btn_next_month"] {
        border-radius: 25px !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        height: 44px !important;
    }

    .insta-btn-link {
        display: flex; width: 100%; height: 42px; justify-content: center; align-items: center;
        background-color: #fff5f7; color: #d53f8c !important; border: 1px solid #feb2b2;
        border-radius: 8px; font-weight: 700; font-size: 0.85em; text-decoration: none;
        transition: all 0.2s;
    }
    .insta-btn-link:hover { background-color: #fed7e2; transform: translateY(-1px); }

    /* My Page Specific Styling */
    .profile-box {
        background: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
        border-top: 5px solid #2e7d32; text-align: center;
    }
    .welcome-bar { 
        background-color: #e8f5e9; padding: 8px 16px; 
        border-radius: 50px; margin: 0 auto 25px auto; font-weight: 700; 
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid #c8e6c9; max-width: 650px;
    }
    .welcome-text-inline {
        color: #2e7d32; font-size: 0.9em; text-align: left; flex: 1;
        line-height: 1.3; padding-right: 10px;
    }
    .mypage-btn-inline {
        background-color: #2e7d32; color: white !important;
        padding: 5px 12px; border-radius: 30px; font-weight: 700;
        font-size: 0.8em; text-decoration: none; white-space: nowrap;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: all 0.2s;
    }
    .mypage-btn-inline:hover { background-color: #256b29; transform: translateY(-1px); }
    .fortune-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 20px; }
    .fortune-card {
        background: #fdfdfd; padding: 10px 5px; border-radius: 12px;
        border: 1px solid #edf2f7; text-align: center;
    }
    .fortune-label { font-size: 0.7em; color: #888; margin-bottom: 3px; }
    .fortune-value { font-size: 0.95em; font-weight: 700; color: #2e7d32; }

    /* Partner Card */
    .partner-card-outer {
        background: linear-gradient(135deg, #f0f7ff 0%, #e0f0ff 100%);
        border-radius: 16px; padding: 30px; border: 2px solid #add8e6;
        text-align: center; margin-top: 30px;
    }

    /* Transition Button (Compact Oval) */
    div.stButton > button[key="btn_mypage"] {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        height: 30px !important;
        width: auto !important;
        padding: 0 15px !important;
        margin: 0 !important;
        border: none !important;
    }

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
        df['mother_id'] = df['mother_id'].fillna("").astype(str).replace("nan", "").replace("0.0", "")
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame()

def check_is_dead(row):
    return "虹" in str(row['age']) or "没" in str(row['age']) or "🌈" in str(row['age']) or "虹" in str(row['memo'])

def get_gender_class(gender):
    if 'オス' in gender: return 'male'
    if 'メス' in gender: return 'female'
    return ''

def get_pedigree_style(koala):
    if koala is None: return ""
    if check_is_dead(koala): return "deceased-style"
    return get_gender_class(koala['gender'])

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

# --- Fortune Telling Logic ---
def get_astrology_sign(date):
    if not date: return "不明"
    m, d = date.month, date.day
    if (m == 1 and d >= 20) or (m == 2 and d <= 18): return "水瓶座"
    if (m == 2 and d >= 19) or (m == 3 and d <= 20): return "魚座"
    if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "牡羊座"
    if (m == 4 and d >= 20) or (m == 5 and d <= 20): return "牡牛座"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20): return "双子座"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22): return "蟹座"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22): return "獅子座"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22): return "乙女座"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22): return "天秤座"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21): return "蠍座"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21): return "射手座"
    return "山羊座"

def get_numerology(date):
    if not date: return 0
    s = f"{date.year}{date.month:02d}{date.day:02d}"
    while len(s) > 1:
        s = str(sum(int(d) for d in s))
    return int(s)

def get_nine_star_ki(year):
    stars = ["一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星", "六白金星", "七赤金星", "八白土星", "九紫火星"]
    s = sum(int(d) for d in str(year))
    while s > 9: s = sum(int(d) for d in str(s))
    idx = (12 - s) % 9
    return stars[idx - 1]

def get_animal_zodiac(year):
    zodiacs = ["子（ね）", "丑（うし）", "寅（とら）", "卯（う）", "辰（たつ）", "巳（み）", "午（うま）", "未（ひつじ）", "申（さる）", "酉（とり）", "戌（いぬ）", "亥（いのしし）"]
    return zodiacs[(year - 4) % 12]

def get_user_fortunes(birthday):
    if not birthday: return None
    return {
        "astrology": get_astrology_sign(birthday),
        "numerology": get_numerology(birthday),
        "nine_star": get_nine_star_ki(birthday.year),
        "animal": get_animal_zodiac(birthday.year)
    }

def calculate_compatibility_score(u, k_row):
    if not u: return 0
    score = 0
    try:
        kb_str = k_row['birthday'].replace('/', '-')
        parts = kb_str.split('-')
        if len(parts) < 3: return 0
        kb = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        kf = get_user_fortunes(kb)
        if u['astrology'] == kf['astrology']: score += 40
        if u['numerology'] == kf['numerology']: score += 30
        if u['nine_star'] == kf['nine_star']: score += 20
        if u['animal'] == kf['animal']: score += 10
    except: pass
    return score

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
    else:
        # mypage など他のビューに対応
        st.query_params.update({"view": view})
    
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
    # Using equal columns to ensure uniform button widths
    c = st.columns(4)
    with c[0]:
        if st.button("🧬家族", key=f"ped_{section_key}_{koala['id']}", use_container_width=True):
            st.session_state.modal_mode = "pedigree"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c[1]:
        if st.button("🍒兄弟", key=f"sib_{section_key}_{koala['id']}", use_container_width=True):
            st.session_state.modal_mode = "siblings"
            st.session_state.modal_target_id = koala['id']
            st.rerun()
    with c[2]:
        if st.button("👶子供", key=f"fam_{section_key}_{koala['id']}", use_container_width=True):
            navigate_to('family', koala['id'])
    with c[3]:
        st.markdown(f'<a href="{insta_url}" target="_blank" class="insta-btn-link">📸インスタ</a>', unsafe_allow_html=True)

# --- Main Page Execution ---
def main():
    st.markdown(STYLING, unsafe_allow_html=True)
    
    # 1. State Initialization
    if 'history' not in st.session_state: st.session_state.history = []
    if 'birthday_offset' not in st.session_state: st.session_state.birthday_offset = 0
    if 'show_dead_birthday' not in st.session_state: st.session_state.show_dead_birthday = False
    if 'modal_mode' not in st.session_state: st.session_state.modal_mode = None
    
    if 'user_nickname' not in st.session_state: st.session_state.user_nickname = ""
    if 'user_birthday' not in st.session_state: st.session_state.user_birthday = datetime.date(2000, 1, 1)

    # 2. Data Loading
    df = load_data()
    if df.empty:
        st.warning("現在データを読み込むことができません。しばらく時間をおいてから再度お試しください。")
        return

    # 3. Routing from URL (Single Source of Truth)
    view = st.query_params.get("view", "home")
    selected_id = st.query_params.get("id")

    # 4. Header & Navigation UI
    st.markdown("""
    <div class="header-container">
        <div class="main-header" onclick="window.location.href='/'">🐨 コアラメモ 🐨</div>
        <div class="subtitle-text">Japan Koala Database</div>
    </div>
    """, unsafe_allow_html=True)
    
    c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
    with c_nav2:
        if st.button("🏠ホームに戻る", use_container_width=True, key="global_home"):
            navigate_to('home')
        if view == 'family' and st.session_state.history:
            if st.button("⬅️ 前のページに戻る", use_container_width=True, key="global_back"):
                go_back()
                
    # 4.5 Welcome Bar (One-row)
    if view == 'home':
        display_name = f"{st.session_state.user_nickname}さん" if st.session_state.user_nickname else "ゲストさん"
        html = f"""
        <div class="welcome-bar">
            <div class="welcome-text-inline">🌟 ようこそ、{display_name}！今日もコアラに癒やされましょう 🐨</div>
            <a href="/?view=mypage" target="_self" class="mypage-btn-inline">📛 my page</a>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

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
    if view == 'mypage':
        st.markdown('### 👤 マイページ設定')
        
        with st.container():
            st.write('<div class="profile-box">', unsafe_allow_html=True)
            new_nick = st.text_input("ニックネーム", value=st.session_state.user_nickname, placeholder="例：コアラ大好きマン")
            new_bday = st.date_input("あなたの生年月日", value=st.session_state.user_birthday, min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
            
            if new_nick != st.session_state.user_nickname or new_bday != st.session_state.user_birthday:
                st.session_state.user_nickname = new_nick
                st.session_state.user_birthday = new_bday
                st.rerun()
            
            # --- Fortune Display ---
            u_fortune = get_user_fortunes(st.session_state.user_birthday)
            if u_fortune:
                st.markdown(f"""
                <div class="fortune-grid">
                    <div class="fortune-card">
                        <div class="fortune-label">✨ 西洋占星術</div>
                        <div class="fortune-value">{u_fortune['astrology']}</div>
                    </div>
                    <div class="fortune-card">
                        <div class="fortune-label">🔢 数秘術 (Life Path)</div>
                        <div class="fortune-value">{u_fortune['numerology']}</div>
                    </div>
                    <div class="fortune-card">
                        <div class="fortune-label">☯️ 九星気学</div>
                        <div class="fortune-value">{u_fortune['nine_star']}</div>
                    </div>
                    <div class="fortune-card">
                        <div class="fortune-label">🐾 動物占い (干支)</div>
                        <div class="fortune-value">{u_fortune['animal']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)

        st.divider()

        # --- Partner Koala Compatibility (運命のコアラを上位に表示) ---
        st.markdown("### 💖 あなたの運命のパートナーコアラ")
        if u_fortune:
            with st.spinner("相性診断中..."):
                df_scores = df.copy()
                df_scores['comp_score'] = df_scores.apply(lambda row: calculate_compatibility_score(u_fortune, row), axis=1)
                partners = df_scores[df_scores.apply(lambda x: not check_is_dead(x), axis=1)].sort_values('comp_score', ascending=False)
                
                if not partners.empty:
                    top_partner = partners.iloc[0]
                    st.write('<div class="partner-card-outer">', unsafe_allow_html=True)
                    st.markdown(f"#### 🎊 最高の相性: {top_partner['comp_score']}点！")
                    st.markdown(f"あなたと最も気が合うコアラは **{top_partner['name']}** です！")
                    render_koala_card(top_partner, section_key="partner_top", is_hero=True)
                    st.write('</div>', unsafe_allow_html=True)
                else:
                    st.write("パートナー候補が見つかりませんでした")

        st.divider()
        
        # --- Same Birth Month Koalas (同じ誕生月コアラを後に表示) ---
        m_user = st.session_state.user_birthday.month
        st.markdown(f"### 🎂 あなたと同じ {m_user}月生まれのコアラたち")
        
        def is_month_match(bday_str, target_m):
            try:
                parts = bday_str.replace('/', '-').split('-')
                return int(parts[1]) == target_m
            except: return False
            
        same_month_ks = df[df['birthday'].apply(lambda x: is_month_match(x, m_user))].copy()
        if same_month_ks.empty:
            st.write("該当するコアラはいません")
        else:
            # 存命コアラを優先的に上位表示
            same_month_ks['is_dead'] = same_month_ks.apply(check_is_dead, axis=1)
            same_month_ks = same_month_ks.sort_values('is_dead', ascending=True)
            
            cols = st.columns(3)
            for idx, (_, k) in enumerate(same_month_ks.head(6).iterrows()):
                with cols[idx % 3]:
                    render_koala_card(k, section_key=f"mypage_month_{idx}")

    elif view == 'family':
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
        # Birthday Section calculation
        c_month = datetime.datetime.now().month
        n_month = (datetime.datetime.now().replace(day=1) + datetime.timedelta(days=32)).month
        m_target = c_month if st.session_state.birthday_offset == 0 else n_month

        # --- Birthday Section ---
        st.write('<div class="birthday-section-outer">', unsafe_allow_html=True)
        st.markdown(f'<div class="birthday-title-text">🎉 {m_target}月のお誕生日 🎉</div>', unsafe_allow_html=True)
        
        b_col1, b_col2 = st.columns([1,1])
        with b_col1:
            if st.button("今月", key="btn_this_month", type="primary" if st.session_state.birthday_offset == 0 else "secondary", use_container_width=True):
                st.session_state.birthday_offset = 0
                st.rerun()
        with b_col2:
            if st.button("来月", key="btn_next_month", type="primary" if st.session_state.birthday_offset == 1 else "secondary", use_container_width=True):
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
            st.write('<div class="birthday-list-scroll">', unsafe_allow_html=True)
            cols_b = st.columns(min(len(bd_koalas), 4))
            for idx, (_, k) in enumerate(bd_koalas.iterrows()):
                with cols_b[idx % 4]:
                    d_style = "deceased-style" if check_is_dead(k) else ""
                    st.markdown(f"""
                    <div class="koala-card {d_style}" style="padding:10px; font-size:0.9em; border-left:3px solid #ff9800; border-radius:8px; margin-bottom:5px;">
                        <div style="font-weight:bold;">{k['name']}</div>
                        <div style="font-size:0.8em;color:#666;">{k['zoo']}</div>
                        <div style="color:#e65100;">{k['birthday']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)

        if dead_cnt > 0:
            btn_txt = "✕ 元気な子のみ表示" if st.session_state.show_dead_birthday else f"🌈 虹のむこうの子（{dead_cnt}頭）も表示"
            if st.button(btn_txt, key="btn_toggle_dead"):
                st.session_state.show_dead_birthday = not st.session_state.show_dead_birthday
                st.rerun()
        st.write('</div>', unsafe_allow_html=True)
            
        # Search Section
        # Search Section
        st.write('<div class="search-section-outer">', unsafe_allow_html=True)
        st.markdown('<label class="search-label-text">🔍 なまえで検索</label>', unsafe_allow_html=True)
        st.text_input("なまえで検索", placeholder="例：こまち、きらら...", key="search_input", label_visibility="collapsed")
        st.write('</div>', unsafe_allow_html=True)
        
        st.write('<div class="search-section-outer">', unsafe_allow_html=True)
        st.markdown('<label class="search-label-text">📍 動物園から探す</label>', unsafe_allow_html=True)
        zoos = [""] + sorted(list(set(df['zoo'].dropna())))
        st.selectbox("動物園から探す", zoos, key="search_zoo", label_visibility="collapsed")
        st.write('</div>', unsafe_allow_html=True)

        search_name = st.session_state.get("search_input")
        search_zoo = st.session_state.get("search_zoo")
        
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