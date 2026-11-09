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
    page_title="ملف الإنجاز المهني",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. منظومة المظاهر (Themes) المتعددة
# ==========================================
THEMES = {
    "emerald": {
        "name": "🟢 الأخضر الوزاري (الافتراضي)",
        "primary": "#146c59",
        "primary_dark": "#0f5243",
        "bg": "#f7f6f2",
        "accent": "#c57b30",
        "tint": "#e6f2ef"
    },
    "royal": {
        "name": "🔵 الأزرق الملكي الاحترافي",
        "primary": "#1e3a8a",
        "primary_dark": "#172554",
        "bg": "#f0f4f8",
        "accent": "#0284c7",
        "tint": "#dbeafe"
    },
    "bronze": {
        "name": "🟤 الذهبي الكلاسيكي الفاخر",
        "primary": "#7c4d25",
        "primary_dark": "#5c3719",
        "bg": "#faf6f0",
        "accent": "#b45309",
        "tint": "#fef3c7"
    },
    "slate": {
        "name": "⚫ الرمادي العصري الداكن",
        "primary": "#1e293b",
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
# 4. الاتصال بقاعدة البيانات وإدارة الجلسة
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
    st.session_state.view_standard_id = 1
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id is not None:
        st.session_state.view_standard_id = std_id
    st.rerun()

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

# تطبيق التصميم (CSS) بناءً على المظهر المختار
user_info = get_user_profile()
active_theme_key = user_info.get("theme", "emerald")
if active_theme_key not in THEMES:
    active_theme_key = "emerald"
th = THEMES[active_theme_key]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stSidebar {{display: none !important;}}
    
    body, [class*="css"] {{
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
        background-color: {th['bg']};
    }}
    .stApp {{ background-color: {th['bg']}; }}
    
    /* الهيدر الترحيبي */
    .greeting-header {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 0 14px 0; border-bottom: 1px solid rgba(0,0,0,0.08); margin-bottom: 16px;
    }}
    .greeting-title {{ font-size: 23px; font-weight: 700; color: {th['primary_dark']}; margin: 0;}}
    .greeting-date {{ font-size: 13px; color: #64748b; margin-top: 4px;}}
    .icon-btn {{ 
        background: {th['primary']}; color: white; width: 40px; height: 40px; 
        border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
        font-weight: bold; font-size: 17px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }}

    /* بانر المدرسة المطور (بدون إجازة ثابتة) */
    .school-banner {{
        background: linear-gradient(135deg, {th['primary']}, {th['primary_dark']});
        color: white; padding: 20px 22px; border-radius: 18px;
        margin-bottom: 18px; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
    }}
    .banner-main {{ font-size: 19px; font-weight: 700; margin: 4px 0; }}
    .banner-sub {{ font-size: 13px; opacity: 0.9; }}
    .banner-badge {{
        background: rgba(255,255,255,0.18); padding: 6px 14px; border-radius: 12px;
        font-size: 13px; font-weight: 700; backdrop-filter: blur(4px);
    }}
    
    /* بطاقات الإحصائيات السريعة */
    .kpi-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px;
    }}
    .kpi-card {{
        background: white; border-radius: 14px; padding: 12px 8px; text-align: center;
        border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    .kpi-val {{ font-size: 21px; font-weight: 700; color: {th['primary']}; }}
    .kpi-lbl {{ font-size: 11px; color: #64748b; margin-top: 2px; }}

    /* شريط الإنجاز */
    .progress-card {{
        background: white; padding: 16px 20px; border-radius: 16px; 
        margin-bottom: 18px; border: 1px solid rgba(0,0,0,0.06);
    }}
    .progress-bar-bg {{
        background: #e2e8f0; height: 9px; border-radius: 5px; width: 100%; overflow: hidden; margin-top: 8px;
    }}
    .progress-bar-fill {{
        background: {th['primary']}; height: 100%; border-radius: 5px;
    }}
    
    /* بطاقة المعيار */
    .std-card {{
        background: white; border: 1px solid rgba(0,0,0,0.07); border-radius: 16px;
        padding: 15px 18px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }}
    .std-num {{
        width: 42px; height: 42px; border-radius: 12px;
        background: {th['tint']}; color: {th['primary']};
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 18px; margin-left: 14px; flex-shrink: 0;
    }}
    .std-num-empty {{ background: #fee2e2; color: #dc2626; }}
    .std-title {{ font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }}
    .weight-badge {{
        background: #f1f5f9; color: #475569; font-size: 12px; padding: 2px 10px;
        border-radius: 8px; display: inline-block;
    }}
    .dots-row {{ display: flex; gap: 5px; margin-bottom: 5px; justify-content: flex-end; }}
    .dot {{ width: 14px; height: 6px; border-radius: 3px; }}
    .dot-on {{ background: {th['primary']}; }}
    .dot-off {{ background: #e2e8f0; }}
    
    /* تصغير صور الشواهد تلقائياً وتكبيرها عند الضغط */
    .thumbs-container {{
        display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0 14px 0;
    }}
    .thumb-link {{
        position: relative; display: inline-block; width: 105px; height: 105px;
        border-radius: 12px; overflow: hidden; border: 2px solid {th['tint']};
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: transform 0.2s ease;
    }}
    .thumb-link:hover {{ transform: scale(1.05); border-color: {th['primary']}; }}
    .thumb-link img {{
        width: 100%; height: 100%; object-fit: cover;
    }}
    .thumb-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0;
        background: rgba(0,0,0,0.6); color: white; font-size: 10px;
        text-align: center; padding: 3px 0;
    }}
    .pdf-badge {{
        display: inline-flex; align-items: center; justify-content: center;
        height: 105px; padding: 0 16px; border-radius: 12px;
        background: #f8fafc; border: 1px dashed {th['primary']};
        color: {th['primary']}; font-weight: 700; font-size: 13px; text-decoration: none;
    }}
    
    /* بطاقة الشاهد */
    .ev-box {{
        background: white; border: 1px solid rgba(0,0,0,0.08); border-radius: 14px;
        padding: 16px; margin-bottom: 12px; border-right: 4px solid {th['primary']};
    }}
    .idea-card {{
        background: white; border: 1px solid rgba(0,0,0,0.06); padding: 11px 15px;
        border-radius: 11px; margin-bottom: 7px; font-size: 14px; color: #334155;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .visitor-banner {{
        background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;
        padding: 10px 16px; border-radius: 12px; margin-bottom: 14px;
        font-weight: 700; font-size: 14px; text-align: center;
    }}
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
# 5. دوال التاريخ والترحيب
# ==========================================
def get_greeting_and_dates():
    tz = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz)
    today = now.date()
    greeting = "صباح الخير" if now.hour < 12 else "مساء الخير"
    
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[today.weekday()]
    g_date = f"{today.day} {months_ar[today.month - 1]} {today.year}م"
    
    h_obj = Gregorian(today.year, today.month, today.day).to_hijri()
    h_months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    h_date = f"{h_obj.day} {h_months[h_obj.month - 1]} {h_obj.year}هـ"
    
    return greeting, f"{day_name} • {h_date} • {g_date}"

# ==========================================
# 6. صفحة تسجيل الدخول (معلم + زائر)
# ==========================================
def login_page():
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="school-banner" style="text-align: center; display: block;">
            <div style="font-size: 25px; font-weight: bold; margin-bottom: 5px;">ملف الإنجاز المهني الإلكتروني</div>
            <div style="font-size: 14px; opacity: 0.9;">{user_info['full_name']} • {user_info['school_name']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    tab_teacher, tab_visitor = st.tabs(["🔒 دخول المعلم (تحكم كامل)", "👁️ دخول زائر (مشاهدة فقط)"])
    
    with tab_teacher:
        with st.form("login_form"):
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("تسجيل الدخول", type="primary", use_container_width=True)
            if submit:
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = response.user
                        st.session_state.is_visitor = False
                        st.success("تم تسجيل الدخول بنجاح!")
                        time.sleep(0.4)
                        st.rerun()
                    except Exception:
                        st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                else:
                    st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")

    with tab_visitor:
        st.info("هذه البوابة مخصصة لمدير المدرسة والمشرف التربوي للاطلاع على ملف الإنجاز بواسطة رمز المشاهدة الممنوح من المعلم.")
        with st.form("visitor_form"):
            v_code = st.text_input("أدخل رمز المشاهدة للزائر:", type="password")
            v_submit = st.form_submit_button("👁️ استعراض ملف الإنجاز", use_container_width=True)
            if v_submit:
                saved_code = str(user_info.get("visitor_code", "1448")).strip()
                if not user_info.get("allow_visitor", True):
                    st.error("المعلم قام بإيقاف خاصية دخول الزوار حالياً.")
                elif v_code.strip() == saved_code:
                    st.session_state.is_visitor = True
                    st.rerun()
                else:
                    st.error("رمز المشاهدة غير صحيح.")

# ==========================================
# 7. التطبيق الرئيسي
# ==========================================
def main_app():
    is_visitor = st.session_state.is_visitor

    # جلب السنة الدراسية النشطة
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else {"id": None, "year_name": "1448"}

    # تنبيه في حال كان التصفح بوضع الزائر
    if is_visitor:
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            st.markdown("<div class='visitor-banner'>👁️ تتصفح الملف حالياً بوضع الزائر (قراءة ومشاهدة فقط)</div>", unsafe_allow_html=True)
        with col_v2:
            if st.button("🚪 خروج الزائر", use_container_width=True):
                st.session_state.is_visitor = False
                st.query_params.clear()
                st.rerun()

    # شريط التنقل العلوي
    if is_visitor:
        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            if st.button("🏠 الرئيسية", use_container_width=True): navigate_to('home')
        with nav2:
            if st.button("📋 تصفح البنود", use_container_width=True): navigate_to('standard_view', st.session_state.view_standard_id)
        with nav3:
            if st.button("📄 طباعة التقرير", type="primary", use_container_width=True): navigate_to('reports')
    else:
        nav1, nav2, nav3, nav4, nav5 = st.columns(5)
        with nav1:
            if st.button("🏠 الرئيسية", use_container_width=True): navigate_to('home')
        with nav2:
            if st.button("📋 البنود", use_container_width=True): navigate_to('standard_view', st.session_state.view_standard_id)
        with nav3:
            if st.button("➕ إضافة", type="primary", use_container_width=True): navigate_to('quick_add')
        with nav4:
            if st.button("📄 التقرير", use_container_width=True): navigate_to('reports')
        with nav5:
            if st.button("⚙️ حسابي", use_container_width=True): navigate_to('settings')

    # الهيدر الترحيبي بالتاريخ الهجري والميلادي
    greeting, today_str = get_greeting_and_dates()
    first_name = user_info['full_name'].split()[0] if user_info['full_name'] else "المعلم"
    first_letter = first_name[0] if first_name else "ز"
    
    st.markdown(f"""
        <div class="greeting-header">
            <div>
                <h1 class="greeting-title">{greeting}، أ. {first_name}</h1>
                <div class="greeting-date">{today_str}</div>
            </div>
            <div>
                <span class="icon-btn">{first_letter}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # جلب المعايير والشواهد
    standards_res = supabase.table("standards").select("*").order("id").execute()
    stds = standards_res.data
    
    evidences = []
    if active_year and active_year.get('id'):
        ev_res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", active_year['id']).order("created_at", desc=True).execute()
        evidences = ev_res.data

    # ----------------------------------------
    # 🏠 1. الصفحة الرئيسية المطورة
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        st.markdown(f"""
            <div class="school-banner">
                <div>
                    <div class="banner-sub">🏫 {user_info['school_name']} • المرحلة: {user_info['education_stage']}</div>
                    <div class="banner-main">{user_info['full_name']}</div>
                    <div class="banner-sub">التخصص: {user_info['specialization']} • مدير المدرسة: {user_info['principal_name']}</div>
                </div>
                <div class="banner-badge">📅 العام الدراسي {active_year['year_name']}هـ</div>
            </div>
        """, unsafe_allow_html=True)

        # حساب الإحصائيات
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

        pct = int((stds_with_ev / total_stds) * 100) if total_stds else 0

        # بطاقات الإحصائيات الرباعية
        st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-val">{total_ev_count}</div>
                    <div class="kpi-lbl">إجمالي الشواهد</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{stds_with_ev}/{total_stds}</div>
                    <div class="kpi-lbl">البنود المغطاة</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{stds_reached_target}</div>
                    <div class="kpi-lbl">حققت المستهدف</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val" style="color:#dc2626;">{empty_stds}</div>
                    <div class="kpi-lbl">بنود فارغة</div>
                </div>
            </div>
            <div class="progress-card">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:14px;">
                    <span>نسبة تغطية معايير الأداء الوظيفي</span>
                    <span style="color:{th['primary']};">{pct}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {pct}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # الفلاتر
        f_col1, f_col2, f_col3 = st.columns(3)
        less_than_3 = sum(1 for s in stds if ev_by_std[s['id']] < s.get('target_evidences', 3))
        with f_col1:
            if st.button(f"الكل • {total_stds}", use_container_width=True):
                st.session_state.filter_mode = 'all'
                st.rerun()
        with f_col2:
            if st.button(f"فارغة • {empty_stds}", use_container_width=True):
                st.session_state.filter_mode = 'empty'
                st.rerun()
        with f_col3:
            if st.button(f"أقل من 3 • {less_than_3}", use_container_width=True):
                st.session_state.filter_mode = 'less3'
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
                f"<div class='dot {'dot-on' if i < count else 'dot-off'}'></div>"
                for i in range(target)
            ])
            
            if count == 0:
                status_txt = "<span style='color:#dc2626; font-size:12px;'>لا شواهد بعد</span>"
                num_cls = "std-num std-num-empty"
            elif count >= target:
                status_txt = f"<span style='color:{th['primary']}; font-size:12px; font-weight:bold;'>مكتمل ({count} شواهد)</span>"
                num_cls = "std-num"
            else:
                status_txt = f"<span style='color:{th['accent']}; font-size:12px;'>{count} شاهد • بقي {target - count}</span>"
                num_cls = "std-num"

            st.markdown(f"""
                <div class="std-card">
                    <div style="display:flex; align-items:center;">
                        <div class="{num_cls}">{s_id}</div>
                        <div>
                            <div class="std-title">{s_id}. {std['title']}</div>
                            <span class="weight-badge">الوزن النسبي: {std['weight']}%</span>
                        </div>
                    </div>
                    <div style="text-align:left;">
                        <div class="dots-row">{dots_html}</div>
                        {status_txt}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📂 استعراض شواهد البند {s_id}", key=f"open_std_{s_id}", use_container_width=True):
                navigate_to('standard_view', s_id)

    # ----------------------------------------
    # 📋 2. صفحة تفاصيل البند الفردي (الصور المصغرة + تاريخ التنفيذ)
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        std_id = st.session_state.view_standard_id
        std_list = [s for s in stds if s['id'] == std_id]
        std_data = std_list[0] if std_list else stds[0]

        c_back, c_title = st.columns([1, 4])
        with c_back:
            if st.button("➡️ رجوع", use_container_width=True):
                navigate_to('home')
        with c_title:
            st.markdown(f"### البند {std_id}: {std_data['title']} (الوزن {std_data['weight']}%)")

        std_evidences = [e for e in evidences if e['standard_id'] == std_id]
        st.markdown(f"#### شواهدك المرفوعة ({len(std_evidences)})")

        if not std_evidences:
            st.info("لا توجد شواهد مرفوعة في هذا البند حتى الآن.")
        else:
            for ev in std_evidences:
                files = ev.get("evidence_files", [])
                # قراءة تاريخ التنفيذ (أو تاريخ الرفع كبديل للشواهد القديمة)
                exec_date = ev.get('execution_date') or ev['created_at'][:10]
                
                # بناء الصور المصغرة القابلة للضغط للتكبير بالحجم الأصلي
                thumbs_html = "<div class='thumbs-container'>"
                for i, f_rec in enumerate(files):
                    try:
                        url_res = supabase.storage.from_("private-achievements").create_signed_url(f_rec['file_url'], 1800)
                        sec_url = url_res['signedURL']
                        if f_rec.get('file_type', '').startswith('image/'):
                            thumbs_html += f"""
                                <a href="{sec_url}" target="_blank" class="thumb-link" title="اضغط لعرض الصورة بالحجم الأصلي">
                                    <img src="{sec_url}" alt="شاهد">
                                    <div class="thumb-overlay">🔍 تكبير</div>
                                </a>
                            """
                        else:
                            thumbs_html += f"""
                                <a href="{sec_url}" target="_blank" class="pdf-badge">
                                    📄 فتح PDF ({i+1})
                                </a>
                            """
                    except Exception:
                        pass
                thumbs_html += "</div>"

                st.markdown(f"""
                    <div class="ev-box">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                            <span style="font-weight:700; font-size:16px; color:{th['primary']};">📄 {ev['title']}</span>
                            <span style="background:{th['tint']}; color:{th['primary_dark']}; padding:4px 12px; border-radius:10px; font-size:12px; font-weight:700;">
                                📅 تاريخ التنفيذ: {exec_date}
                            </span>
                        </div>
                        <div style="font-size:14px; color:#334155; line-height:1.6; margin-bottom:6px;">{ev.get('description') or ''}</div>
                        <div style="font-size:11px; color:#64748b; margin-bottom:4px;">💡 اضغط على الصورة المصغرة لعرضها بالحجم الأصلي الكامل:</div>
                        {thumbs_html}
                    </div>
                """, unsafe_allow_html=True)

                # أزرار التعديل والحذف (تظهر للمعلم فقط وتختفي عن الزائر)
                if not is_visitor:
                    ed_col, del_col = st.columns(2)
                    with ed_col:
                        with st.expander("✏️ تعديل الشاهد وتاريخ التنفيذ"):
                            with st.form(f"edit_form_{ev['id']}"):
                                new_t = st.text_input("عنوان الشاهد:", value=ev['title'])
                                try:
                                    default_d = datetime.date.fromisoformat(str(exec_date)[:10])
                                except Exception:
                                    default_d = datetime.date.today()
                                new_exec_date = st.date_input("تاريخ التنفيذ (حسب توزيع المنهج):", value=default_d)
                                new_d = st.text_area("وصف الشاهد:", value=ev.get('description', ''))
                                new_files = st.file_uploader("استبدال المرفقات (اختياري):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key=f"up_{ev['id']}")
                                
                                if st.form_submit_button("حفظ التعديل 💾", type="primary"):
                                    update_payload = {"title": new_t, "description": new_d, "execution_date": str(new_exec_date)}
                                    try:
                                        supabase.table("evidences").update(update_payload).eq("id", ev['id']).execute()
                                    except Exception:
                                        supabase.table("evidences").update({"title": new_t, "description": new_d}).eq("id", ev['id']).execute()
                                        
                                    if new_files:
                                        old_paths = [f['file_url'] for f in files]
                                        if old_paths:
                                            supabase.storage.from_("private-achievements").remove(old_paths)
                                        supabase.table("evidence_files").delete().eq("evidence_id", ev['id']).execute()
                                        for nf in new_files:
                                            ext = nf.name.split('.')[-1]
                                            path = f"{ev['id']}/{uuid.uuid4()}.{ext}"
                                            supabase.storage.from_("private-achievements").upload(path=path, file=nf.getvalue(), file_options={"content-type": nf.type})
                                            supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": path, "file_type": nf.type}).execute()
                                    st.success("تم التحديث بنجاح!")
                                    time.sleep(0.4)
                                    st.rerun()
                    with del_col:
                        with st.expander("🗑️ حذف الشاهد"):
                            if st.button("تأكيد الحذف النهائي", key=f"confirm_del_{ev['id']}", type="primary"):
                                old_paths = [f['file_url'] for f in files]
                                if old_paths:
                                    supabase.storage.from_("private-achievements").remove(old_paths)
                                supabase.table("evidences").delete().eq("id", ev['id']).execute()
                                st.success("تم الحذف!")
                                time.sleep(0.4)
                                st.rerun()

        st.write("---")

        # جلب البنود الفرعية
        try:
            sub_res = supabase.table("sub_items").select("*").eq("standard_id", std_id).execute()
            db_subs = [item['title'] for item in sub_res.data] if sub_res.data else []
        except Exception:
            db_subs = []
        sub_options = db_subs if db_subs else DEFAULT_SUB_ITEMS.get(std_id, [])

        st.markdown("#### 💡 الشواهد المستهدفة لهذا المعيار")
        for idea in sub_options:
            st.markdown(f"""
                <div class="idea-card">
                    <span>💡 {idea}</span>
                    <span style="color:{th['primary']}; font-weight:bold;">✔</span>
                </div>
            """, unsafe_allow_html=True)

        # نموذج الإضافة (يظهر للمعلم فقط)
        if not is_visitor:
            st.markdown("#### ➕ إضافة شاهد جديد لهذا البند")
            with st.form(f"add_ev_std_{std_id}", clear_on_submit=True):
                chosen_idea = st.selectbox("اختر البند الفرعي:", sub_options + ["أخرى (كتابة عنوان مخصص)"])
                custom_title = st.text_input("عنوان مخصص للشاهد (اختياري):")
                exec_date_input = st.date_input("📅 تاريخ التنفيذ (حسب توزيع المنهج):", value=datetime.date.today())
                desc = st.text_area("وصف الشاهد (الهدف، التنفيذ، الأثر):")
                uploaded_files = st.file_uploader("ارفع المرفقات (صور أو PDF):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
                
                if st.form_submit_button("حفظ الشاهد ورفع المرفقات 💾", type="primary", use_container_width=True):
                    final_title = custom_title.strip() if (chosen_idea == "أخرى (كتابة عنوان مخصص)" or custom_title.strip()) else chosen_idea
                    if final_title and uploaded_files and active_year.get('id'):
                        with st.spinner("جاري رفع المرفقات وحفظ الشاهد..."):
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
                            for up_file in uploaded_files:
                                ext = up_file.name.split('.')[-1]
                                path = f"{new_id}/{uuid.uuid4()}.{ext}"
                                supabase.storage.from_("private-achievements").upload(
                                    path=path, file=up_file.getvalue(), file_options={"content-type": up_file.type}
                                )
                                supabase.table("evidence_files").insert({
                                    "evidence_id": new_id, "file_url": path, "file_type": up_file.type
                                }).execute()
                            st.success("تم حفظ الشاهد بنجاح!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.warning("يرجى اختيار العنوان وإرفاق ملف واحد على الأقل.")

    # ----------------------------------------
    # ➕ 3. صفحة الإضافة السريعة (للمعلم فقط)
    # ----------------------------------------
    elif st.session_state.current_page == 'quick_add' and not is_visitor:
        st.markdown("### ➕ إضافة شاهد سريع")
        std_dict = {f"{s['id']}. {s['title']}": s['id'] for s in stds}
        selected_std_label = st.selectbox("اختر البند الرئيسي:", list(std_dict.keys()))
        sel_std_id = std_dict[selected_std_label]
        
        ideas = DEFAULT_SUB_ITEMS.get(sel_std_id, [])
        with st.form("quick_add_form", clear_on_submit=True):
            chosen_idea = st.selectbox("اختر الشاهد الفرعي:", ideas + ["أخرى..."])
            custom_t = st.text_input("أو اكتب عنواناً مخصصاً:")
            exec_date_q = st.date_input("📅 تاريخ التنفيذ (حسب توزيع المنهج):", value=datetime.date.today())
            desc = st.text_area("وصف الشاهد:")
            up_files = st.file_uploader("المرفقات (صور أو PDF):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
            if st.form_submit_button("حفظ الشاهد 💾", type="primary", use_container_width=True):
                final_t = custom_t.strip() if custom_t.strip() else chosen_idea
                if final_t and up_files and active_year.get('id'):
                    payload = {
                        "standard_id": sel_std_id,
                        "year_id": active_year['id'],
                        "title": final_t,
                        "description": desc,
                        "execution_date": str(exec_date_q)
                    }
                    try:
                        ev_data = supabase.table("evidences").insert(payload).execute()
                    except Exception:
                        payload.pop("execution_date", None)
                        ev_data = supabase.table("evidences").insert(payload).execute()
                        
                    new_id = ev_data.data[0]['id']
                    for f in up_files:
                        ext = f.name.split('.')[-1]
                        path = f"{new_id}/{uuid.uuid4()}.{ext}"
                        supabase.storage.from_("private-achievements").upload(path=path, file=f.getvalue(), file_options={"content-type": f.type})
                        supabase.table("evidence_files").insert({"evidence_id": new_id, "file_url": path, "file_type": f.type}).execute()
                    st.success("تم الحفظ بنجاح!")
                    time.sleep(0.5)
                    navigate_to('standard_view', sel_std_id)
                else:
                    st.warning("يرجى إكمال البيانات وإرفاق ملف.")

    # ----------------------------------------
    # 📄 4. صفحة التقارير والطباعة (3 تصاميم احترافية للاختيار قبل الطباعة)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.markdown("### 📄 تصدير وطباعة ملف الإنجاز (A4 PDF)")
        
        report_style = st.radio(
            "🎨 اختر تصميم التقرير قبل الطباعة:",
            [
                "1. التصميم الرسمي الوزاري (إطار كلاسيكي وجداول رسمية)",
                "2. التصميم العصري الحديث (بطاقات ناعمة وألوان المظهر الحالي)",
                "3. التصميم التنفيذي المختصر (تخطيط مكثف بحدود هندسية أنيقة)"
            ]
        )

        if st.button("تجهيز التقرير بالتصميم المختار للطباعة 🖨️", type="primary", use_container_width=True):
            with st.spinner("جاري تجهيز صفحات A4..."):
                ev_res = supabase.table("evidences").select("*, standards(title, weight, target_evidences), evidence_files(*)").eq("year_id", active_year['id']).order("standard_id").execute()
                all_evidences = ev_res.data
                
                total_evidences = len(all_evidences)
                active_stds = [s for s in stds if len([e for e in all_evidences if e['standard_id'] == s['id']]) > 0]
                covered_stds = len(active_stds)

                # تحديد ألوان وأنماط التقرير بناءً على التصميم المختار
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
                        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
                        body {{ font-family: 'Tajawal', sans-serif; background-color: #cbd5e1; margin: 0; padding: 20px; }}
                        .page {{ background-color: white; width: 210mm; height: 296mm; padding: 10mm 15mm; margin: 0 auto 20mm auto; box-shadow: 0 10px 20px rgba(0,0,0,0.15); box-sizing: border-box; page-break-after: always; page-break-inside: avoid; display: flex; flex-direction: column; overflow: hidden; }}
                        .cover-page {{ border: {cover_border}; border-radius: {box_radius}; padding: 35px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; box-sizing: border-box; }}
                        .cover-title {{ color: {rep_color}; font-size: 38px; font-weight: bold; margin-bottom: 10px; }}
                        .cover-subtitle {{ font-size: 20px; margin-bottom: 40px; font-weight: bold; color: #475569; }}
                        .info-table {{ width: 88%; border-collapse: collapse; margin: 0 auto; font-size: 17px; }}
                        .info-table th, .info-table td {{ border: 1px solid #cbd5e1; padding: 13px; text-align: center; }}
                        .info-table th {{ background-color: #f8fafc; width: 32%; font-weight: bold; color: {rep_color}; }}
                        .header-container {{ display: flex; justify-content: space-between; border-bottom: 2px solid {rep_color}; padding-bottom: 8px; margin-bottom: 14px; font-size: 13px; font-weight: bold; flex-shrink: 0; }}
                        .header-right {{ color: {rep_color}; }}
                        .header-left {{ text-align: left; }}
                        .index-title {{ color: {rep_color}; font-size: 24px; font-weight: bold; margin-bottom: 18px; }}
                        .index-table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
                        .index-table th {{ background-color: #f1f5f9; color: {rep_color}; padding: 10px; text-align: center; border-bottom: 2px solid {rep_color}; }}
                        .index-table td {{ padding: 10px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
                        .content-wrapper {{ flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }}
                        .std-header {{ background-color: {rep_color}; color: white; padding: 10px 15px; font-size: 16px; font-weight: bold; border-radius: {box_radius} {box_radius} 0 0; flex-shrink: 0; }}
                        .ev-header {{ background-color: {rep_sub}; color: white; padding: 8px 15px; font-size: 14px; margin-bottom: 14px; border-radius: 0 0 {box_radius} {box_radius}; flex-shrink: 0; }}
                        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; flex-shrink: 0; }}
                        .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 9px; text-align: center; border-radius: {box_radius}; }}
                        .meta-title {{ font-size: 12px; color: #64748b; font-weight: bold; }}
                        .meta-value {{ font-size: 14px; font-weight: bold; color: #0f172a; }}
                        .desc-section {{ margin-bottom: 14px; line-height: 1.6; font-size: 14px; padding: 10px; background: #fafafa; border-right: 4px solid {rep_color}; border-radius: {box_radius}; flex-shrink: 0; }}
                        .images-grid {{ flex-grow: 1; display: flex; justify-content: center; align-items: center; gap: 12px; min-height: 0; padding: 5px 0; overflow: hidden; }}
                        .images-grid img {{ max-width: 100%; max-height: 100%; object-fit: contain; border: 1px solid #cbd5e1; border-radius: {box_radius}; }}
                        .pdf-notice {{ background: #f1f5f9; padding: 9px; text-align: center; border-radius: {box_radius}; font-size: 13px; color: #334155; margin-bottom: 10px; border: 1px dashed #94a3b8; flex-shrink: 0; }}
                        .signatures {{ display: flex; justify-content: space-between; margin-top: auto; border-top: 2px solid #e2e8f0; padding-top: 12px; text-align: center; flex-shrink: 0; }}
                        .sig-box {{ width: 42%; }}
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
                        <div style="font-size:16px; font-weight:bold; color:{rep_color}; margin-bottom:10px;">المملكة العربية السعودية • وزارة التعليم</div>
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
                    </div>
                </div>
                """
                
                shared_header = f"""
                <div class="header-container">
                    <div class="header-right">
                        {user_info['full_name']}<br>
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
                    count = len([e for e in all_evidences if e['standard_id'] == std['id']])
                    if count == 0:
                        continue
                    target = std.get('target_evidences', 3)
                    html_content += f"<tr><td>{std['id']}</td><td style='text-align:right; font-weight:bold;'>{std['title']}</td><td>{std['weight']}%</td><td style='color:{rep_color}; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
                html_content += "</table></div>"
                
                for ev in all_evidences:
                    std = ev['standards']
                    exec_date = ev.get('execution_date') or ev['created_at'][:10]
                    files = ev.get('evidence_files', [])
                    img_html = ""
                    pdf_count = 0
                    for f in files:
                        if f.get('file_type', '').startswith('image/'):
                            url_res = supabase.storage.from_("private-achievements").create_signed_url(f['file_url'], 3600)
                            img_html += f"<img src='{url_res['signedURL']}'>"
                        elif f.get('file_type') == 'application/pdf':
                            pdf_count += 1
                            
                    pdf_notice = f"<div class='pdf-notice'>📌 مرفق مستند PDF رسمي عدد ({pdf_count}) محفوظ في النظام الإلكتروني.</div>" if pdf_count > 0 else ""
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
                            {images_section}
                        </div>
                        <div class="signatures">
                            <div class="sig-box">
                                <div style="color:#666; font-size:12px; margin-bottom:18px;">المعلم:</div>
                                <div style="font-weight:bold;">{user_info['full_name']}</div>
                            </div>
                            <div class="sig-box">
                                <div style="color:#666; font-size:12px; margin-bottom:18px;">مدير المدرسة:</div>
                                <div style="font-weight:bold;">{user_info['principal_name']}</div>
                            </div>
                        </div>
                    </div>
                    """
                
                html_content += "</body></html>"
                safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                
                components.html(f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <button onclick="openPrintWindow()" style="width: 100%; padding: 15px; background-color: {rep_color}; color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; font-family: 'Tajawal', sans-serif;">
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
        st.markdown("### ⚙️ إعدادات الحساب والمظهر والمشاركة")
        t1, t2, t3, t4 = st.tabs(["👤 البيانات والمظهر", "🔗 مشاركة الملف (للزوار)", "💾 النسخ الاحتياطي", "🚪 الخروج"])
        
        with t1:
            with st.form("profile_form"):
                st.markdown("#### 🎨 مظهر التطبيق")
                theme_keys = list(THEMES.keys())
                theme_labels = [THEMES[k]["name"] for k in theme_keys]
                current_idx = theme_keys.index(active_theme_key) if active_theme_key in theme_keys else 0
                selected_theme_label = st.selectbox("اختر المظهر اللوني للتطبيق:", theme_labels, index=current_idx)
                chosen_theme_key = theme_keys[theme_labels.index(selected_theme_label)]

                st.markdown("#### 📝 البيانات الأساسية")
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
                    st.success("تم تحديث البيانات والمظهر بنجاح!")
                    time.sleep(0.4)
                    st.rerun()

        with t2:
            st.markdown("#### 🔗 التحكم في وصول الزوار (قراءة ومشاهدة فقط)")
            st.write("يمكنك مشاركة ملف إنجازك مع مدير المدرسة أو المشرف التربوي للاطلاع فقط دون السماح لهم بالتعديل أو الحذف.")
            with st.form("visitor_settings_form"):
                allow_v = st.checkbox("تفعيل السماح بدخول الزوار عبر الرمز السري", value=user_info.get("allow_visitor", True))
                v_code_input = st.text_input("الرمز السري للزائر (أعطِ هذا الرمز فقط لمن ترغب باطلاعه على ملفك):", value=str(user_info.get("visitor_code", "1448")))
                if st.form_submit_button("حفظ إعدادات الزائر 🔒", type="primary"):
                    try:
                        supabase.table("user_profile").update({
                            "allow_visitor": allow_v,
                            "visitor_code": v_code_input.strip()
                        }).eq("id", 1).execute()
                        st.success("تم تحديث إعدادات الزائر بنجاح!")
                        time.sleep(0.4)
                        st.rerun()
                    except Exception as e:
                        st.error(f"يرجى تنفيذ كود SQL الخاص بحقول الزائر أولاً: {e}")

            curr_code = user_info.get("visitor_code", "1448")
            st.info(f"💡 **طريقة المشاركة السريعة:** أضف `?visitor={curr_code}` في نهاية رابط تطبيقك لإرساله مباشرة للمدير أو المشرف، أو اطلب منه إدخال الرمز `{curr_code}` في تبويب (دخول زائر) بصفحة الدخول.")

        with t3:
            st.write("تصدير نسخة احتياطية كاملة لبياناتك بصيغة JSON:")
            if st.button("📦 تجهيز ملف النسخة الاحتياطية", type="primary", use_container_width=True):
                backup = {"standards": stds, "evidences": evidences}
                st.download_button(
                    label="⬇️ تحميل النسخة الاحتياطية (JSON)",
                    data=json.dumps(backup, ensure_ascii=False, indent=4),
                    file_name=f"portfolio_backup_{datetime.date.today()}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with t4:
            if st.button("🚪 تسجيل الخروج من الحساب", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.is_visitor = False
                st.rerun()

# ==========================================
# 8. نقطة تشغيل التطبيق
# ==========================================
if st.session_state.user is None and not st.session_state.is_visitor:
    login_page()
else:
    main_app()
