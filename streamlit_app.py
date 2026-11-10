import streamlit as st
from supabase import create_client
import time
import uuid
import json
import datetime
from hijri_converter import Gregorian
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(
    page_title="منصة زياد الذكية | ملف الإنجاز المهني",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. منظومة المظاهر (Themes) المتعددة
# ==========================================
THEMES = {
    "emerald": {
        "name": "🟢 الأخضر الوزاري الفاخر",
        "primary": "#0f5243",
        "primary_light": "#146c59",
        "primary_dark": "#09352b",
        "bg": "#f4f6f5",
        "accent": "#d97706",
        "tint": "#e6f2ef"
    },
    "royal": {
        "name": "🔵 الأزرق الملكي الاحترافي",
        "primary": "#1e3a8a",
        "primary_light": "#2563eb",
        "primary_dark": "#172554",
        "bg": "#f0f4f8",
        "accent": "#0284c7",
        "tint": "#dbeafe"
    },
    "bronze": {
        "name": "🟤 الذهبي الكلاسيكي الفاخر",
        "primary": "#78350f",
        "primary_light": "#92400e",
        "primary_dark": "#451a03",
        "bg": "#faf6f0",
        "accent": "#b45309",
        "tint": "#fef3c7"
    },
    "slate": {
        "name": "⚫ الرمادي العصري الرسمي",
        "primary": "#1e293b",
        "primary_light": "#334155",
        "primary_dark": "#0f172a",
        "bg": "#f1f5f9",
        "accent": "#475569",
        "tint": "#e2e8f0"
    }
}

# ==========================================
# 3. البنود الفرعية الافتراضية للمعايير الـ 11
# ==========================================
DEFAULT_SUB_ITEMS = {
    1: [
        "تقرير الحضور والانتظار من النظام",
        "سجل تنفيذ المناوبة والإشراف اليومي",
        "تكليفات اللجان مع محاضر الإنجاز",
        "مبادرة انضباط أو قيم وطنية نفذتها مع وصف أثرها"
    ],
    2: [
        "شهادة دورة مع ملخص ما طبقته منها في الفصل",
        "تقرير زيارة تبادلية مع زميل ونموذج الملاحظة",
        "تأمل ذاتي مكتوب بعد درس",
        "محضر مجتمع تعلم مهني شاركت فيه أو قدمته",
        "خطة إرشاد معلم جديد وسجل لقاءاتها",
        "ورشة قدمتها لمعلمي المدرسة أو المكتب"
    ],
    3: [
        "سجل تواصل مجمّع: التاريخ والموضوع والإجراء (بلا لقطات محادثات)",
        "رسائل دورية عن تقدم الطلاب",
        "محضر لقاء ولي أمر وخطة دعم مشتركة",
        "نشرة إرشادية لدعم التعلم في البيت"
    ],
    4: [
        "تحضير درس يوضح الاستراتيجية المستخدمة",
        "أعمال طلاب ناتجة عن الاستراتيجية (بلا أسماء ولا وجوه)",
        "مصفوفة الاستراتيجيات المستخدمة خلال الفصل",
        "درس تطبيقي قدمته لزملائك عن استراتيجية"
    ],
    5: [
        "خطة علاجية مع نتائج قبلية وبعدية مجمعة",
        "نماذج تغذية راجعة مكتوبة على أعمال الطلاب",
        "برنامج إثرائي للمتفوقين",
        "رسم بياني لتطور نسب الإتقان"
    ],
    6: [
        "خطة توزيع المنهج الفصلية",
        "تحضير دروس بأنشطة متمايزة",
        "محضر تخطيط مشترك مع معلمي المادة",
        "تعديل على الخطة بعد تحليل النتائج مع بيان السبب"
    ],
    7: [
        "تقرير نشاط منصة مدرستي (واجبات واختبارات ودروس)",
        "وسيلة تعليمية محسوسة أو رقمية من إعدادك",
        "درس تفاعلي باختبار قصير أو سبورة تفاعلية",
        "ورشة لزملائك عن أداة رقمية"
    ],
    8: [
        "صور الفصل والجداريات دون طلاب",
        "لوحة تعزيز أو نظام نقاط",
        "ركن قراءة أو ركن تعلم",
        "ميثاق صف أعده الطلاب (بلا أسماء)"
    ],
    9: [
        "قواعد الصف وإجراءاته المعلنة",
        "سجل متابعة السلوك بأرقام مجمعة",
        "توزيع الأدوار والمجموعات",
        "خطة تعديل سلوك فردية (بلا اسم)"
    ],
    10: [
        "اختبار تشخيصي وتحليله لكل مهارة",
        "تصنيف الطلاب: متقن وقريب ومتعثر",
        "تحليل نتائج نافس أو اختبار الفترة",
        "قرار تدريسي اتخذته بناءً على التحليل",
        "تقرير تشخيصي شاركته مع زملائك"
    ],
    11: [
        "اختبار قصير مع مهمة أدائية وسلم تقدير",
        "قائمة رصد أو بطاقة ملاحظة",
        "اختبار إلكتروني مع تقريره",
        "نماذج تقويم ذاتي وتقويم أقران"
    ]
}

# ==========================================
# 4. الاتصال بقاعدة البيانات والتخزين المؤقت السريع (Caching)
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_visitor' not in st.session_state:
    st.session_state.is_visitor = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'view_standard_id' not in st.session_state:
    st.session_state.view_standard_id = 0
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'

def clear_app_cache():
    st.cache_data.clear()

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id is not None:
        st.session_state.view_standard_id = std_id
    st.rerun()

@st.cache_data(ttl=180)
def get_user_profile():
    default_profile = {
        "full_name": "زياد المعمري",
        "specialization": "لغة إنجليزية / تربية خاصة",
        "school_name": "ابتدائية عبادة بن قيس الأنصاري",
        "education_stage": "ابتدائي / متوسط",
        "city": "المدينة المنورة",
        "principal_name": "عبدالمجيد الحربي",
        "theme": "emerald",
        "visitor_code": "1448",
        "allow_visitor": True
    }
    try:
        res = supabase.table("user_profile").select("*").eq("id", 1).execute()
        if res.data:
            return {**default_profile, **res.data[0]}
    except Exception:
        pass
    return default_profile

@st.cache_data(ttl=180)
def fetch_all_years():
    res = supabase.table("academic_years").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []

@st.cache_data(ttl=300)
def fetch_standards_and_subs():
    stds = supabase.table("standards").select("*").order("id").execute().data
    try:
        subs = supabase.table("sub_items").select("*").execute().data
    except Exception:
        subs = []
    return stds, subs

@st.cache_data(ttl=120)
def fetch_year_evidences(year_id):
    if not year_id:
        return []
    res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", year_id).order("created_at", desc=True).execute()
    return res.data if res.data else []

@st.cache_data(ttl=1800)
def get_signed_urls_batch(paths_tuple):
    """توليد كافة روابط المرفقات دفعة واحدة لتسريع التصفح ومنع أي ثقل"""
    if not paths_tuple:
        return {}
    url_map = {}
    storage_paths = [p for p in paths_tuple if not p.startswith("http")]
    for p in paths_tuple:
        if p.startswith("http"):
            url_map[p] = p
    if storage_paths:
        try:
            res = supabase.storage.from_("private-achievements").create_signed_urls(storage_paths, 3600)
            for item in res:
                if item.get("path") and item.get("signedURL"):
                    url_map[item["path"]] = item["signedURL"]
        except Exception:
            for sp in storage_paths:
                try:
                    single = supabase.storage.from_("private-achievements").create_signed_url(sp, 3600)
                    url_map[sp] = single.get("signedURL", "")
                except Exception:
                    pass
    return url_map

user_info = get_user_profile()
active_theme_key = user_info.get("theme", "emerald")
if active_theme_key not in THEMES:
    active_theme_key = "emerald"
th = THEMES[active_theme_key]

ZIYAD_LOGO_SVG = '<svg width="46" height="46" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="16" fill="white" fill-opacity="0.15"/><rect x="2" y="2" width="60" height="60" rx="14" stroke="white" stroke-opacity="0.35" stroke-width="2"/><path d="M32 14L12 24L32 34L52 24L32 14Z" fill="#FBBF24"/><path d="M20 29V41C20 44.5 25.5 48 32 48C38.5 48 44 44.5 44 41V29L32 35L20 29Z" fill="white"/><path d="M48 26V40" stroke="#FBBF24" stroke-width="3" stroke-linecap="round"/></svg>'

# ==========================================
# 5. التصميم الشامل (إصلاح الوضع الليلي + منع تكدس الأزرار في الجوال)
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;600;700;800&family=Readex+Pro:wght@400;500;600;700&display=swap');

:root, html, body, .stApp {{
    color-scheme: light !important;
    direction: rtl; 
    text-align: right; 
    font-family: 'Readex Pro', 'Cairo', sans-serif;
    background-color: {th['bg']} !important;
    color: #1e293b !important;
}}

header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
.stSidebar {{display: none !important;}}
.block-container {{ padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 760px !important; }}

/* فرض وضوح جميع العناوين والنصوص في الوضع الليلي للجوال */
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {{
    font-family: 'Readex Pro', 'Cairo', sans-serif;
    color: #1e293b !important;
}}

/* الحفاظ على خط أيقونات النظام لمنع ظهور كلمة visibility */
span[data-testid="stIconMaterial"], .material-icons, [class*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    direction: ltr !important;
}}

