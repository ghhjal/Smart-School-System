import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# ---------------------------------------------------------
# 1. إعداد الصفحة + التصميم
# ---------------------------------------------------------
st.set_page_config(page_title="بوابة المستقبل التعليمية", layout="wide", page_icon="🏫")

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
# 3. القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=120)
    st.markdown("### 🏫 بوابة المدرسة الذكية")
    
    menu = ["🏠 الرئيسية", "🔐 بوابة الموظفين", "👨‍👩‍👦 بوابة ولي الأمر"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    if st.session_state.logged_in:
        role = st.session_state.user_info.get('Role')
        st.success(f"مرحباً: {st.session_state.user_info.get('Username')} ({role})")
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# ---------------------------------------------------------
# 4. المحتوى الرئيسي
# ---------------------------------------------------------

# --- الصفحة الرئيسية ---
if choice == "🏠 الرئيسية":
    st.title("اللوحة الرئيسية للمدرسة 📢")
    
    col_main1, col_main2 = st.columns([2, 1])
    
    with col_main1:
        st.subheader("📰 آخر الأخبار والإعلانات")
        try:
            db = get_db_connection()
            sheet_news = db.worksheet("News")
            news_data = sheet_news.get_all_records()
            df_news = pd.DataFrame(news_data)
            
            if not df_news.empty:
                for index, row in df_news.tail(3).iloc[::-1].iterrows():
                    st.info(f"📌 **{row['Title']}**\n\n{row['Content']}\n\nStart -- *{row['Author']} | {row['Date']}*")
            else:
                st.write("لا توجد أخبار جديدة.")
        except:
            st.warning("جاري تحميل الأخبار...")

    with col_main2:
        st.subheader("🏆 لوحة الشرف (TOP 5)")
        try:
            # حساب الأوائل تلقائياً من الدرجات
            sheet_grades = db.worksheet("Grades")
            df_grades = pd.DataFrame(sheet_grades.get_all_records())
            
            if not df_grades.empty:
                # تجميع الدرجات لكل طالب
                # نحول Score لرقم لضمان الجمع الصحيح
                df_grades['Score'] = pd.to_numeric(df_grades['Score'], errors='coerce')
                leaderboard = df_grades.groupby('Student_Name')['Score'].sum().reset_index()
                leaderboard = leaderboard.sort_values(by='Score', ascending=False).head(5)
                
                # عرض جدول بسيط وأنيق
                st.dataframe(leaderboard, hide_index=True, use_container_width=True)
                st.caption("يتم التحديث تلقائياً بناءً على مجموع الدرجات المرصودة.")
            else:
                st.write("بانتظار رصد الدرجات...")
        except:
            st.write("لا توجد بيانات كافية.")

    st.markdown("---")
    # إحصائيات سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("الفصل الدراسي", "الثاني")
    try:
        st_count = len(db.worksheet("Students").get_all_values()) - 1
        c2.metric("عدد الطلاب", st_count)
    except:
        pass
    c3.metric("حالة النظام", "متصل ✅")


# --- بوابة الموظفين ---
elif choice == "🔐 بوابة الموظفين":
    if not st.session_state.logged_in:
        st.markdown("### 🔐 تسجيل دخول الكادر")
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
        role = st.session_state.user_info.get('Role')
        user_name = st.session_state.user_info.get('Username')
        
        # --- أدوات المدير ---
        if role == "مدير":
            with st.expander("👮‍♂️ أدوات المدير"):
                tab_a1, tab_a2 = st.tabs(["إضافة موظف", "نشر خبر"])
                with tab_a1:
                    with st.form("add_u"):
                        nu = st.text_input("اسم المستخدم")
                        np = st.text_input("كلمة المرور", type="password")
                        nr = st.selectbox("الصلاحية", ["معلم", "إداري", "مدير"])
                        if st.form_submit_button("إضافة"):
                            db = get_db_connection()
                            db.worksheet("Users").append_row([nu, make_hashes(np), nr, ""])
                            st.success("تم!")
                with tab_a2:
                    with st.form("add_n"):
                        nt = st.text_input("العنوان")
                        nc = st.text_area("المحتوى")
                        if st.form_submit_button("نشر"):
                            dt = datetime.now().strftime("%Y-%m-%d")
                            db = get_db_connection()
                            db.worksheet("News").append_row([dt, nt, nc, user_name])
                            st.success("تم النشر!")

        # --- أدوات المعلم (الكل في واحد) ---
        st.markdown("### 🏫 المهام اليومية")
        
        try:
            db = get_db_connection()
            students = db.worksheet("Students").get_all_records()
            student_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
            # استخراج قائمة الفصول الموجودة لتسهيل اختيار الفصل للواجبات
            df_st = pd.DataFrame(students)
            class_list = df_st['Class'].unique().tolist() if 'Class' in df_st.columns else ["أول/1", "أول/2", "أول/3"]
        except:
            student_list = []
            class_list = []

        # التبويبات الشاملة
        tab1, tab2, tab3, tab4 = st.tabs(["📝 الواجبات (جديد)", "📅 الحضور", "⚠️ السلوك", "💯 الدرجات"])

        # 1. الواجبات المنزلية
        with tab1:
            st.subheader("إرسال واجب يومي للفصل")
            with st.form("hw_form"):
                hw_class = st.selectbox("اختر الفصل:", class_list)
                hw_subject = st.selectbox("المادة:", ["رياضيات", "لغة عربية", "علوم", "إنجليزي", "فقه", "عام"])
                hw_content = st.text_area("نص الواجب المطلوب:")
                
                if st.form_submit_button("🚀 إرسال الواجب"):
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    # Date | Class | Subject | Content | Teacher
                    db.worksheet("Homework").append_row([curr_date, hw_class, hw_subject, hw_content, user_name])
                    st.success(f"تم إرسال الواجب لطلاب فصل {hw_class}")

        # 2. الحضور
        with tab2:
            st.subheader("رصد الغياب اليومي")
            with st.form("att_form"):
                absent_students = st.multiselect("حدد الغائبين:", student_list)
                if st.form_submit_button("حفظ الغياب"):
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    absent_ids = [s.split(" - ")[0] for s in absent_students]
                    rows = []
                    for s in student_list:
                        sid, sname = s.split(" - ", 1)
                        stat = "غائب" if sid in absent_ids else "حاضر"
                        rows.append([curr_date, sid, sname, stat, user_name])
                    db.worksheet("Attendance").append_rows(rows)
                    st.success("تم الحفظ.")

        # 3. السلوك
        with tab3:
            with st.form("beh_form"):
                bs = st.selectbox("الطالب:", student_list)
                bt = st.selectbox("النوع:", ["مخالفة", "تأخر", "إشادة"])
                bn = st.text_area("التفاصيل:")
                if st.form_submit_button("حفظ"):
                    sid, sname = bs.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                    db.worksheet("Behavior_Log").append_row([dt.split()[0], dt.split()[1], sid, sname, bt, bn, user_name, "جديد"])
                    st.success("تم.")

        # 4. الدرجات
        with tab4:
            with st.form("grd_form"):
                gs = st.selectbox("الطالب:", student_list, key="gs")
                gsub = st.selectbox("المادة:", ["رياضيات", "علوم", "عربي", "إنجليزي"])
                gtype = st.selectbox("النوع:", ["مشاركة", "اختبار شهري", "نهائي"])
                gscore = st.number_input("الدرجة:", 0, 100)
                if st.form_submit_button("رصد"):
                    sid, sname = gs.split(" - ", 1)
                    dt = datetime.now().strftime("%Y-%m-%d")
                    db.worksheet("Grades").append_row([dt, sid, sname, gsub, gtype, gscore, user_name, ""])
                    st.success("تم.")


# --- بوابة ولي الأمر ---
elif choice == "👨‍👩‍👦 بوابة ولي الأمر":
    st.markdown("### 👨‍👩‍👦 متابعة ابني/ابنتي")
    
    col_p1, col_p2 = st.columns([3, 1])
    pid = col_p1.text_input("أدخل هوية الطالب:")
    pbtn = col_p2.button("عرض الملف الشامل")
    
    if pbtn and pid:
        try:
            db = get_db_connection()
            # جلب بيانات الطالب
            df_s = pd.DataFrame(db.worksheet("Students").get_all_records())
            student = df_s[df_s['Student_ID'].astype(str) == pid]
            
            if not student.empty:
                s_name = student.iloc[0]['Full_Name']
                s_class = student.iloc[0]['Class'] # جلب الفصل لعرض الواجبات والجدول
                
                st.success(f"الطالب: {s_name} | الفصل: {s_class}")
                
                # التبويبات الشاملة لولي الأمر
                t1, t2, t3, t4, t5 = st.tabs(["🗓️ الجدول الدراسي", "📝 الواجبات", "📊 التقرير", "📅 الحضور", "📩 التواصل"])
                
                # 1. الجدول الدراسي
                with t1:
                    try:
                        df_sch = pd.DataFrame(db.worksheet("Schedule").get_all_records())
                        # البحث عن جدول فصل الطالب
                        my_sch = df_sch[df_sch['Class'] == s_class]
                        if not my_sch.empty:
                            st.table(my_sch)
                        else:
                            st.info("لم يتم رفع جدول لهذا الفصل بعد.")
                    except:
                        st.warning("صفحة Schedule غير موجودة أو فارغة.")

                # 2. الواجبات المنزلية
                with t2:
                    try:
                        df_hw = pd.DataFrame(db.worksheet("Homework").get_all_records())
                        # تصفية الواجبات لفصل الطالب
                        my_hw = df_hw[df_hw['Class'] == s_class]
                        if not my_hw.empty:
                            # عرض أحدث 5 واجبات
                            st.table(my_hw[['Date', 'Subject', 'Content']].tail(5))
                        else:
                            st.info("لا توجد واجبات مسجلة لهذا الفصل.")
                    except:
                        st.warning("صفحة Homework غير موجودة.")

                # 3. التقرير والدرجات
                with t3:
                    df_g = pd.DataFrame(db.worksheet("Grades").get_all_records())
                    if not df_g.empty:
                        my_g = df_g[df_g['Student_ID'].astype(str) == pid]
                        if not my_g.empty:
                            # حساب المعدل
                            avg = pd.to_numeric(my_g['Score'], errors='coerce').mean()
                            st.metric("المعدل العام", f"{avg:.1f}%")
                            st.dataframe(my_g[['Subject', 'Exam_Type', 'Score', 'Date']], hide_index=True)
                        else:
                            st.info("لا توجد درجات.")
                
                # 4. سجل الحضور
                with t4:
                    df_a = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                    if not df_a.empty:
                        my_a = df_a[df_a['Student_ID'].astype(str) == pid]
                        absent_days = len(my_a[my_a['Status'] == 'غائب'])
                        st.metric("أيام الغياب", absent_days)
                        st.dataframe(my_a[['Date', 'Status']], hide_index=True)
                
                # 5. التواصل
                with t5:
                    with st.form("msg_p"):
                        ph = st.text_input("رقم الجوال:")
                        msg = st.text_area("الرسالة:")
                        if st.form_submit_button("إرسال"):
                            db.worksheet("Messages").append_row([datetime.now().strftime("%Y-%m-%d"), s_name, ph, msg, "جديد"])
                            st.success("تم الإرسال.")

            else:
                st.error("رقم الطالب غير صحيح.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
