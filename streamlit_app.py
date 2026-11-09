import streamlit as st
from supabase import create_client
import time
import uuid
import json
import math
from datetime import datetime, date
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة والتصميم العام (CSS)
# ==========================================
st.set_page_config(page_title="ملف الإنجاز المهني", page_icon="💼", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
        background-color: #F6F5F0;
    }

    /* الترويسة الترحيبية العليا */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 5px 20px 5px;
    }
    .greeting-box h2 {
        margin: 0;
        font-size: 26px;
        font-weight: 800;
        color: #1A2E28;
    }
    .greeting-box p {
        margin: 4px 0 0 0;
        font-size: 14px;
        color: #7A827E;
    }
    .avatar-circle {
        width: 48px;
        height: 48px;
        background-color: #0F5243;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 2px 6px rgba(15, 82, 67, 0.25);
    }

    /* بطاقة المدرسة وتقويم الإجازات */
    .school-banner {
        background: linear-gradient(135deg, #0F5243 0%, #176B58 100%);
        color: white;
        padding: 22px 25px;
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 6px 15px rgba(15, 82, 67, 0.15);
        position: relative;
        overflow: hidden;
    }
    .school-banner .school-name {
        font-size: 15px;
        color: #CBE5DF;
        margin-bottom: 6px;
    }
    .school-banner .calendar-info {
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* بطاقة إحصائية الإنجاز */
    .summary-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #E6E4DD;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }
    .progress-section {
        flex-grow: 1;
    }
    .progress-title {
        font-size: 16px;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 10px;
    }
    .custom-progress-bg {
        width: 100%;
        height: 9px;
        background-color: #ECEAE2;
        border-radius: 5px;
        overflow: hidden;
    }
    .custom-progress-fill {
        height: 100%;
        background-color: #0F5243;
        border-radius: 5px;
    }
    .stats-counters {
        display: flex;
        gap: 18px;
        align-items: center;
    }
    .counter-item {
        text-align: center;
        padding-left: 15px;
        border-left: 1px solid #EAEAEA;
    }
    .counter-item:last-child {
        border-left: none;
        padding-left: 0;
    }
    .counter-num {
        font-size: 22px;
        font-weight: 800;
        line-height: 1.1;
    }
    .counter-label {
        font-size: 12px;
        color: #777;
    }

    /* بطاقة البند الرئيسي */
    .std-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 12px;
        border: 1px solid #EAE8E1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .std-right {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .std-num-box {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 18px;
    }
    .num-active { background-color: #F4EFE6; color: #B4782B; }
    .num-empty { background-color: #F9EBEC; color: #B93829; }
    
    .std-info-title {
        font-size: 17px;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 6px;
    }
    .badge-weight {
        background-color: #EFECE6;
        color: #555;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-left: 6px;
        font-weight: 500;
    }
    .badge-est {
        background-color: #E2F2EE;
        color: #0F5243;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        font-weight: 700;
    }
    .dots-row {
        display: flex;
        gap: 5px;
        margin-bottom: 6px;
        justify-content: flex-end;
    }
    .dot-bar {
        width: 18px;
        height: 6px;
        border-radius: 4px;
    }
    .dot-on { background-color: #C47F2A; }
    .dot-off { background-color: #E2E0D8; }

    /* بطاقة الشاهد المرفوع داخل البند */
    .ev-grid-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .ev-card-top {
        background-color: #E6F4EE;
        height: 85px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #146C59;
        font-size: 20px;
        font-weight: bold;
    }
    .ev-card-bottom {
        padding: 14px;
    }
    .ev-card-title {
        font-weight: 700;
        font-size: 15px;
        color: #1F2937;
        margin-bottom: 8px;
    }
    .ev-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #6B7280;
    }
    .approved-pill {
        background-color: #E2F2EE;
        color: #0F5243;
        padding: 2px 10px;
        border-radius: 10px;
        font-weight: 700;
    }

    /* قائمة الأفكار (المعايير الفرعية) */
    .idea-row {
        background-color: #FFFFFF;
        border: 1px solid #EAE8E1;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .idea-title {
        font-size: 15px;
        font-weight: 700;
        color: #2D3748;
    }
    .idea-desc {
        font-size: 12px;
        color: #718096;
        margin-top: 2px;
    }

    /* صفحة استعراض الشاهد التفصيلية */
    .evidence-detail-box {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 22px;
        border: 1px solid #EAE8E1;
        margin-bottom: 20px;
    }
    .leader-notes-box {
        background-color: #E8F3EE;
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        color: #0F5243;
        border-right: 4px solid #0F5243;
    }

    /* تحسين الأزرار */
    div[data-testid="stButton"] button {
        border-radius: 12px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. دوال التاريخ الهجري والميلادي والترحيب
# ==========================================
def gregorian_to_hijri(y, m, d):
    """تحويل التاريخ الميلادي إلى هجري تلقائياً بدون مكتبات خارجية إضافية"""
    jd = int((1461 * (y + 4800 + int((m - 14) / 12))) / 4) + \
         int((367 * (m - 2 - 12 * (int((m - 14) / 12)))) / 12) - \
         int((3 * (int((y + 4900 + int((m - 14) / 12)) / 100))) / 4) + d - 32075
    l = jd - 1948440 + 10632
    n = int((l - 1) / 10631)
    l = l - 10631 * n + 354
    j = (int((10985 - l) / 5316)) * (int((50 * l) / 17719)) + (int(l / 5670)) * (int((43 * l) / 15238))
    l = l - (int((30 - j) / 15)) * (int((17719 * j) / 50)) - (int(j / 16)) * (int((15238 * j) / 43)) + 29
    h_month = int((24 * l) / 709)
    h_day = l - int((709 * h_month) / 24)
    h_year = 30 * n + j - 30
    
    hijri_months = [
        "", "محرم", "صفر", "ربيع الأول", "ربيع الآخر", 
        "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", 
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
    ]
    return f"{h_day} {hijri_months[h_month]} {h_year}هـ"

def get_arabic_date_line():
    now = datetime.now()
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[now.weekday()]
    greg_str = f"{now.day} {months_ar[now.month]} {now.year}م"
    hijri_str = gregorian_to_hijri(now.year, now.month, now.day)
    
    greeting = "صباح الخير" if now.hour < 12 else "مساء الخير"
    return greeting, f"{day_name} • {hijri_str} • {greg_str}"

# ==========================================
# 3. الاتصال بقاعدة البيانات وإدارة الجلسة
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state: st.session_state.user = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'
if 'selected_std_id' not in st.session_state: st.session_state.selected_std_id = None
if 'selected_ev_id' not in st.session_state: st.session_state.selected_ev_id = None
if 'prefill_idea_title' not in st.session_state: st.session_state.prefill_idea_title = ""
if 'confirm_del_id' not in st.session_state: st.session_state.confirm_del_id = None

def navigate_to(page_name, std_id=None, ev_id=None):
    st.session_state.current_page = page_name
    st.session_state.selected_std_id = std_id
    st.session_state.selected_ev_id = ev_id
    st.session_state.confirm_del_id = None
    st.rerun()

# ==========================================
# 4. صفحة تسجيل الدخول
# ==========================================
def login_page():
    st.markdown("<h2 style='text-align:center; color:#0F5243; margin-top:40px;'>🔒 ملف الإنجاز المهني</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("تسجيل الدخول", type="primary", use_container_width=True):
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.rerun()
                except Exception:
                    st.error("بيانات الدخول غير صحيحة.")
            else:
                st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")

# ==========================================
# 5. شريط الإحصائيات المشترك
# ==========================================
def render_summary_bar(stds, all_evidences):
    total_stds = len(stds)
    stds_with_ev = 0
    stds_reached_target = 0
    
    for s in stds:
        c = len([e for e in all_evidences if e['standard_id'] == s['id']])
        if c > 0:
            stds_with_ev += 1
        if c >= s['target_evidences']:
            stds_reached_target += 1
            
    empty_stds = total_stds - stds_with_ev
    pct = int((stds_with_ev / total_stds) * 100) if total_stds else 0

    st.markdown(f"""
    <div class="summary-card">
        <div class="progress-section">
            <div class="progress-title">{stds_with_ev} من {total_stds} فيها شواهد</div>
            <div class="custom-progress-bg">
                <div class="custom-progress-fill" style="width: {pct}%;"></div>
            </div>
        </div>
        <div class="stats-counters">
            <div class="counter-item">
                <div class="counter-num" style="color: #0F5243;">{stds_reached_target}</div>
                <div class="counter-label">وصلت الهدف</div>
            </div>
            <div class="counter-item">
                <div class="counter-num" style="color: #B93829;">{empty_stds}</div>
                <div class="counter-label">فارغة</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. التطبيق الرئيسي
# ==========================================
def main_app():
    # جلب السنة الدراسية النشطة
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None

    # جلب بيانات المعلم
    profile_res = supabase.table("user_profile").select("*").eq("id", 1).execute()
    if profile_res.data:
        user_info = profile_res.data[0]
    else:
        user_info = {
            "full_name": "زياد المعمري", "specialization": "لغة إنجليزية / تربية خاصة",
            "school_name": "ابتدائية عبادة بن قيس الأنصاري", "education_stage": "ابتدائي / متوسط",
            "city": "المدينة المنورة", "principal_name": "عبدالمجيد الحربي",
            "show_calendar": True, "calendar_text": "الأسبوع 11 • إجازة