/* إصلاح حقول الإدخال والقوائم المنسدلة في الوضع الليلي */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {{
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}}
input, textarea, [data-baseweb="select"] span, [data-baseweb="select"] div {{
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    background-color: transparent !important;
}}
input::placeholder, textarea::placeholder {{
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}}
[data-testid="stForm"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}}

/* إصلاح القوائم المنسدلة (Expanders) والتبويبات (Tabs) في الوضع الليلي */
[data-testid="stExpander"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span {{
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-weight: 700 !important;
}}
button[data-baseweb="tab"] {{
    background-color: transparent !important;
    color: #475569 !important;
    font-weight: 700 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {th['primary']} !important;
    border-bottom-color: {th['primary']} !important;
}}

/* إصلاح شكل الأزرار لمنع ظهورها باللون الأسود في الوضع الليلي */
div[data-testid="stButton"] button {{
    background-color: #ffffff !important;
    color: {th['primary']} !important;
    border: 1.5px solid {th['primary']} !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.45rem 0.9rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
}}
div[data-testid="stButton"] button p {{
    color: {th['primary']} !important;
    font-weight: 700 !important;
}}
div[data-testid="stButton"] button:hover {{
    background-color: {th['tint']} !important;
}}
div[data-testid="stButton"] button[kind="primary"], div[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, {th['primary']}, {th['primary_light']}) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(15, 82, 67, 0.2) !important;
}}
div[data-testid="stButton"] button[kind="primary"] p, div[data-testid="stFormSubmitButton"] button p {{
    color: #ffffff !important;
}}

/* شريط التنقل الأفقي وشريط الفلاتر (أفقي دائماً ولا ينقلب عمودياً في الجوال) */
div[data-testid="stRadio"] > div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 6px !important;
    background: #ffffff !important;
    padding: 6px !important;
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
    justify-content: space-between !important;
    scrollbar-width: none;
}}
div[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar {{ display: none; }}
div[data-testid="stRadio"] label {{
    flex: 1 1 auto !important;
    margin: 0 !important;
    padding: 8px 10px !important;
    border-radius: 12px !important;
    background: transparent !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    white-space: nowrap !important;
    transition: all 0.2s ease !important;
}}
/* إخفاء دائرة الراديو التقليدية لتحويلها إلى تبويبات كبسولات عصرية */
div[data-testid="stRadio"] label > div:first-child {{
    display: none !important;
}}
div[data-testid="stRadio"] label p {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #475569 !important;
    margin: 0 !important;
}}
div[data-testid="stRadio"] label:has(input:checked) {{
    background: {th['primary']} !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12) !important;
}}
div[data-testid="stRadio"] label:has(input:checked) p {{
    color: #ffffff !important;
}}

