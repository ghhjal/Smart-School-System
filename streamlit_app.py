import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime
from streamlit_option_menu import option_menu

# ---------------------------------------------------------
# 1. إعداد الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="نظام مدرستي الذكي",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. تصميم CSS (Modern UI) - تحسينات بصرية
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }
    
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* إخفاء عناصر ستريم ليت */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    
    /* تصميم البطاقات */
    div.css-1r6slb0, div.stForm {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* تحسين الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
    }
    
    /* رسائل النجاح والخطأ */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الدوال والاتصال
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
# 4. القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
    st.markdown("<h3 style='text-align: center; color: #444;'>بوابة المستقبل</h3>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["الرئيسية", "بوابة الموظفين", "ولي الأمر"],
        icons=["house", "briefcase", "people"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#667eea", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "right", "margin":"5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )
    
    st.markdown("---")
    if st.session_state.logged_in:
        user = st.session_state.user_info.get('Username')
        role = st.session_state.user_info.get('Role')
        st.info(f"👤 {user} | {role}")
        if st.button("تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# ---------------------------------------------------------
# 5. المحتوى الرئيسي
# ---------------------------------------------------------

# --- الصفحة الرئيسية ---
if selected == "الرئيسية":
    st.markdown("### 📊 لوحة المعلومات")
    
    # إحصائيات سريعة
    c1, c2, c3, c4 = st.columns(4)
    try:
        db = get_db_connection()
        st_cnt = len(db.worksheet("Students").get_all_values()) - 1
    except: st_cnt = 0
    
    c1.metric("الطلاب", st_cnt)
    c2.metric("الفصل الدراسي", "2")
    c3.metric("السنة", "1445")
    c4.metric("النظام", "Active ✅")
    
    st.markdown("---")
    st.subheader("📢 آخر الأخبار")
    try:
        news = db.worksheet("News").get_all_records()
        df_news = pd.DataFrame(news)
        if not df_news.empty:
            for i, row in df_news.tail(3).iloc[::-1].iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-right: 4px solid #764ba2;">
                    <h4 style="margin:0; color: #2c3e50;">{row['Title']}</h4>
                    <p style="color: #555; margin-top: 5px;">{row['Content']}</p>
                    <small style="color: #888;">{row['Date']} | {row['Author']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد أخبار حالياً.")
    except: st.warning("جاري التحميل...")

# --- بوابة الموظفين (تم إصلاح الفصل بين المدير والمعلم) ---
elif selected == "بوابة الموظفين":
    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("### 🔐 الدخول للنظام")
            with st.form("login_form"):
                u = st.text_input("اسم المستخدم")
                p = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("دخول", use_container_width=True):
                    try:
                        db = get_db_connection()
                        users = db.worksheet("Users").get_all_records()
                        df = pd.DataFrame(users)
                        user = df[df['Username'].astype(str) == u]
                        if not user.empty and check_hashes(p, user.iloc[0]['Password']):
                            st.session_state.logged_in = True
                            st.session_state.user_info = user.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error("بيانات خاطئة")
                    except Exception as e: st.error(f"خطأ: {e}")
    else:
        # هنا يبدأ المنطق المصحح
        role = st.session_state.user_info.get('Role')
        user_name = st.session_state.user_info.get('Username')
        
        st.success(f"مرحباً بك: {user_name}")

        # 🅰️ إذا كان المستخدم مديراً (Admin View)
        if role == "مدير":
            st.markdown("### 👮‍♂️ لوحة تحكم المدير")
            
            # تبويبات المدير الخاصة
            tab1, tab2, tab3 = st.tabs(["👥 إدارة المستخدمين", "📢 نشر الأخبار", "📥 استيراد طلاب"])
            
            with tab1:
                st.write("إضافة موظف جديد للنظام:")
                with st.form("add_user"):
                    c1, c2 = st.columns(2)
                    nu = c1.text_input("اسم المستخدم")
                    np = c2.text_input("كلمة المرور", type="password")
                    nr = st.selectbox("الصلاحية", ["معلم", "مدير", "إداري"])
                    if st.form_submit_button("إضافة المستخدم"):
                        try:
                            db = get_db_connection()
                            db.worksheet("Users").append_row([nu, make_hashes(np), nr, ""])
                            st.success(f"تم إضافة {nu} بنجاح!")
                        except Exception as e: st.error(f"خطأ: {e}")

            with tab2:
                st.write("نشر خبر جديد في الصفحة الرئيسية:")
                with st.form("add_news"):
                    nt = st.text_input("عنوان الخبر")
                    nc = st.text_area("نص الخبر")
                    if st.form_submit_button("نشر"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db = get_db_connection()
                        db.worksheet("News").append_row([dt, nt, nc, user_name])
                        st.success("تم النشر!")

            with tab3:
                st.write("رفع بيانات الطلاب دفعة واحدة (Excel/CSV):")
                up_file = st.file_uploader("اختر الملف", type=['xlsx', 'csv'])
                if up_file:
                    if st.button("بدء الاستيراد"):
                        try:
                            if up_file.name.endswith('csv'):
                                df = pd.read_csv(up_file)
                            else:
                                df = pd.read_excel(up_file)
                            
                            df = df.astype(str)
                            db = get_db_connection()
                            db.worksheet("Students").append_rows(df.values.tolist())
                            st.success(f"تم استيراد {len(df)} طالب بنجاح!")
                        except Exception as e: st.error(f"خطأ في الملف: {e}")

        # 🅱️ إذا كان المستخدم معلماً (Teacher View)
        else:
            st.markdown("### 🏫 المهام الأكاديمية")
            
            # جلب القوائم
            try:
                db = get_db_connection()
                students = db.worksheet("Students").get_all_records()
                s_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
                df_st = pd.DataFrame(students)
                c_list = df_st['Class'].unique().tolist() if 'Class' in df_st.columns else []
            except: s_list, c_list = [], []

            tab1, tab2, tab3, tab4 = st.tabs(["📝 الواجبات", "📅 الغياب", "⚠️ السلوك", "💯 الدرجات"])

            with tab1: # واجبات
                with st.form("hw"):
                    cls = st.selectbox("الفصل الدراسي", c_list)
                    sub = st.selectbox("المادة", ["رياضيات", "علوم", "لغتي", "فقه", "إنجليزي"])
                    txt = st.text_area("تفاصيل الواجب")
                    if st.form_submit_button("إرسال للفصل"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db.worksheet("Homework").append_row([dt, cls, sub, txt, user_name])
                        st.success("تم!")

            with tab2: # غياب
                with st.form("att"):
                    st.write("حدد الطلاب **الغائبين** فقط:")
                    absent = st.multiselect("", s_list)
                    if st.form_submit_button("حفظ الغياب"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        absent_ids = [s.split(" - ")[0] for s in absent]
                        rows = []
                        for s in s_list:
                            sid, sname = s.split(" - ", 1)
                            stat = "غائب" if sid in absent_ids else "حاضر"
                            rows.append([dt, sid, sname, stat, user_name])
                        db.worksheet("Attendance").append_rows(rows)
                        st.success("تم الحفظ!")

            with tab3: # سلوك
                with st.form("beh"):
                    s = st.selectbox("الطالب", s_list)
                    t = st.selectbox("النوع", ["مخالفة", "تأخر", "إشادة"])
                    n = st.text_area("الملاحظة")
                    if st.form_submit_button("حفظ"):
                        sid, sname = s.split(" - ", 1)
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db.worksheet("Behavior_Log").append_row([dt, "", sid, sname, t, n, user_name, "جديد"])
                        st.success("تم!")

            with tab4: # درجات
                with st.form("grd"):
                    s = st.selectbox("الطالب", s_list, key="g")
                    sub = st.selectbox("المادة", ["رياضيات", "علوم", "لغتي"])
                    sc = st.number_input("الدرجة", 0, 100)
                    if st.form_submit_button("رصد"):
                        sid, sname = s.split(" - ", 1)
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db.worksheet("Grades").append_row([dt, sid, sname, sub, "اختبار", sc, user_name, ""])
                        st.success("تم!")

# --- بوابة ولي الأمر ---
elif selected == "ولي الأمر":
    st.markdown("### 👨‍👩‍👦 متابعة الأبناء")
    
    col1, col2 = st.columns([3,1])
    pid = col1.text_input("رقم الهوية / الأكاديمي")
    btn = col2.button("بحث 🔍", use_container_width=True)
    
    if btn and pid:
        try:
            db = get_db_connection()
            df = pd.DataFrame(db.worksheet("Students").get_all_records())
            st_info = df[df['Student_ID'].astype(str) == pid]
            
            if not st_info.empty:
                info = st_info.iloc[0]
                st.success(f"الطالب: {info['Full_Name']} | الصف: {info['Class']}")
                
                # إحصائيات سريعة
                t1, t2, t3 = st.tabs(["📊 الدرجات", "📅 الغياب", "📩 التواصل"])
                
                with t1:
                    df_g = pd.DataFrame(db.worksheet("Grades").get_all_records())
                    my_g = df_g[df_g['Student_ID'].astype(str) == pid] if not df_g.empty else pd.DataFrame()
                    if not my_g.empty:
                        st.dataframe(my_g[['Subject', 'Score', 'Exam_Type']], use_container_width=True)
                    else: st.info("لا توجد درجات")
                
                with t2:
                    df_a = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                    my_a = df_a[df_a['Student_ID'].astype(str) == pid] if not df_a.empty else pd.DataFrame()
                    if not my_a.empty:
                        absents = len(my_a[my_a['Status'] == 'غائب'])
                        st.metric("عدد أيام الغياب", absents)
                        st.dataframe(my_a[['Date', 'Status']], use_container_width=True)
                    else: st.info("لا يوجد غياب")
                
                with t3:
                    with st.form("msg"):
                        ph = st.text_input("رقم الجوال")
                        msg = st.text_area("الرسالة للإدارة")
                        if st.form_submit_button("إرسال"):
                            dt = datetime.now().strftime("%Y-%m-%d")
                            db.worksheet("Messages").append_row([dt, info['Full_Name'], ph, msg, "جديد"])
                            st.success("تم الإرسال")
            else:
                st.error("الرقم غير صحيح")
        except Exception as e: st.error(f"خطأ: {e}")
