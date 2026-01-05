import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# ---------------------------------------------------------
# 1. إعداد الصفحة + التصميم الاحترافي
# ---------------------------------------------------------
st.set_page_config(page_title="بوابة المستقبل التعليمية", layout="wide", page_icon="🏫")

# إخفاء عناصر Streamlit غير المرغوبة
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {display: none;}
[data-testid="stToolbar"] {visibility: hidden !important;}
[data-testid="stDecoration"] {visibility: hidden !important;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. تهيئة الذاكرة والدوال
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

def get_db_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# ---------------------------------------------------------
# 3. القائمة الجانبية (Sidebar)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=120)
    st.markdown("### 🏫 بوابة المدرسة الذكية")
    
    menu = ["🏠 الرئيسية / الأخبار", "🔐 بوابة الموظفين", "👨‍👩‍👦 بوابة ولي الأمر"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    if st.session_state.logged_in:
        user_role = st.session_state.user_info.get('Role')
        st.success(f"مرحباً: {st.session_state.user_info.get('Username')}\n({user_role})")
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# ---------------------------------------------------------
# 4. المحتوى الرئيسي
# ---------------------------------------------------------

# --- الصفحة الرئيسية (لوحة الأخبار العامة) ---
if choice == "🏠 الرئيسية / الأخبار":
    st.title("اللوحة الرئيسية للمدرسة 📢")
    
    # 1. عرض الأخبار
    try:
        db = get_db_connection()
        sheet_news = db.worksheet("News")
        news_data = sheet_news.get_all_records()
        df_news = pd.DataFrame(news_data)
        
        if not df_news.empty:
            # عرض آخر الأخبار أولاً
            for index, row in df_news.tail(5).iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;margin-bottom:10px;border-right: 5px solid #ff4b4b;">
                        <h4>📌 {row['Title']}</h4>
                        <p>{row['Content']}</p>
                        <small style="color:grey">✍️ {row['Author']} | 📅 {row['Date']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("لا توجد أخبار جديدة اليوم.")
            
    except:
        st.warning("جاري تحميل الأخبار...")

    # 2. إحصائيات سريعة
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("الفصل الدراسي", "الثاني", "1445هـ")
    col2.metric("حالة النظام", "مفعل ✅")
    try:
        st_count = len(db.worksheet("Students").get_all_values()) - 1
        col3.metric("عدد الطلاب", st_count)
    except:
        pass

# --- بوابة الموظفين (المعلم / المدير) ---
elif choice == "🔐 بوابة الموظفين":
    if not st.session_state.logged_in:
        # شاشة الدخول
        st.markdown("### 🔐 تسجيل دخول الكادر التعليمي والإداري")
        with st.form("login"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
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
                except Exception as e:
                    st.error(f"خطأ اتصال: {e}")
    else:
        # لوحة التحكم
        role = st.session_state.user_info.get('Role')
        user_name = st.session_state.user_info.get('Username')
        
        # --- أدوات المدير (إضافة موظف + نشر خبر) ---
        if role == "مدير":
            with st.expander("👮‍♂️ أدوات المدير (الموظفين + الأخبار)"):
                tab_admin1, tab_admin2 = st.tabs(["إضافة موظف", "نشر خبر عام"])
                
                with tab_admin1:
                    with st.form("add_u"):
                        nu = st.text_input("اسم المستخدم")
                        np = st.text_input("كلمة المرور", type="password")
                        nr = st.selectbox("الصلاحية", ["معلم", "إداري", "مدير"])
                        if st.form_submit_button("إضافة"):
                            if nu and np:
                                db = get_db_connection()
                                db.worksheet("Users").append_row([nu, make_hashes(np), nr, ""])
                                st.success("تم!")
                
                with tab_admin2:
                    with st.form("add_news"):
                        t_title = st.text_input("عنوان الخبر")
                        t_content = st.text_area("نص الخبر")
                        if st.form_submit_button("نشر"):
                            db = get_db_connection()
                            cur_date = datetime.now().strftime("%Y-%m-%d")
                            db.worksheet("News").append_row([cur_date, t_title, t_content, user_name])
                            st.success("تم النشر في الصفحة الرئيسية!")

        # --- أدوات المعلم (حضور، سلوك، درجات) ---
        st.markdown("### 🏫 لوحة الفصول الدراسية")
        
        # جلب الطلاب
        try:
            db = get_db_connection()
            students = db.worksheet("Students").get_all_records()
            student_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
        except:
            student_list = []
        
        tab1, tab2, tab3 = st.tabs(["📅 الحضور والغياب", "📝 السلوك", "💯 الدرجات"])
        
        # 1. الحضور والغياب (جديد!)
        with tab1:
            st.warning("⚠️ يتم تحضير الطلاب لليوم الحالي.")
            with st.form("attendance_form"):
                # نستخدم Multiselect لاختيار الغائبين فقط (أسرع للمعلم)
                absent_students = st.multiselect("اختر الطلاب الغائبين (اترك الباقي للحضور):", student_list)
                att_note = st.text_input("ملاحظات عامة:")
                
                if st.form_submit_button("💾 حفظ الحضور"):
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    att_rows = []
                    
                    # نفصل أرقام الهويات ونجهز البيانات
                    absent_ids = [s.split(" - ")[0] for s in absent_students]
                    
                    for s_str in student_list:
                        sid, sname = s_str.split(" - ", 1)
                        status = "غائب" if sid in absent_ids else "حاضر"
                        # Date | ID | Name | Status | Teacher
                        att_rows.append([curr_date, sid, sname, status, user_name])
                    
                    # الحفظ دفعة واحدة
                    db.worksheet("Attendance").append_rows(att_rows)
                    st.success(f"تم رصد الحضور لـ {len(student_list)} طالب.")

        # 2. السلوك
        with tab2:
            with st.form("beh_form"):
                bs = st.selectbox("الطالب:", student_list, key="b_s")
                bt = st.selectbox("النوع:", ["مخالفة سلوكية", "تأخر صباحي", "غياب حصة", "إشادة وتميز"])
                bn = st.text_area("التفاصيل:")
                if st.form_submit_button("حفظ"):
                    sid, sname = bs.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d")
                    tm = datetime.now().strftime("%H:%M:%S")
                    db.worksheet("Behavior_Log").append_row([dt, tm, sid, sname, bt, bn, user_name, "جديد"])
                    st.success("تم!")

        # 3. الدرجات
        with tab3:
            with st.form("grd_form"):
                gs = st.selectbox("الطالب:", student_list, key="g_s")
                gsub = st.selectbox("المادة:", ["رياضيات", "لغة عربية", "علوم", "إنجليزي"])
                gex = st.selectbox("التقييم:", ["اختبار 1", "اختبار 2", "مشاركة", "نهائي"])
                gsc = st.number_input("الدرجة:", 0, 100)
                if st.form_submit_button("رصد"):
                    sid, sname = gs.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d")
                    db.worksheet("Grades").append_row([dt, sid, sname, gsub, gex, gsc, user_name, ""])
                    st.success("تم!")

# --- بوابة ولي الأمر ---
elif choice == "👨‍👩‍👦 بوابة ولي الأمر":
    st.markdown("### 👨‍👩‍👦 متابعة ولي الأمر")
    
    col_p1, col_p2 = st.columns([3,1])
    p_id = col_p1.text_input("رقم هوية الطالب:")
    p_btn = col_p2.button("عرض الملف")
    
    if p_btn and p_id:
        try:
            db = get_db_connection()
            # 1. بحث الطالب
            df_s = pd.DataFrame(db.worksheet("Students").get_all_records())
            student = df_s[df_s['Student_ID'].astype(str) == p_id]
            
            if not student.empty:
                s_name = student.iloc[0]['Full_Name']
                st.success(f"ملف الطالب: {s_name}")
                
                tab_p1, tab_p2, tab_p3 = st.tabs(["📊 التقرير الأكاديمي", "📅 سجل الحضور", "📩 التواصل"])
                
                # تقرير الدرجات
                with tab_p1:
                    df_g = pd.DataFrame(db.worksheet("Grades").get_all_records())
                    if not df_g.empty:
                        my_g = df_g[df_g['Student_ID'].astype(str) == p_id]
                        if not my_g.empty:
                            st.table(my_g[['Subject', 'Exam_Type', 'Score', 'Date']])
                        else:
                            st.info("لا توجد درجات.")
                
                # سجل الحضور (جديد!)
                with tab_p2:
                    df_a = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                    if not df_a.empty:
                        my_a = df_a[df_a['Student_ID'].astype(str) == p_id]
                        # نحسب نسبة الغياب
                        total_days = len(my_a)
                        absent_days = len(my_a[my_a['Status'] == 'غائب'])
                        
                        col_a1, col_a2 = st.columns(2)
                        col_a1.metric("إجمالي الأيام", total_days)
                        col_a2.metric("أيام الغياب", absent_days, delta_color="inverse")
                        
                        st.dataframe(my_a[['Date', 'Status', 'Teacher']], hide_index=True)
                    else:
                        st.info("لم يتم رصد حضور بعد.")

                # التواصل
                with tab_p3:
                    with st.form("msg_p"):
                        ph = st.text_input("رقم جوالك:")
                        txt = st.text_area("رسالتك:")
                        if st.form_submit_button("إرسال"):
                            dt = datetime.now().strftime("%Y-%m-%d")
                            db.worksheet("Messages").append_row([dt, s_name, ph, txt, "جديد"])
                            st.success("وصلت رسالتك للإدارة!")
            else:
                st.error("رقم الطالب غير صحيح")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