/* الهيدر والبنر المدمج الاحترافي */
.hero-wrapper {{
    background: linear-gradient(135deg, {th['primary_dark']} 0%, {th['primary']} 55%, {th['primary_light']} 100%);
    color: white !important;
    padding: 20px 22px;
    border-radius: 22px;
    margin-bottom: 12px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(255,255,255,0.12);
}}
.hero-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    padding-bottom: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
    gap: 8px;
}}
.brand-box {{ display: flex; align-items: center; gap: 10px; }}
.brand-title {{ font-size: 16px; font-weight: 700; color: #fbbf24 !important; margin: 0; }}
.brand-sub {{ font-size: 11px; color: rgba(255,255,255,0.88) !important; margin: 2px 0 0 0; }}
.date-pill {{
    background: rgba(255,255,255,0.14);
    padding: 5px 12px;
    border-radius: 99px;
    font-size: 11.5px;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2);
}}
.hero-body {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 12px;
}}
.welcome-line {{ font-size: 13.5px; color: #fde68a !important; font-weight: 600; margin-bottom: 3px; }}
.teacher-name {{ font-size: 23px; font-weight: 800; color: #ffffff !important; margin: 0 0 8px 0; }}
.meta-badges {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.meta-pill {{
    background: rgba(0,0,0,0.25);
    color: #ffffff !important;
    padding: 4px 10px;
    border-radius: 9px;
    font-size: 11.5px;
    font-weight: 500;
}}
.year-badge {{
    background: #fbbf24;
    color: #1e293b !important;
    padding: 7px 14px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 4px 10px rgba(251, 191, 36, 0.3);
}}

/* بطاقات الإحصائيات السريعة */
.kpi-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 14px; margin-top: 8px;
}}
.kpi-card {{
    background: #ffffff; border-radius: 15px; padding: 12px 6px; text-align: center;
    border: 1px solid #e2e8f0; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}}
.kpi-val {{ font-size: 20px; font-weight: 700; color: {th['primary']} !important; text-align: center; }}
.kpi-lbl {{ font-size: 11px; color: #475569 !important; margin-top: 2px; font-weight: 600; text-align: center; }}

/* شريط الإنجاز */
.progress-card {{
    background: #ffffff; padding: 14px 18px; border-radius: 16px; 
    margin-bottom: 14px; border: 1px solid #e2e8f0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}}
.progress-bar-bg {{
    background: #e2e8f0; height: 10px; border-radius: 6px; width: 100%; overflow: hidden; margin-top: 8px;
}}
.progress-bar-fill {{
    background: linear-gradient(90deg, {th['primary']}, {th['primary_light']});
    height: 100%; border-radius: 6px;
}}

/* بطاقة المعيار */
.std-card {{
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 14px 16px; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}}
.std-num {{
    width: 40px; height: 40px; border-radius: 12px;
    background: {th['tint']}; color: {th['primary']} !important;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 17px; margin-left: 12px; flex-shrink: 0;
}}
.std-num-empty {{ background: #fee2e2; color: #dc2626 !important; }}
.std-title {{ font-size: 15px; font-weight: 700; color: #0f172a !important; margin-bottom: 4px; }}
.weight-badge {{
    background: #f1f5f9; color: #475569 !important; font-size: 11px; padding: 2px 9px;
    border-radius: 8px; display: inline-block; font-weight: 600;
}}
.dots-row {{ display: flex; gap: 4px; margin-bottom: 4px; justify-content: flex-end; }}
.dot {{ width: 13px; height: 6px; border-radius: 3px; }}
.dot-on {{ background: {th['primary']}; }}
.dot-off {{ background: #e2e8f0; }}

/* المرفقات والصور المصغرة والروابط الخارجية */
.thumbs-container {{
    display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0 6px 0; align-items: center;
}}
.thumb-link {{
    position: relative; display: inline-block; width: 96px; height: 96px;
    border-radius: 12px; overflow: hidden; border: 2px solid {th['tint']};
    box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: transform 0.2s ease;
}}
.thumb-link:hover {{ transform: scale(1.04); border-color: {th['primary']}; }}
.thumb-link img {{ width: 100%; height: 100%; object-fit: cover; }}
.thumb-overlay {{
    position: absolute; bottom: 0; left: 0; right: 0;
    background: rgba(0,0,0,0.65); color: #ffffff !important; font-size: 10px;
    text-align: center; padding: 2px 0;
}}
.pdf-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 46px; padding: 0 14px; border-radius: 10px;
    background: #f8fafc; border: 1.5px dashed {th['primary']};
    color: {th['primary']} !important; font-weight: 700; font-size: 12.5px; text-decoration: none;
}}
.ext-link-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 46px; padding: 0 16px; border-radius: 10px;
    background: #eff6ff; border: 1.5px solid #2563eb;
    color: #1d4ed8 !important; font-weight: 700; font-size: 12.5px; text-decoration: none;
}}

/* بطاقة الشاهد */
.ev-box {{
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 15px; margin-bottom: 10px; border-right: 4px solid {th['primary']};
}}
.idea-card {{
    background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 14px;
    border-radius: 11px; margin-bottom: 6px; font-size: 13px; color: #1e293b !important;
    display: flex; justify-content: space-between; align-items: center;
}}
.visitor-banner {{
    background: #fef3c7; color: #92400e !important; border: 1px solid #f59e0b;
    padding: 10px 16px; border-radius: 12px; margin-bottom: 12px;
    font-weight: 700; font-size: 13.5px; text-align: center;
}}

/* الفوتر الثابت */
.ziyad-footer {{
    margin-top: 38px;
    padding: 18px 14px;
    background: #ffffff;
    border-top: 3px solid {th['primary']};
    border-radius: 16px 16px 8px 8px;
    text-align: center;
    border: 1px solid #e2e8f0;
}}
.footer-brand {{ font-size: 14px; font-weight: 700; color: {th['primary']} !important; margin-bottom: 3px; text-align: center; }}
.footer-rights {{ font-size: 11.5px; color: #64748b !important; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# التحقق التلقائي من رابط الزائر (?visitor=CODE)
query_params = st.query_params
if "visitor" in query_params and st.session_state.user is None:
    entered_code = str(query_params["visitor"]).strip()
    saved_code = str(user_info.get("visitor_code", "1448")).strip()
    if user_info.get("allow_visitor", True) and entered_code == saved_code:
        st.session_state.is_visitor = True

# ==========================================
# 6. دوال التاريخ والترحيب والفوتر وعرض المرفقات
# ==========================================
def get_greeting_and_dates():
    tz = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz)
    today = now.date()
    greeting = "صباح الخير والتميز" if now.hour < 12 else "مساء الخير والعطاء"
    
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[today.weekday()]
    g_date = f"{today.day} {months_ar[today.month - 1]} {today.year}م"
    
    h_obj = Gregorian(today.year, today.month, today.day).to_hijri()
    h_months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    h_date = f"{h_obj.day} {h_months[h_obj.month - 1]} {h_obj.year}هـ"
    
    return greeting, f"{day_name} • {h_date} • {g_date}"

def render_attachments_html(files, signed_urls_map):
    if not files:
        return ""
    thumbs_html = '<div class="thumbs-container">'
    for i, f_rec in enumerate(files):
        f_url = f_rec.get('file_url', '')
        f_type = f_rec.get('file_type', '')
        if f_type == 'external/link' or f_url.startswith('http'):
            thumbs_html += f'<a href="{f_url}" target="_blank" class="ext-link-badge">🔗 فتح الرابط المرفق</a>'
        else:
            sec_url = signed_urls_map.get(f_url, '')
            if not sec_url:
                continue
            if f_type.startswith('image/'):
                thumbs_html += (
                    f'<a href="{sec_url}" target="_blank" class="thumb-link" title="اضغط للتكبير بالحجم الأصلي">'
                    f'<img src="{sec_url}" alt="شاهد"><div class="thumb-overlay">🔍 تكبير</div></a>'
                )
            else:
                thumbs_html += f'<a href="{sec_url}" target="_blank" class="pdf-badge">📄 ملف PDF ({i+1})</a>'
    thumbs_html += '</div>'
    return thumbs_html

def render_footer():
    year_now = datetime.date.today().year
    footer_html = (
        f'<div class="ziyad-footer">'
        f'<div class="footer-brand">🎓 منصة زياد الذكية | نظام ملف الإنجاز المهني الإلكتروني</div>'
        f'<div class="footer-rights">جميع الحقوق محفوظة © {year_now}م - تصميم وتطوير: أ. {user_info["full_name"]}</div>'
        f'</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)

# ==========================================
# 7. صفحة تسجيل الدخول (معلم + زائر)
# ==========================================
def login_page():
    login_hero = (
        f'<div class="hero-wrapper" style="text-align:center;">'
        f'<div style="display:flex; justify-content:center; margin-bottom:10px;">{ZIYAD_LOGO_SVG}</div>'
        f'<div style="font-size:15px; color:#fbbf24 !important; font-weight:700; text-align:center;">منصة زياد الذكية</div>'
        f'<div style="font-size:23px; font-weight:800; margin:6px 0; color:white !important; text-align:center;">ملف الإنجاز المهني الإلكتروني</div>'
        f'<div style="font-size:13px; opacity:0.95; color:white !important; text-align:center;">أ. {user_info["full_name"]} • {user_info["school_name"]}</div>'
        f'</div>'
    )
    st.markdown(login_hero, unsafe_allow_html=True)
    
    tab_teacher, tab_visitor = st.tabs(["🔒 دخول المعلم (تحكم كامل)", "👁️ دخول زائر (مشاهدة فقط)"])
    
    with tab_teacher:
        with st.form("login_form"):
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("تسجيل الدخول للنظام", type="primary", use_container_width=True)
            if submit:
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = response.user
                        st.session_state.is_visitor = False
                        st.success("تم تسجيل الدخول بنجاح!")
                        time.sleep(0.3)
                        st.rerun()
                    except Exception:
                        st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                else:
                    st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")

    with tab_visitor:
        st.info("بوابة مخصصة لمدير المدرسة والمشرف التربوي للاطلاع على ملف الإنجاز بواسطة رمز المشاهدة الممنوح من المعلم.")
        with st.form("visitor_form"):
            v_code = st.text_input("أدخل رمز المشاهدة للزائر:", type="password")
            v_submit = st.form_submit_button("👁️ استعراض ملف الإنجاز", type="primary", use_container_width=True)
            if v_submit:
                saved_code = str(user_info.get("visitor_code", "1448")).strip()
                if not user_info.get("allow_visitor", True):
                    st.error("المعلم قام بإيقاف خاصية دخول الزوار حالياً.")
                elif v_code.strip() == saved_code:
                    st.session_state.is_visitor = True
                    st.rerun()
                else:
                    st.error("رمز المشاهدة غير صحيح.")

    render_footer()

# ==========================================
# 8. التطبيق الرئيسي
# ==========================================
def main_app():
    is_visitor = st.session_state.is_visitor

    # 1. جلب البيانات المخزنة مؤقتاً بسرعة فائقة
    all_years = fetch_all_years()
    active_years = [y for y in all_years if y.get("is_active")]
    active_year = active_years[0] if active_years else (all_years[0] if all_years else {"id": None, "year_name": "1448"})

    stds, all_subs = fetch_standards_and_subs()
    evidences = fetch_year_evidences(active_year.get('id'))

    # تحضير جميع روابط الصور والملفات دفعة واحدة (سرعة فائقة)
    all_file_paths = tuple(
        f['file_url'] for ev in evidences for f in ev.get('evidence_files', []) if f.get('file_url')
    )
    signed_urls_map = get_signed_urls_batch(all_file_paths)

    # 2. الهيدر والبنر الاحترافي في قمة الصفحة دائماً
    greeting, today_str = get_greeting_and_dates()
    hero_html = (
        f'<div class="hero-wrapper">'
        f'<div class="hero-top">'
        f'<div class="brand-box">{ZIYAD_LOGO_SVG}'
        f'<div><div class="brand-title">منصة زياد الذكية</div>'
        f'<div class="brand-sub">نظام إدارة وتوثيق شواهد الأداء الوظيفي</div></div></div>'
        f'<div class="date-pill">🗓️ {today_str}</div>'
        f'</div>'
        f'<div class="hero-body">'
        f'<div>'
        f'<div class="welcome-line">✨ {greeting}</div>'
        f'<div class="teacher-name">أ. {user_info["full_name"]}</div>'
        f'<div class="meta-badges">'
        f'<span class="meta-pill">🏫 {user_info["school_name"]}</span>'
        f'<span class="meta-pill">📚 {user_info["specialization"]}</span>'
        f'<span class="meta-pill">👔 مدير المدرسة: {user_info["principal_name"]}</span>'
        f'</div>'
        f'</div>'
        f'<div class="year-badge">📁 ملف إنجاز عام {active_year["year_name"]}هـ</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # تنبيه وضع الزائر
    if is_visitor:
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            st.markdown('<div class="visitor-banner">👁️ تتصفح الملف بوضع الزائر (مشاهدة فقط)</div>', unsafe_allow_html=True)
        with col_v2:
            if st.button("🚪 خروج", use_container_width=True):
                st.session_state.is_visitor = False
                st.query_params.clear()
                st.rerun()

    # 3. شريط التنقل الأفقي الموحد (لا ينقلب عمودياً في الجوال أبداً)
    if is_visitor:
        nav_map = {
            'home': "🏠 الرئيسية",
            'standard_view': "📋 البنود والشواهد",
            'reports': "📄 التقرير"
        }
    else:
        nav_map = {
            'home': "🏠 الرئيسية",
            'standard_view': "📋 البنود",
            'archive': "📅 الأرشيف",
            'reports': "📄 التقرير",
            'settings': "⚙️ حسابي"
        }

    nav_keys = list(nav_map.keys())
    curr_page = st.session_state.current_page if st.session_state.current_page in nav_keys else 'home'
    selected_nav = st.radio(
        "القائمة الرئيسية",
        options=nav_keys,
        format_func=lambda k: nav_map[k],
        index=nav_keys.index(curr_page),
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_nav != st.session_state.current_page:
        st.session_state.current_page = selected_nav
        st.rerun()

    # حساب إحصائيات البنود
    total_stds = len(stds)
    total_ev_count = len(evidences)
    stds_with_ev = 0
    stds_reached_target = 0
    empty_stds = 0

    ev_by_std = {}
    for s in stds:
        c = len([e for e in evidences if e['standard_id'] == s['id']])
        ev_by_std[s['id']] = c
        if c > 0:
            stds_with_ev += 1
        else:
            empty_stds += 1
        if c >= s.get('target_evidences', 3):
            stds_reached_target += 1

    less_than_3 = sum(1 for s in stds if ev_by_std[s['id']] < s.get('target_evidences', 3))
    pct = int((stds_with_ev / total_stds) * 100) if total_stds else 0

    # ----------------------------------------
    # 🏠 1. الصفحة الرئيسية
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        kpi_html = (
            f'<div class="kpi-grid">'
            f'<div class="kpi-card"><div class="kpi-val">{total_ev_count}</div><div class="kpi-lbl">إجمالي الشواهد</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_with_ev}/{total_stds}</div><div class="kpi-lbl">البنود المغطاة</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_reached_target}</div><div class="kpi-lbl">حققت المستهدف</div></div>'
            f'<div class="kpi-card"><div class="kpi-val" style="color:#dc2626 !important;">{empty_stds}</div><div class="kpi-lbl">بنود فارغة</div></div>'
            f'</div>'
            f'<div class="progress-card">'
            f'<div style="display:flex; justify-content:space-between; font-weight:700; font-size:13.5px; color:#1e293b;">'
            f'<span style="color:#1e293b !important;">نسبة تغطية معايير الأداء الوظيفي ({active_year["year_name"]}هـ)</span>'
            f'<span style="color:{th["primary"]} !important;">{pct}%</span>'
            f'</div>'
            f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;"></div></div>'
            f'</div>'
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

        # شريط الفرز الأفقي الأنيق (Pills) في سطر واحد
        filter_map = {
            'all': f"الكل • {total_stds}",
            'empty': f"فارغة • {empty_stds}",
            'less3': f"أقل من 3 • {less_than_3}"
        }
        f_keys = list(filter_map.keys())
        sel_filter = st.radio(
            "فرز المعايير",
            options=f_keys,
            format_func=lambda x: filter_map[x],
            index=f_keys.index(st.session_state.filter_mode),
            horizontal=True,
            label_visibility="collapsed"
        )
        if sel_filter != st.session_state.filter_mode:
            st.session_state.filter_mode = sel_filter
            st.rerun()

        # عرض بطاقات البنود الـ 11
        for std in stds:
            s_id = std['id']
            count = ev_by_std[s_id]
            target = std.get('target_evidences', 3)

            if st.session_state.filter_mode == 'empty' and count > 0:
                continue
            if st.session_state.filter_mode == 'less3' and count >= target:
                continue

            dots_html = "".join([
                f'<div class="dot {"dot-on" if i < count else "dot-off"}"></div>'
                for i in range(target)
            ])
            
            if count == 0:
                status_txt = '<span style="color:#dc2626 !important; font-size:12px; font-weight:600;">لا شواهد بعد</span>'
                num_cls = "std-num std-num-empty"
            elif count >= target:
                status_txt = f'<span style="color:{th["primary"]} !important; font-size:12px; font-weight:700;">مكتمل ({count} شواهد)</span>'
                num_cls = "std-num"
            else:
                status_txt = f'<span style="color:{th["accent"]} !important; font-size:12px; font-weight:600;">{count} شاهد • بقي {target - count}</span>'
                num_cls = "std-num"

            card_html = (
                f'<div class="std-card">'
                f'<div style="display:flex; align-items:center;">'
                f'<div class="{num_cls}">{s_id}</div>'
                f'<div><div class="std-title">{s_id}. {std["title"]}</div>'
                f'<span class="weight-badge">الوزن النسبي: {std["weight"]}%</span></div>'
                f'</div>'
                f'<div style="text-align:left;"><div class="dots-row">{dots_html}</div>{status_txt}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            btn_label = f"➕ إضافة أو استعراض شواهد البند {s_id}" if not is_visitor else f"👁️ استعراض شواهد البند {s_id}"
            if st.button(btn_label, key=f"open_std_{s_id}", use_container_width=True):
                navigate_to('standard_view', s_id)

    # ----------------------------------------
    # 📋 2. صفحة البنود والشواهد (مع دعم الرابط الاختياري https://)
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        st.markdown("#### 📋 استعراض وإدارة بنود الأداء والشواهد")
        
        options_map = {0: "🔍 عرض ملخص جميع البنود والشواهد المرفوعة"}
        for s in stds:
            options_map[s['id']] = f"البند {s['id']}: {s['title']} ({ev_by_std[s['id']]} شواهد)"
            
        current_std_id = st.session_state.view_standard_id
        if current_std_id not in options_map:
            current_std_id = 0
            
        selected_option = st.selectbox(
            "اختر البند للتنقل السريع أو إضافة شاهد:",
            options=list(options_map.keys()),
            format_func=lambda x: options_map[x],
            index=list(options_map.keys()).index(current_std_id)
        )
        
        if selected_option != st.session_state.view_standard_id:
            st.session_state.view_standard_id = selected_option
            st.rerun()

        if selected_option == 0:
            for s in stds:
                s_evs = [e for e in evidences if e['standard_id'] == s['id']]
                with st.expander(f"{'✅' if len(s_evs)>0 else '⚪'} البند {s['id']}: {s['title']} — ({len(s_evs)} شواهد)", expanded=(len(s_evs) > 0)):
                    if not s_evs:
                        st.caption("لا توجد شواهد مرفوعة في هذا البند حتى الآن.")
                    else:
                        for ev in s_evs:
                            files = ev.get("evidence_files", [])
                            exec_date = ev.get('execution_date') or ev['created_at'][:10]
                            thumbs_html = render_attachments_html(files, signed_urls_map)
                            ev_card = (
                                f'<div class="ev-box">'
                                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">'
                                f'<span style="font-weight:700; color:{th["primary"]} !important;">📄 {ev["title"]}</span>'
                                f'<span style="font-size:12px; color:#64748b !important;">📅 {exec_date}</span>'
                                f'</div>'
                                f'<div style="font-size:13.5px; color:#334155 !important;">{ev.get("description") or ""}</div>'
                                f'{thumbs_html}</div>'
                            )
                            st.markdown(ev_card, unsafe_allow_html=True)
                    if st.button(f"📂 فتح صفحة البند {s['id']} للإدارة والإضافة", key=f"jump_std_{s['id']}", use_container_width=True):
                        navigate_to('standard_view', s['id'])

        else:
            std_id = selected_option
            std_data = [s for s in stds if s['id'] == std_id][0]
            std_evidences = [e for e in evidences if e['standard_id'] == std_id]

            st.markdown(f"##### 📂 الشواهد المرفوعة في البند {std_id}: {std_data['title']} ({len(std_evidences)})")
            if not std_evidences:
                st.info("لا توجد شواهد مرفوعة في هذا البند حتى الآن. يمكنك إضافة شاهد جديد من النموذج بالأسفل.")
            else:
                for ev in std_evidences:
                    files = ev.get("evidence_files", [])
                    exec_date = ev.get('execution_date') or ev['created_at'][:10]
                    thumbs_html = render_attachments_html(files, signed_urls_map)

                    # استخراج الرابط الخارجي الحالي إن وجد لتسهيل تعديله
                    existing_links = [f['file_url'] for f in files if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http')]
                    current_ext_link = existing_links[0] if existing_links else ""

                    ev_detail_html = (
                        f'<div class="ev-box">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">'
                        f'<span style="font-weight:700; font-size:15.5px; color:{th["primary"]} !important;">📄 {ev["title"]}</span>'
                        f'<span style="background:{th["tint"]}; color:{th["primary_dark"]} !important; padding:4px 12px; border-radius:10px; font-size:12px; font-weight:700;">'
                        f'📅 تاريخ التنفيذ: {exec_date}</span></div>'
                        f'<div style="font-size:13.5px; color:#334155 !important; line-height:1.6; margin-bottom:6px;">{ev.get("description") or ""}</div>'
                        f'{thumbs_html}</div>'
                    )
                    st.markdown(ev_detail_html, unsafe_allow_html=True)

                    if not is_visitor:
                        ed_col, del_col = st.columns(2)
                        with ed_col:
                            with st.expander("✏️ تعديل الشاهد"):
                                with st.form(f"edit_form_{ev['id']}"):
                                    new_t = st.text_input("عنوان الشاهد:", value=ev['title'])
                                    try:
                                        default_d = datetime.date.fromisoformat(str(exec_date)[:10])
                                    except Exception:
                                        default_d = datetime.date.today()
                                    new_exec_date = st.date_input("📅 تاريخ التنفيذ:", value=default_d)
                                    new_d = st.text_area("وصف الشاهد:", value=ev.get('description', ''))
                                    new_files = st.file_uploader("استبدال المرفقات (صور أو PDF - اختياري):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key=f"up_{ev['id']}")
                                    new_ext_link = st.text_input("🔗 أو رابط (يوتيوب، مدرستي...):", value=current_ext_link, placeholder="https://")
                                    
                                    if st.form_submit_button("حفظ التعديل 💾", type="primary", use_container_width=True):
                                        update_payload = {"title": new_t, "description": new_d, "execution_date": str(new_exec_date)}
                                        try:
                                            supabase.table("evidences").update(update_payload).eq("id", ev['id']).execute()
                                        except Exception:
                                            supabase.table("evidences").update({"title": new_t, "description": new_d}).eq("id", ev['id']).execute()
                                            
                                        if new_files:
                                            old_storage_paths = [f['file_url'] for f in files if not f.get('file_url', '').startswith('http')]
                                            if old_storage_paths:
                                                supabase.storage.from_("private-achievements").remove(old_storage_paths)
                                            supabase.table("evidence_files").delete().eq("evidence_id", ev['id']).execute()
                                            for nf in new_files:
                                                ext = nf.name.split('.')[-1]
                                                path = f"{ev['id']}/{uuid.uuid4()}.{ext}"
                                                supabase.storage.from_("private-achievements").upload(path=path, file=nf.getvalue(), file_options={"content-type": nf.type})
                                                supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": path, "file_type": nf.type}).execute()
                                            if new_ext_link.strip():
                                                supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": new_ext_link.strip(), "file_type": "external/link"}).execute()
                                        elif new_ext_link.strip() != current_ext_link:
                                            # تحديث الرابط الخارجي فقط
                                            for f in files:
                                                if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http'):
                                                    supabase.table("evidence_files").delete().eq("id", f['id']).execute()
                                            if new_ext_link.strip():
                                                supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": new_ext_link.strip(), "file_type": "external/link"}).execute()

                                        clear_app_cache()
                                        st.success("تم التحديث بنجاح!")
                                        time.sleep(0.3)
                                        st.rerun()
                        with del_col:
                            with st.expander("🗑️ حذف الشاهد"):
                                if st.button("تأكيد الحذف النهائي", key=f"confirm_del_{ev['id']}", type="primary", use_container_width=True):
                                    old_storage_paths = [f['file_url'] for f in files if not f.get('file_url', '').startswith('http')]
                                    if old_storage_paths:
                                        supabase.storage.from_("private-achievements").remove(old_storage_paths)
                                    supabase.table("evidences").delete().eq("id", ev['id']).execute()
                                    clear_app_cache()
                                    st.success("تم الحذف!")
                                    time.sleep(0.3)
                                    st.rerun()

            # عرض الأفكار والشواهد المستهدفة
            db_subs = [item['title'] for item in all_subs if item.get('standard_id') == std_id]
            sub_options = db_subs if db_subs else DEFAULT_SUB_ITEMS.get(std_id, [])

            with st.expander("💡 استعراض أمثلة الشواهد المستهدفة لهذا البند", expanded=False):
                for idea in sub_options:
                    st.markdown(f'<div class="idea-card"><span>💡 {idea}</span><span style="color:{th["primary"]} !important; font-weight:bold;">✔</span></div>', unsafe_allow_html=True)

            # نموذج إضافة شاهد جديد (مع حقل الرابط الاختياري https://)
            if not is_visitor:
                st.markdown("##### ➕ إضافة شاهد جديد لهذا البند")
                with st.form(f"add_ev_std_{std_id}", clear_on_submit=True):
                    chosen_idea = st.selectbox("اختر البند الفرعي:", sub_options + ["أخرى (كتابة عنوان مخصص)"])
                    custom_title = st.text_input("عنوان مخصص للشاهد (اختياري):")
                    exec_date_input = st.date_input("📅 تاريخ التنفيذ (حسب توزيع المنهج):", value=datetime.date.today())
                    desc = st.text_area("وصف الشاهد (الهدف، التنفيذ، الأثر):")
                    uploaded_files = st.file_uploader("📎 المرفقات (صور أو ملف PDF):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
                    ext_link_input = st.text_input("🔗 أو رابط (يوتيوب، مدرستي، درايف... - اختياري):", placeholder="https://")
                    
                    if st.form_submit_button("حفظ الشاهد ورفع المرفقات 💾", type="primary", use_container_width=True):
                        final_title = custom_title.strip() if (chosen_idea == "أخرى (كتابة عنوان مخصص)" or custom_title.strip()) else chosen_idea
                        has_attachment = bool(uploaded_files) or bool(ext_link_input.strip())
                        
                        if final_title and has_attachment and active_year.get('id'):
                            with st.spinner("جاري حفظ الشاهد والمرفقات..."):
                                insert_payload = {
                                    "standard_id": std_id,
                                    "year_id": active_year['id'],
                                    "title": final_title,
                                    "description": desc,
                                    "execution_date": str(exec_date_input)
                                }
                                try:
                                    ev_data = supabase.table("evidences").insert(insert_payload).execute()
                                except Exception:
                                    insert_payload.pop("execution_date", None)
                                    ev_data = supabase.table("evidences").insert(insert_payload).execute()
                                    
                                new_id = ev_data.data[0]['id']
                                if uploaded_files:
                                    for up_file in uploaded_files:
                                        ext = up_file.name.split('.')[-1]
                                        path = f"{new_id}/{uuid.uuid4()}.{ext}"
                                        supabase.storage.from_("private-achievements").upload(
                                            path=path, file=up_file.getvalue(), file_options={"content-type": up_file.type}
                                        )
                                        supabase.table("evidence_files").insert({
                                            "evidence_id": new_id, "file_url": path, "file_type": up_file.type
                                        }).execute()
                                if ext_link_input.strip():
                                    supabase.table("evidence_files").insert({
                                        "evidence_id": new_id,
                                        "file_url": ext_link_input.strip(),
                                        "file_type": "external/link"
                                    }).execute()
                                    
                                clear_app_cache()
                                st.success("تم حفظ الشاهد بنجاح!")
                                time.sleep(0.4)
                                st.rerun()
                        else:
                            st.warning("يرجى اختيار العنوان وإرفاق ملف واحد على الأقل أو وضع رابط خارجي.")

    # ----------------------------------------
    # 📅 3. صفحة أرشفة ملفات الإنجاز وإدارة الأعوام الدراسية
    # ----------------------------------------
    elif st.session_state.current_page == 'archive' and not is_visitor:
        st.markdown("#### 📅 أرشفة ملفات الإنجاز وإدارة الأعوام الدراسية")
        st.write("في نهاية كل عام دراسي، يمكنك أرشفة ملف الإنجاز الحالي وبدء ملف إنجاز جديد للعام القادم دون فقدان أي شواهد سابقة.")

        with st.form("archive_and_new_year_form", clear_on_submit=True):
            new_year_name = st.text_input("🆕 اسم العام الدراسي الجديد (مثال: 1449 أو 1449-1450):")
            submit_new_year = st.form_submit_button("📦 أرشفة العام الحالي وبدء ملف الإنجاز الجديد", type="primary", use_container_width=True)
            if submit_new_year:
                if new_year_name.strip():
                    for y in all_years:
                        supabase.table("academic_years").update({"is_active": False}).eq("id", y['id']).execute()
                    supabase.table("academic_years").insert({
                        "year_name": new_year_name.strip(),
                        "is_active": True
                    }).execute()
                    clear_app_cache()
                    st.success(f"تمت أرشفة العام السابق، وفتح ملف إنجاز جديد لعام ({new_year_name.strip()})!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("يرجى كتابة اسم العام الدراسي الجديد.")

        st.markdown("##### 🗂️ سجل ملفات الإنجاز المحفوظة")
        for y in all_years:
            y_ev_res = supabase.table("evidences").select("id", count="exact").eq("year_id", y['id']).execute()
            y_count = y_ev_res.count if y_ev_res.count is not None else len(y_ev_res.data)
            is_act = y.get("is_active", False)
            
            badge_html = '<span style="background:#10b981; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">🟢 الملف النشط</span>' if is_act else '<span style="background:#64748b; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">📦 مؤرشف</span>'
            
            arch_card = (
                f'<div class="std-card">'
                f'<div><div class="std-title">📁 ملف إنجاز العام الدراسي: {y["year_name"]}هـ</div>'
                f'<div style="font-size:12.5px; color:#64748b !important;">عدد الشواهد الموثقة: <strong>{y_count} شاهد</strong></div></div>'
                f'<div>{badge_html}</div>'
                f'</div>'
            )
            st.markdown(arch_card, unsafe_allow_html=True)
            
            if not is_act:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    if st.button(f"🔄 تفعيل واستعراض ملف عام {y['year_name']}هـ", key=f"act_{y['id']}", use_container_width=True):
                        for item_y in all_years:
                            supabase.table("academic_years").update({"is_active": False}).eq("id", item_y['id']).execute()
                        supabase.table("academic_years").update({"is_active": True}).eq("id", y['id']).execute()
                        clear_app_cache()
                        st.rerun()
                with col_b:
                    if y_count == 0:
                        if st.button("🗑️ حذف", key=f"del_y_{y['id']}", use_container_width=True):
                            supabase.table("academic_years").delete().eq("id", y['id']).execute()
                            clear_app_cache()
                            st.rerun()

    # ----------------------------------------
    # 📄 4. صفحة التقارير والطباعة (3 تصاميم احترافية بحجم A4)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.markdown("#### 📄 تصدير وطباعة ملف الإنجاز (A4 PDF)")
        
        report_style = st.selectbox(
            "🎨 اختر تصميم التقرير قبل الطباعة:",
            [
                "1. التصميم الرسمي الوزاري (إطار كلاسيكي وجداول رسمية)",
                "2. التصميم العصري الحديث (بطاقات ناعمة وألوان المظهر الحالي)",
                "3. التصميم التنفيذي المختصر (تخطيط مكثف بحدود هندسية أنيقة)"
            ]
        )

        if st.button("تجهيز التقرير بالتصميم المختار للطباعة 🖨️", type="primary", use_container_width=True):
            with st.spinner("جاري تجهيز صفحات A4..."):
                stds_map = {s['id']: s for s in stds}
                all_evidences = sorted(evidences, key=lambda x: x.get('standard_id', 0))
                
                total_evidences = len(all_evidences)
                active_stds = [s for s in stds if len([e for e in all_evidences if e['standard_id'] == s['id']]) > 0]
                covered_stds = len(active_stds)

                if report_style.startswith("1."):
                    rep_color = "#146c59"
                    rep_sub = "#0f5243"
                    cover_border = "6px double #146c59"
                    box_radius = "4px"
                elif report_style.startswith("2."):
                    rep_color = th['primary']
                    rep_sub = th['primary_dark']
                    cover_border = f"3px solid {th['primary']}"
                    box_radius = "14px"
                else:
                    rep_color = "#1e293b"
                    rep_sub = "#334155"
                    cover_border = "2px solid #1e293b"
                    box_radius = "0px"

                html_content = f"""
                <!DOCTYPE html>
                <html dir="rtl" lang="ar">
                <head>
                    <meta charset="UTF-8">
                    <title>ملف الإنجاز المهني - {user_info['full_name']}</title>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Readex+Pro:wght@400;500;600;700&display=swap');
                        body {{ font-family: 'Readex Pro', sans-serif; background-color: #cbd5e1; margin: 0; padding: 20px; }}
                        .page {{ background-color: white; width: 210mm; height: 296mm; padding: 10mm 15mm; margin: 0 auto 20mm auto; box-shadow: 0 10px 20px rgba(0,0,0,0.15); box-sizing: border-box; page-break-after: always; page-break-inside: avoid; display: flex; flex-direction: column; overflow: hidden; }}
                        .cover-page {{ border: {cover_border}; border-radius: {box_radius}; padding: 35px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; box-sizing: border-box; }}
                        .cover-title {{ color: {rep_color}; font-size: 36px; font-weight: 700; margin-bottom: 10px; }}
                        .cover-subtitle {{ font-size: 19px; margin-bottom: 35px; font-weight: 600; color: #475569; }}
                        .info-table {{ width: 88%; border-collapse: collapse; margin: 0 auto; font-size: 16px; }}
                        .info-table th, .info-table td {{ border: 1px solid #cbd5e1; padding: 12px; text-align: center; }}
                        .info-table th {{ background-color: #f8fafc; width: 32%; font-weight: 700; color: {rep_color}; }}
                        .header-container {{ display: flex; justify-content: space-between; border-bottom: 2px solid {rep_color}; padding-bottom: 8px; margin-bottom: 14px; font-size: 12.5px; font-weight: 700; flex-shrink: 0; }}
                        .header-right {{ color: {rep_color}; }}
                        .header-left {{ text-align: left; }}
                        .index-title {{ color: {rep_color}; font-size: 22px; font-weight: 700; margin-bottom: 16px; }}
                        .index-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
                        .index-table th {{ background-color: #f1f5f9; color: {rep_color}; padding: 10px; text-align: center; border-bottom: 2px solid {rep_color}; }}
                        .index-table td {{ padding: 10px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
                        .content-wrapper {{ flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }}
                        .std-header {{ background-color: {rep_color}; color: white; padding: 10px 15px; font-size: 15px; font-weight: 700; border-radius: {box_radius} {box_radius} 0 0; flex-shrink: 0; }}
                        .ev-header {{ background-color: {rep_sub}; color: white; padding: 8px 15px; font-size: 13.5px; margin-bottom: 12px; border-radius: 0 0 {box_radius} {box_radius}; flex-shrink: 0; }}
                        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; flex-shrink: 0; }}
                        .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px; text-align: center; border-radius: {box_radius}; }}
                        .meta-title {{ font-size: 11.5px; color: #64748b; font-weight: 600; }}
                        .meta-value {{ font-size: 13.5px; font-weight: 700; color: #0f172a; }}
                        .desc-section {{ margin-bottom: 12px; line-height: 1.6; font-size: 13.5px; padding: 10px; background: #fafafa; border-right: 4px solid {rep_color}; border-radius: {box_radius}; flex-shrink: 0; }}
                        .images-grid {{ flex-grow: 1; display: flex; justify-content: center; align-items: center; gap: 12px; min-height: 0; padding: 5px 0; overflow: hidden; }}
                        .images-grid img {{ max-width: 100%; max-height: 100%; object-fit: contain; border: 1px solid #cbd5e1; border-radius: {box_radius}; }}
                        .pdf-notice {{ background: #f1f5f9; padding: 8px; text-align: center; border-radius: {box_radius}; font-size: 12.5px; color: #334155; margin-bottom: 8px; border: 1px dashed #94a3b8; flex-shrink: 0; }}
                        .signatures {{ display: flex; justify-content: space-between; margin-top: auto; border-top: 2px solid #e2e8f0; padding-top: 10px; text-align: center; flex-shrink: 0; }}
                        .sig-box {{ width: 42%; }}
                        .print-footer {{ text-align: center; font-size: 10px; color: #64748b; margin-top: 8px; padding-top: 4px; border-top: 1px dashed #e2e8f0; flex-shrink: 0; }}
                        @media print {{
                            body {{ background-color: white; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                            .page {{ width: 210mm; height: 296mm; margin: 0; padding: 10mm 15mm; box-shadow: none; border: none; }}
                            @page {{ size: A4 portrait; margin: 0; }}
                        }}
                    </style>
                </head>
                <body>
                """
                
                html_content += f"""
                <div class="page">
                    <div class="cover-page">
                        <div style="font-size:15px; font-weight:700; color:{rep_color}; margin-bottom:8px;">المملكة العربية السعودية • وزارة التعليم</div>
                        <div style="font-size:13px; color:#b45309; font-weight:700; margin-bottom:12px;">🎓 منصة زياد الذكية لتوثيق الأداء المهني</div>
                        <div class="cover-title">ملف الإنجاز المهني</div>
                        <div class="cover-subtitle">توثيق شواهد الأداء الوظيفي</div>
                        <table class="info-table">
                            <tr><th>اسم المعلم</th><td>{user_info['full_name']}</td></tr>
                            <tr><th>التخصص</th><td>{user_info['specialization']}</td></tr>
                            <tr><th>المدرسة</th><td>{user_info['school_name']}</td></tr>
                            <tr><th>المرحلة الدراسية</th><td>{user_info['education_stage']}</td></tr>
                            <tr><th>المدينة</th><td>{user_info['city']}</td></tr>
                            <tr><th>مدير المدرسة</th><td>{user_info['principal_name']}</td></tr>
                            <tr><th>العام الدراسي</th><td>{active_year['year_name']}هـ</td></tr>
                            <tr><th>إجمالي الشواهد الموثقة</th><td>{total_evidences} شاهد ({covered_stds} من {len(stds)} معايير)</td></tr>
                        </table>
                        <div style="margin-top:35px; font-size:11px; color:#64748b;">صدر إلكترونياً عبر منصة زياد الذكية — جميع الحقوق محفوظة © أ. {user_info['full_name']}</div>
                    </div>
                </div>
                """
                
                shared_header = f"""
                <div class="header-container">
                    <div class="header-right">
                        منصة زياد الذكية | أ. {user_info['full_name']}<br>
                        <span style="font-size:11px; font-weight:normal; color:#666;">شواهد الأداء الوظيفي - العام الدراسي {active_year['year_name']}هـ</span>
                    </div>
                    <div class="header-left">
                        المملكة العربية السعودية<br>
                        <span style="font-size:11px; font-weight:normal; color:#666;">وزارة التعليم - {user_info['school_name']}</span>
                    </div>
                </div>
                """
                
                html_content += f"""
                <div class="page">
                    {shared_header}
                    <div class="index-title">فهرس معايير الأداء المنجزة</div>
                    <table class="index-table">
                        <tr><th>م</th><th>المعيار</th><th>الوزن النسبي</th><th>الشواهد الموثقة</th><th>المستهدف</th></tr>
                """
                for std in stds:
                    count = ev_by_std[std['id']]
                    if count == 0:
                        continue
                    target = std.get('target_evidences', 3)
                    html_content += f"<tr><td>{std['id']}</td><td style='text-align:right; font-weight:bold;'>{std['title']}</td><td>{std['weight']}%</td><td style='color:{rep_color}; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
                html_content += f"""
                    </table>
                    <div class="print-footer" style="margin-top:auto;">منصة زياد الذكية | جميع الحقوق محفوظة © أ. {user_info['full_name']}</div>
                </div>
                """
                
                for ev in all_evidences:
                    std = stds_map.get(ev['standard_id'], {"title": "", "weight": 10})
                    exec_date = ev.get('execution_date') or ev['created_at'][:10]
                    files = ev.get('evidence_files', [])
                    img_html = ""
                    pdf_count = 0
                    ext_links = []
                    for f in files:
                        f_url = f.get('file_url', '')
                        f_type = f.get('file_type', '')
                        if f_type == 'external/link' or f_url.startswith('http'):
                            ext_links.append(f_url)
                        elif f_type.startswith('image/'):
                            sec_u = signed_urls_map.get(f_url, '')
                            if sec_u:
                                img_html += f"<img src='{sec_u}'>"
                        elif f_type == 'application/pdf':
                            pdf_count += 1
                            
                    pdf_notice = f"<div class='pdf-notice'>📌 مرفق مستند PDF رسمي عدد ({pdf_count}) محفوظ في النظام الإلكتروني.</div>" if pdf_count > 0 else ""
                    link_notice = f"<div class='pdf-notice'>🔗 رابط إلكتروني مرفق: {ext_links[0]}</div>" if ext_links else ""
                    images_section = f"<div class='images-grid'>{img_html}</div>" if img_html else ""
                    
                    html_content += f"""
                    <div class="page">
                        {shared_header}
                        <div class="content-wrapper">
                            <div class="std-header">المعيار {ev['standard_id']}: {std['title']} (الوزن {std['weight']}%)</div>
                            <div class="ev-header">الشاهد: {ev['title']}</div>
                            <div class="meta-grid">
                                <div class="meta-box"><div class="meta-title">تاريخ التنفيذ الفعلي</div><div class="meta-value">{exec_date}</div></div>
                                <div class="meta-box"><div class="meta-title">حالة التوثيق</div><div class="meta-value">شاهد معتمد وموثق</div></div>
                            </div>
                            <div class="desc-section"><strong>وصف الشاهد والأثر:</strong><br>{ev.get('description') or 'تم تنفيذ الشاهد وتوثيقه وفق خطة توزيع المنهج.'}</div>
                            {pdf_notice}
                            {link_notice}
                            {images_section}
                        </div>
                        <div class="signatures">
                            <div class="sig-box">
                                <div style="color:#666; font-size:12px; margin-bottom:16px;">المعلم:</div>
                                <div style="font-weight:bold;">{user_info['full_name']}</div>
                            </div>
                            <div class="sig-box">
                                <div style="color:#666; font-size:12px; margin-bottom:16px;">مدير المدرسة:</div>
                                <div style="font-weight:bold;">{user_info['principal_name']}</div>
                            </div>
                        </div>
                        <div class="print-footer">منصة زياد الذكية | ملف الإنجاز المهني — أ. {user_info['full_name']}</div>
                    </div>
                    """
                
                html_content += "</body></html>"
                safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                
                components.html(f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <button onclick="openPrintWindow()" style="width: 100%; padding: 15px; background-color: {rep_color}; color: white; border: none; border-radius: 12px; font-size: 17px; font-weight: bold; cursor: pointer; font-family: 'Readex Pro', sans-serif;">
                            🖨️ فتح التقرير للطباعة بحجم A4
                        </button>
                    </div>
                    <script>
                        function openPrintWindow() {{
                            var win = window.open('', '_blank');
                            win.document.write(`{safe_html}`);
                            win.document.close();
                            setTimeout(function() {{ win.print(); }}, 1500);
                        }}
                    </script>
                """, height=85)

    # ----------------------------------------
    # ⚙️ 5. صفحة حسابي (البيانات + المظاهر + مشاركة الزائر + النسخ الاحتياطي)
    # ----------------------------------------
    elif st.session_state.current_page == 'settings' and not is_visitor:
        st.markdown("#### ⚙️ إعدادات الحساب والمظهر والمشاركة")
        t1, t2, t3, t4 = st.tabs(["👤 البيانات والمظهر", "🔗 مشاركة للزوار", "💾 النسخ الاحتياطي", "🚪 الخروج"])
        
        with t1:
            with st.form("profile_form"):
                st.markdown("##### 🎨 مظهر التطبيق")
                theme_keys = list(THEMES.keys())
                theme_labels = [THEMES[k]["name"] for k in theme_keys]
                current_idx = theme_keys.index(active_theme_key) if active_theme_key in theme_keys else 0
                selected_theme_label = st.selectbox("اختر المظهر اللوني للتطبيق:", theme_labels, index=current_idx)
                chosen_theme_key = theme_keys[theme_labels.index(selected_theme_label)]

                st.markdown("##### 📝 البيانات الأساسية")
                c1, c2 = st.columns(2)
                with c1:
                    n_name = st.text_input("اسم المعلم:", value=user_info['full_name'])
                    n_spec = st.text_input("التخصص:", value=user_info['specialization'])
                    n_city = st.text_input("المدينة:", value=user_info['city'])
                with c2:
                    n_school = st.text_input("اسم المدرسة:", value=user_info['school_name'])
                    n_stage = st.text_input("المرحلة الدراسية:", value=user_info['education_stage'])
                    n_prin = st.text_input("اسم مدير المدرسة:", value=user_info['principal_name'])
                
                if st.form_submit_button("حفظ البيانات والمظهر 💾", type="primary", use_container_width=True):
                    payload = {
                        "id": 1,
                        "full_name": n_name,
                        "specialization": n_spec,
                        "school_name": n_school,
                        "education_stage": n_stage,
                        "city": n_city,
                        "principal_name": n_prin,
                        "theme": chosen_theme_key
                    }
                    try:
                        supabase.table("user_profile").upsert(payload).execute()
                    except Exception:
                        payload.pop("theme", None)
                        supabase.table("user_profile").upsert(payload).execute()
                    clear_app_cache()
                    st.success("تم تحديث البيانات والمظهر بنجاح!")
                    time.sleep(0.3)
                    st.rerun()

        with t2:
            st.markdown("##### 🔗 التحكم في وصول الزوار (قراءة ومشاهدة فقط)")
            with st.form("visitor_settings_form"):
                allow_v = st.checkbox("تفعيل السماح بدخول الزوار عبر الرمز السري", value=user_info.get("allow_visitor", True))
                v_code_input = st.text_input("الرمز السري للزائر:", value=str(user_info.get("visitor_code", "1448")))
                if st.form_submit_button("حفظ إعدادات الزائر 🔒", type="primary", use_container_width=True):
                    try:
                        supabase.table("user_profile").update({
                            "allow_visitor": allow_v,
                            "visitor_code": v_code_input.strip()
                        }).eq("id", 1).execute()
                        clear_app_cache()
                        st.success("تم تحديث إعدادات الزائر بنجاح!")
                        time.sleep(0.3)
                        st.rerun()
                    except Exception as e:
                        st.error(f"يرجى التأكد من تحديث جدول user_profile: {e}")

            curr_code = user_info.get("visitor_code", "1448")
            st.info(f"💡 **رابط المشاركة السريعة للزائر:** أضف `?visitor={curr_code}` لنهاية رابط موقعك، أو أعطِ الرمز `{curr_code}` للزائر ليدخله في تبويب (دخول زائر).")

        with t3:
            st.write("تصدير نسخة احتياطية كاملة لبياناتك بصيغة JSON:")
            if st.button("📦 تجهيز ملف النسخة الاحتياطية", type="primary", use_container_width=True):
                backup = {"academic_years": all_years, "standards": stds, "evidences": evidences}
                st.download_button(
                    label="⬇️ تحميل النسخة الاحتياطية (JSON)",
                    data=json.dumps(backup, ensure_ascii=False, indent=4),
                    file_name=f"ziyad_portfolio_backup_{datetime.date.today()}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with t4:
            if st.button("🚪 تسجيل الخروج من الحساب", type="primary", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.is_visitor = False
                st.rerun()

    render_footer()

# ==========================================
# 9. نقطة تشغيل التطبيق
# ==========================================
if st.session_state.user is None and not st.session_state.is_visitor:
    login_page()
else:
    main_app()
