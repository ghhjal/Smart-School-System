import streamlit as st
from supabase import create_client
import time
import uuid
import json
import datetime
from hijri_converter import Gregorian
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة و CSS (تصميم الجوال الحديث)
# ==========================================
st.set_page_config(page_title="ملف الإنجاز المهني", page_icon="🟢", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    /* إخفاء واجهة Streamlit الافتراضية */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSidebar {display: none !important;}
    
    body, [class*="css"] {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
        background-color: #f7f6f2; /* لون الخلفية حسب الصورة */
    }
    
    /* الهيدر الترحيبي */
    .greeting-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 15px;
    }
    .greeting-title { font-size: 24px; font-weight: 700; color: #1a4a40; margin: 0;}
    .greeting-date { font-size: 13px; color: #7f8c8d; margin-top: 5px;}
    .icon-btn { 
        background: #146c59; color: white; width: 40px; height: 40px; 
        border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
        font-weight: bold; margin-right: 5px; font-size:18px;
    }

    /* بانر المدرسة والإجازة */
    .school-banner {
        background-color: #146c59; color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 20px;
    }
    .school-name { font-size: 13px; opacity: 0.9; margin-bottom: 5px; text-align: left; }
    .holiday-text { font-size: 18px; font-weight: bold; text-align: left; margin: 0; }
    
    /* شريط التقدم الدائري / الخطي */
    .progress-container { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #eee; display: flex; align-items: center;}
    .progress-stats { flex-grow: 1; }
    .progress-title { font-size: 16px; font-weight: bold; margin-bottom: 10px;}
    .progress-bar-bg { background: #e0e0e0; height: 8px; border-radius: 4px; width: 100%; position: relative; overflow: hidden;}
    .progress-bar-fill { background: #146c59; height: 100%; border-radius: 4px;}
    .progress-numbers { display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-top: 8px;}
    
    /* بطاقات البنود الرئيسية */
    .item-card {
        background: white; border: 1px solid #eee; border-radius: 12px; padding: 15px; 
        margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .item-num { background: #faebd7; color: #d35400; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; margin-left: 15px;}
    .item-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; color: #333;}
    .item-meta { font-size: 12px; color: #888; background: #f0f0f0; padding: 2px 8px; border-radius: 10px; display: inline-block;}
    .item-status { font-size: 12px; color: #d35400; margin-top: 5px;}
    .item-empty { color: #aaa; }
    
    /* البنود الفرعية (أفكار تبدأ منها) */
    .sub-item-card { background: transparent; border: 1px solid #e0e0e0; padding: 12px; border-radius: 8px; margin-bottom: 8px; font-size: 14px; color: #333; display: flex; align-items: center;}
    .sub-icon { color: #d35400; margin-left: 10px; font-size: 18px;}
    
    /* شريط الملاحة السفلي */
    .bottom-nav {
        position: fixed; bottom: 0; left: 0; right: 0; background: white; 
        display: flex; justify-content: space-around; padding: 10px 0; 
        border-top: 1px solid #e0e0e0; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    
    /* مساحة فارغة في الأسفل لمنع تغطية المحتوى */
    .spacer { height: 80px; }
    
    /* أزرار مخصصة (لتحل محل أزرار Streamlit في القائمة السفلية) */
    div[data-testid="stButton"] button {
        border: none; background: transparent; color: #7f8c8d; padding: 5px; font-size: 12px; font-weight: bold; display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    div[data-testid="stButton"] button:hover, div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus {
        color: #146c59; background: transparent; border: none; box-shadow: none;
    }
    
    /* زر الإضافة العائم الكبير */
    .fab-btn button {
        background-color: #146c59 !important; color: white !important; width: 60px !important; height: 60px !important; border-radius: 50% !important; margin-top: -20px !important; box-shadow: 0 4px 10px rgba(20, 108, 89, 0.4) !important;
    }
    
    /* زر الإضافة العريض داخل البند */
    .add-wide-btn button { background-color: #146c59 !important; color: white !important; width: 100% !important; border-radius: 8px !important; height: 50px !important; font-size: 16px !important;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. التهيئة والاتصال
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state: st.session_state.user = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'
if 'view_standard_id' not in st.session_state: st.session_state.view_standard_id = None

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id: st.session_state.view_standard_id = std_id
    st.rerun()

# ==========================================
# 3. دوال مساعدة (التواريخ والإجازات)
# ==========================================
def get_today_dates():
    today = datetime.date.today()
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[today.weekday()]
    g_date = f"{today.day} {months_ar[today.month - 1]} {today.year}م"
    
    h_date_obj = Gregorian(today.year, today.month, today.day).to_hijri()
    h_months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    h_date = f"{h_date_obj.day} {h_months[h_date_obj.month - 1]} {h_date_obj.year}هـ"
    
    return f"{day_name} • {h_date} • {g_date}"

# ==========================================
# 4. واجهة المستخدم الرئيسية (UI)
# ==========================================
def main_app():
    # جلب البيانات الأساسية
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None
    
    profile_res = supabase.table("user_profile").select("*").eq("id", 1).execute()
    user_info = profile_res.data[0] if profile_res.data else {"full_name": "المعلم", "school_name": "المدرسة"}

    # الهيدر الترحيبي (يظهر دائماً في الأعلى)
    first_name = user_info['full_name'].split()[0] if user_info['full_name'] else "المعلم"
    st.markdown(f"""
        <div class="greeting-header">
            <div>
                <h1 class="greeting-title">مساء الخير، أ. {first_name}</h1>
                <div class="greeting-date">{get_today_dates()}</div>
            </div>
            <div>
                <span class="icon-btn">🔍</span>
                <span class="icon-btn">🔔</span>
                <span class="icon-btn">ز</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # 🏠 الصفحة الرئيسية (الرئيسية)
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        # بانر المدرسة والإجازات
        st.markdown(f"""
            <div class="school-banner">
                <div class="school-name">{user_info['school_name']}</div>
                <div class="holiday-text">الأسبوع 11 • إجازة الخريف بعد 11 يوماً</div>
            </div>
        """, unsafe_allow_html=True)
        
        # جلب الإحصائيات الحقيقية
        standards_res = supabase.table("standards").select("*").order("id").execute()
        stds = standards_res.data
        
        ev_res = supabase.table("evidences").select("*").eq("year_id", active_year['id']).execute() if active_year else None
        evidences = ev_res.data if ev_res else []
        
        covered_stds = len(set([e['standard_id'] for e in evidences]))
        total_stds = len(stds)
        completion_percent = int((covered_stds / total_stds) * 100) if total_stds else 0
        
        # شريط التقدم
        st.markdown(f"""
            <div class="progress-container">
                <div style="margin-left: 20px; text-align: center; color: #146c59;">
                    <div style="font-size: 24px; font-weight: bold; line-height: 1;">{covered_stds}</div>
                    <div style="font-size: 12px;">من 11 فيها شواهد</div>
                </div>
                <div class="progress-stats">
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {completion_percent}%;"></div></div>
                    <div class="progress-numbers"><span>وصلت الهدف 0</span><span style="color:#d35400;">فارغة {total_stds - covered_stds}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # فلاتر علوية
        st.markdown("""
        <div style="display:flex; justify-content:flex-end; gap:10px; margin-bottom:15px;">
            <span style="background:white; border:1px solid #ddd; padding:5px 15px; border-radius:20px; font-size:13px; color:#555;">أقل من 3 • 11</span>
            <span style="background:white; border:1px solid #ddd; padding:5px 15px; border-radius:20px; font-size:13px; color:#555;">فارغة • 5</span>
            <span style="background:#146c59; color:white; padding:5px 15px; border-radius:20px; font-size:13px;">الكل • 11</span>
        </div>
        """, unsafe_allow_html=True)
        
        # قائمة البنود القابلة للضغط
        for std in stds:
            count = len([e for e in evidences if e['standard_id'] == std['id']])
            status_html = f"<div class='item-status'>1 شاهد • بقي 2</div>" if count > 0 else "<div class='item-status item-empty'>لا شواهد بعد</div>"
            
            # كل بطاقة هي زر ينقل لصفحة البند
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(f"{std['title']} (الوزن {std['weight']}%) \n {count} شواهد", key=f"btn_{std['id']}", use_container_width=True):
                    navigate_to('standard_view', std['id'])
            with col2:
                st.markdown(f"<div class='item-num'>{std['id']}</div>", unsafe_allow_html=True)

    # ----------------------------------------
    # 📄 صفحة عرض البند الفردي
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        std_id = st.session_state.view_standard_id
        std_data = supabase.table("standards").select("*").eq("id", std_id).execute().data[0]
        
        # شريط العنوان العلوي
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ عودة"): navigate_to('home')
        with col2:
            st.markdown(f"<h3 style='margin:0;'>البند {std_id}</h3>", unsafe_allow_html=True)
            
        st.info(f"تقدير استرشادي من شواهدك في مثالي: {std_data['title']}")
        
        # 1. عرض الشواهد المرفوعة
        ev_res = supabase.table("evidences").select("*, evidence_files(*)").eq("standard_id", std_id).eq("year_id", active_year['id']).execute()
        
        st.markdown("### شواهدك")
        if not ev_res.data:
            st.markdown("""
            <div style="border:2px dashed #ccc; padding:30px; text-align:center; border-radius:12px; color:#888;">
                <span style="font-size:24px;">➕</span><br>شاهد جديد
            </div>
            """, unsafe_allow_html=True)
        else:
            for ev in ev_res.data:
                files = ev.get("evidence_files", [])
                st.markdown(f"""
                <div style="background:#e6f2ef; border:1px solid #146c59; padding:15px; border-radius:12px; margin-bottom:10px;">
                    <div style="text-align:center; color:#146c59; font-size:20px; margin-bottom:10px;">📄 {len(files)}</div>
                    <div style="font-weight:bold; text-align:center; margin-bottom:5px;">{ev['title']}</div>
                    <div style="text-align:center; font-size:12px; color:#146c59;"><span style="background:#d1e8e2; padding:2px 8px; border-radius:10px;">معتمد</span> {ev['created_at'][:10]}</div>
                </div>
                """, unsafe_allow_html=True)

        # 2. عرض أفكار الشواهد (البنود الفرعية)
        st.markdown("### أفكار تبدأ منها")
        sub_items = supabase.table("sub_items").select("*").eq("standard_id", std_id).execute().data
        for item in sub_items:
            st.markdown(f"""
            <div class="sub-item-card">
                <span style="color:#146c59; font-weight:bold; margin-left:10px;">⊕</span>
                <span style="flex-grow:1;">{item['title']}</span>
                <span class="sub-icon">💡</span>
            </div>
            """, unsafe_allow_html=True)

        # نموذج إضافة الشاهد السريع
        st.write("---")
        with st.expander("➕ إضافة شاهد لهذا البند", expanded=False):
            with st.form(f"add_ev_{std_id}", clear_on_submit=True):
                title = st.selectbox("اختر نوع الشاهد:", [s['title'] for s in sub_items] + ["أخرى..."])
                if title == "أخرى...": title = st.text_input("اكتب عنوان الشاهد:")
                desc = st.text_area("وصف التنفيذ، الأثر المستهدف:")
                uploaded_files = st.file_uploader("المرفقات", type=["pdf", "jpg", "png"], accept_multiple_files=True)
                
                st.markdown("<div class='add-wide-btn'>", unsafe_allow_html=True)
                if st.form_submit_button("حفظ الشاهد", type="primary"):
                    if title and uploaded_files:
                        ev_data = supabase.table("evidences").insert({"standard_id": std_id, "year_id": active_year['id'], "title": title, "description": desc}).execute()
                        new_id = ev_data.data[0]['id']
                        for up_file in uploaded_files:
                            ext = up_file.name.split('.')[-1]
                            path = f"{new_id}/{uuid.uuid4()}.{ext}"
                            supabase.storage.from_("private-achievements").upload(path=path, file=up_file.getvalue(), file_options={"content-type": up_file.type})
                            supabase.table("evidence_files").insert({"evidence_id": new_id, "file_url": path, "file_type": up_file.type}).execute()
                        st.success("تم الحفظ!")
                        time.sleep(1)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------
    # 📄 صفحة التقارير / التصدير
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        # نفس كود التصدير للـ PDF الذي عملنا عليه سابقاً يعمل بشكل ممتاز هنا
        st.info("صفحة تصدير التقارير (الكود السابق يعمل هنا)")
        
    elif st.session_state.current_page == 'settings':
        st.info("صفحة إعدادات المعلم والنسخ الاحتياطي (الكود السابق يعمل هنا)")

    # ==========================================
    # شريط الملاحة السفلي (Bottom Navigation)
    # ==========================================
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='bottom-nav'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠\nالرئيسية", use_container_width=True): navigate_to('home')
    with col2:
        if st.button("📋\nالبنود", use_container_width=True): navigate_to('home')
    with col3:
        st.markdown("<div class='fab-btn'>", unsafe_allow_html=True)
        if st.button("➕", use_container_width=True): navigate_to('home') # يفتح نافذة سريعة لاحقاً
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        if st.button("📄\nملف الإنجاز", use_container_width=True): navigate_to('reports')
    with col5:
        if st.button("👤\nحسابي", use_container_width=True): navigate_to('settings')
    st.markdown("</div>", unsafe_allow_html=True)

# تشغيل التطبيق
if st.session_state.user is None: login_page()
else: main_app()
