import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime
from streamlit_option_menu import option_menu # مكتبة القوائم الاحترافية

# ---------------------------------------------------------
# 1. إعداد الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="نظام مدرستي",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. تصميم CSS الاحترافي (Modern UI + RTL)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* استيراد خط Cairo العصري */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

    /* تطبيق الخط واتجاه اليمين */
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    /* إخفاء عناصر ستريم ليت المزعجة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}

    /* خلفية التطبيق */
    .stApp {
        background-color: #f8f9fa;
    }

    /* تصميم البطاقات (Cards) */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #eee;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333;
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }

    /* تحسين الأزرار */
    .stButton > button {
        background: linear-gradient(45deg, #2575fc, #6a11cb);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }

    /* تحسين حقول الإدخال */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
        text-align: right;
    }
    
    /* تحسين العناوين */
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الدوال الأساسية
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def get_db_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# ---------------------------------------------------------
# 4. واجهة التطبيق
# ---------------------------------------------------------

# --- القائمة الجانبية (الشكل الجديد) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 مدرستي</h2>", unsafe_allow_html=True)
    
    # القائمة الاحترافية (Option Menu)
    selected = option_menu(
        menu_title=None,
        options=["الرئيسية", "بوابة الموظفين", "بوابة ولي الأمر", "استيراد بيانات"],
        icons=["house", "person-badge", "people", "cloud-upload"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#ffffff"},
            "icon": {"color": "#6a11cb", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "right", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#6a11cb"},
        }
    )
    
    st.markdown("---")
    if st.session_state.logged_in:
        role = st.session_state.user_info.get('Role')
        user = st.session_state.user_info.get('Username')
        st.caption(f"👤 {user} | {role}")
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# --- المحتوى الرئيسي ---

# 1. الصفحة الرئيسية (Dashboard)
if selected == "الرئيسية":
    st.markdown("### 📊 لوحة المعلومات العامة")
    
    # بطاقات إحصائية بتصميم جميل
    col1, col2, col3, col4 = st.columns(4)
    
    # نحاول جلب الأرقام الحقيقية
    try:
        db = get_db_connection()
        st_count = len(db.worksheet("Students").get_all_values()) - 1
    except: st_count = 0
    
    col1.metric("👨‍🎓 الطلاب", f"{st_count}", "+جديد")
    col2.metric("📅 الفصل الدراسي", "الثاني", "1445")
    col3.metric("🏫 الفصول", "12", "فصل")
    col4.metric("✅ حالة النظام", "مفعل")

    st.markdown("---")
    
    # قسم الأخبار بتصميم البطاقات
    st.subheader("📢 آخر الإعلانات")
    try:
        sheet_news = db.worksheet("News")
        df_news = pd.DataFrame(sheet_news.get_all_records())
        if not df_news.empty:
            for i, row in df_news.tail(3).iloc[::-1].iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; border-right: 5px solid #6a11cb; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color: #6a11cb;">{row['Title']}</h4>
                    <p style="color: #666;">{row['Content']}</p>
                    <small style="color: #999;">📅 {row['Date']} | ✍️ {row['Author']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد أخبار جديدة")
    except: st.warning("جاري الاتصال...")

# 2. بوابة الموظفين
elif selected == "بوابة الموظفين":
    if not st.session_state.logged_in:
        # شاشة دخول مركزة في المنتصف
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
            <div style="text-align: center;">
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="100">
                <h3>دخول الكادر التعليمي</h3>
            </div>
            """, unsafe_allow_html=True)
            with st.form("login_modern"):
                u = st.text_input("اسم المستخدم")
                p = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("تسجيل الدخول"):
                    try:
                        db = get_db_connection()
                        users = db.worksheet("Users").get_all_records()
                        df = pd.DataFrame(users)
                        user_found = df[df['Username'].astype(str) == u]
                        if not user_found.empty and check_hashes(p, user_found.iloc[0]['Password']):
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_found.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error("البيانات غير صحيحة")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
    else:
        # لوحة التحكم الداخلية
        role = st.session_state.user_info.get('Role')
        user_name = st.session_state.user_info.get('Username')
        
        st.success(f"أهلاً بك يا {user_name}")

        # نظام التبويبات الحديث
        tab1, tab2, tab3, tab4 = st.tabs(["📝 الواجبات", "📅 الغياب", "⚠️ السلوك", "💯 الدرجات"])
        
        # جلب القوائم مرة واحدة
        try:
            db = get_db_connection()
            students = db.worksheet("Students").get_all_records()
            s_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
            df_st = pd.DataFrame(students)
            c_list = df_st['Class'].unique().tolist() if 'Class' in df_st.columns else []
        except: s_list, c_list = [], []

        with tab1: # الواجبات
            with st.form("hw"):
                cls = st.selectbox("الفصل", c_list)
                sub = st.selectbox("المادة", ["رياضيات", "علوم", "لغتي", "عام"])
                txt = st.text_area("نص الواجب")
                if st.form_submit_button("إرسال الواجب 🚀"):
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    db.worksheet("Homework").append_row([curr_date, cls, sub, txt, user_name])
                    st.success("تم الإرسال!")

        with tab2: # الغياب
            with st.form("att"):
                absent = st.multiselect("اختر الغائبين", s_list)
                if st.form_submit_button("حفظ الغياب"):
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    absent_ids = [s.split(" - ")[0] for s in absent]
                    rows = []
                    for s in s_list:
                        sid, sname = s.split(" - ", 1)
                        stat = "غائب" if sid in absent_ids else "حاضر"
                        rows.append([curr_date, sid, sname, stat, user_name])
                    db.worksheet("Attendance").append_rows(rows)
                    st.success("تم الحفظ!")

        with tab3: # السلوك
            with st.form("beh"):
                s = st.selectbox("الطالب", s_list, key="b")
                t = st.selectbox("النوع", ["مخالفة", "تأخر", "تميز"])
                n = st.text_area("التفاصيل")
                if st.form_submit_button("حفظ"):
                    sid, sname = s.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d")
                    db.worksheet("Behavior_Log").append_row([dt, "", sid, sname, t, n, user_name, "جديد"])
                    st.success("تم!")

        with tab4: # الدرجات
            with st.form("grd"):
                s = st.selectbox("الطالب", s_list, key="g")
                sub = st.selectbox("المادة", ["رياضيات", "علوم"])
                sc = st.number_input("الدرجة", 0, 100)
                if st.form_submit_button("رصد"):
                    sid, sname = s.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d")
                    db.worksheet("Grades").append_row([dt, sid, sname, sub, "اختبار", sc, user_name, ""])
                    st.success("تم!")

# 3. بوابة ولي الأمر
elif selected == "بوابة ولي الأمر":
    st.markdown("### 👨‍👩‍👦 متابعة الطالب")
    
    col_search, col_btn = st.columns([3, 1])
    pid = col_search.text_input("رقم هوية الطالب", placeholder="مثال: 1001")
    search = col_btn.button("🔍 عرض الملف", use_container_width=True)
    
    if search and pid:
        try:
            db = get_db_connection()
            df_s = pd.DataFrame(db.worksheet("Students").get_all_records())
            student = df_s[df_s['Student_ID'].astype(str) == pid]
            
            if not student.empty:
                info = student.iloc[0]
                st.markdown(f"""
                <div style="background: linear-gradient(to left, #6a11cb, #2575fc); padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;">
                    <h2 style="color: white; margin: 0;">{info['Full_Name']}</h2>
                    <p style="margin: 0; opacity: 0.8;">الصف: {info['Class']} | الهوية: {info['Student_ID']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # إحصائيات الطالب السريعة
                c1, c2, c3 = st.columns(3)
                
                # جلب البيانات
                df_g = pd.DataFrame(db.worksheet("Grades").get_all_records())
                my_g = df_g[df_g['Student_ID'].astype(str) == pid] if not df_g.empty else pd.DataFrame()
                
                df_a = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                my_a = df_a[df_a['Student_ID'].astype(str) == pid] if not df_a.empty else pd.DataFrame()
                
                # عرض الأرقام
                avg = pd.to_numeric(my_g['Score'], errors='coerce').mean() if not my_g.empty else 0
                absents = len(my_a[my_a['Status'] == 'غائب']) if not my_a.empty else 0
                
                c1.metric("المعدل العام", f"{avg:.1f}%")
                c2.metric("أيام الغياب", f"{absents}")
                c3.metric("التقدير", "ممتاز" if avg >= 90 else "جيد جداً")
                
                # تفاصيل
                st.markdown("---")
                t1, t2, t3 = st.tabs(["الجدول & الواجبات", "كشف الدرجات", "التواصل"])
                
                with t1:
                    st.write("**الواجبات الأخيرة:**")
                    try:
                        df_hw = pd.DataFrame(db.worksheet("Homework").get_all_records())
                        my_hw = df_hw[df_hw['Class'] == info['Class']]
                        if not my_hw.empty:
                            st.table(my_hw[['Date', 'Subject', 'Content']].tail(5))
                        else: st.info("لا يوجد واجبات")
                    except: pass
                    
                with t2:
                    if not my_g.empty:
                        st.dataframe(my_g[['Subject', 'Score', 'Exam_Type']], use_container_width=True)
                    else: st.info("لا درجات")
                
                with t3:
                    with st.form("msg"):
                        st.text_area("رسالة للمدرسة")
                        st.text_input("رقم الجوال")
                        if st.form_submit_button("إرسال"):
                            st.success("تم الإرسال")
                            
            else:
                st.error("رقم الطالب غير موجود")
        except Exception as e:
            st.error(f"خطأ: {e}")

# 4. صفحة الاستيراد (للمدير)
elif selected == "استيراد بيانات":
    if st.session_state.logged_in and st.session_state.user_info.get('Role') == "مدير":
        st.markdown("### 📥 استيراد الطلاب الجماعي")
        file = st.file_uploader("ملف Excel أو CSV", type=['xlsx', 'csv'])
        if file:
            if st.button("رفع البيانات"):
                try:
                    df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
                    df = df.astype(str)
                    db = get_db_connection()
                    db.worksheet("Students").append_rows(df.values.tolist())
                    st.success(f"تم رفع {len(df)} طالب!")
                except Exception as e: st.error(f"خطأ: {e}")
    else:
        st.warning("يجب تسجيل الدخول كمدير للوصول لهذه الصفحة")
