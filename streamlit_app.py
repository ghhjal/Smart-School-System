import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# ---------------------------------------------------------
# 1. إعداد الصفحة + كود الإخفاء (اللمسة السحرية) ✨
# ---------------------------------------------------------
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# كود CSS لإخفاء القوائم، الفوتر، والشريط العلوي وزر Deploy
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
# 2. تهيئة الذاكرة (Session State)
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# ---------------------------------------------------------
# 3. دوال مساعدة (تشفير + اتصال)
# ---------------------------------------------------------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

def get_db_connection():
    # تحديد الصلاحيات المطلوبة
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # جلب المفاتيح من إعدادات Streamlit السرية
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# ---------------------------------------------------------
# 4. القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
    st.title("نظام الإدارة المدرسية")
    
    menu = ["🏠 الرئيسية", "🔐 بوابة الموظفين", "🔍 بحث عن طالب"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    # زر تسجيل الخروج
    if st.session_state.logged_in:
        st.write(f"👤 مرحباً: {st.session_state.user_info.get('Username')}")
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# ---------------------------------------------------------
# 5. المحتوى الرئيسي
# ---------------------------------------------------------

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.info("نظام سحابي متكامل لربط الإدارة بالمعلمين وأولياء الأمور.")
    
    # محاولة عرض إحصائية سريعة لعدد الطلاب
    try:
        db = get_db_connection()
        sheet_students = db.worksheet("Students")
        # حساب عدد الصفوف ناقص صف العناوين
        count_students = len(sheet_students.get_all_values()) - 1 
        st.metric("عدد الطلاب المسجلين", count_students)
    except:
        pass

elif choice == "🔐 بوابة الموظفين":
    # --- أ) شاشة تسجيل الدخول ---
    if not st.session_state.logged_in:
        st.header("تسجيل دخول الموظفين")
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submit_login = st.form_submit_button("دخول")
            
            if submit_login:
                try:
                    db = get_db_connection()
                    sheet = db.worksheet("Users")
                    users = sheet.get_all_records()
                    df_users = pd.DataFrame(users)
                    
                    # البحث عن المستخدم
                    user_found = df_users[df_users['Username'].astype(str) == username]
                    
                    if not user_found.empty:
                        stored_password = user_found.iloc[0]['Password']
                        # التحقق من الهاش
                        if check_hashes(password, stored_password):
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_found.iloc[0].to_dict()
                            st.success("تم الدخول بنجاح!")
                            st.rerun()
                        else:
                            st.error("كلمة المرور غير صحيحة")
                    else:
                        st.error("اسم المستخدم غير موجود")
                except Exception as e:
                    st.error(f"حدث خطأ في الاتصال: {e}")

    # --- ب) لوحة التحكم (بعد الدخول) ---
    else:
        user_name = st.session_state.user_info.get('Username')
        role = st.session_state.user_info.get('Role')
        
        # -------------------------------------------
        #  🔥 ميزة المدير: إضافة موظفين
        # -------------------------------------------
        if role == "مدير":
            with st.expander("👮‍♂️ لوحة تحكم المدير (إضافة موظفين)", expanded=False):
                st.warning("هذه المنطقة خاصة بالمدير فقط.")
                with st.form("add_user_form"):
                    c1, c2 = st.columns(2)
                    new_u = c1.text_input("اسم المستخدم الجديد:")
                    new_p = c2.text_input("كلمة المرور:", type="password")
                    c3, c4 = st.columns(2)
                    new_r = c3.selectbox("الصلاحية:", ["معلم", "إداري", "مدير"])
                    new_id = c4.text_input("الرقم الوظيفي (اختياري):")
                    
                    if st.form_submit_button("➕ إضافة"):
                        if new_u and new_p:
                            try:
                                db = get_db_connection()
                                hashed = make_hashes(new_p)
                                db.worksheet("Users").append_row([new_u, hashed, new_r, new_id])
                                st.success(f"تمت إضافة {new_u} بنجاح!")
                            except Exception as e:
                                st.error(f"خطأ: {e}")
            st.markdown("---")

        # -------------------------------------------
        #  لوحة الإحصائيات
        # -------------------------------------------
        st.success(f"أهلاً بك: {user_name} ({role})")
        
        try:
            db = get_db_connection()
            sheet_log = db.worksheet("Behavior_Log")
            all_records = sheet_log.get_all_records()
            df_stats = pd.DataFrame(all_records)
            
            if not df_stats.empty:
                col1, col2, col3 = st.columns(3)
                col1.metric("إجمالي الملاحظات", len(df_stats))
                with col2:
                    st.bar_chart(df_stats['Type'].value_counts())
                with col3:
                    st.caption("آخر النشاطات")
                    st.dataframe(df_stats[['Student_Name', 'Type']].tail(3), hide_index=True)
        except:
            pass # تخطي الإحصائيات في حال عدم وجود بيانات

        st.markdown("---")

        # -------------------------------------------
        #  نظام التبويبات (سلوك / درجات)
        # -------------------------------------------
        tab1, tab2 = st.tabs(["📝 رصد السلوك", "💯 رصد الدرجات"])
        
        # جلب قائمة الطلاب
        try:
            sheet_students = db.worksheet("Students")
            students_data = sheet_students.get_all_records()
            student_options = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students_data]
        except:
            student_options = []

        # تبويب 1: السلوك
        with tab1:
            with st.form("behavior_form"):
                b_student = st.selectbox("الطالب:", student_options)
                b_type = st.selectbox("النوع:", ["مخالفة سلوكية", "تأخر صباحي", "غياب حصة", "إشادة وتميز"])
                b_note = st.text_area("التفاصيل:")
                
                if st.form_submit_button("💾 حفظ السلوك"):
                    s_id, s_name = b_student.split(" - ", 1)
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    curr_time = datetime.now().strftime("%H:%M:%S")
                    # Date, Time, ID, Name, Type, Note, Teacher, Status
                    row = [curr_date, curr_time, s_id, s_name, b_type, b_note, user_name, "جديد"]
                    
                    db.worksheet("Behavior_Log").append_row(row)
                    st.success("تم الحفظ!")
                    st.rerun()

        # تبويب 2: الدرجات
        with tab2:
            with st.form("grades_form"):
                g_student = st.selectbox("الطالب (درجات):", student_options)
                g_subject = st.selectbox("المادة:", ["رياضيات", "لغة عربية", "علوم", "إنجليزي", "فقه"])
                g_exam = st.selectbox("نوع التقييم:", ["اختبار شهري", "اختبار نهائي", "مشاركة", "واجبات"])
                g_score = st.number_input("الدرجة:", 0, 100)
                g_note = st.text_input("ملاحظة:")
                
                if st.form_submit_button("📤 رصد الدرجة"):
                    s_id, s_name = g_student.split(" - ", 1)
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    # Date, ID, Name, Subject, Exam, Score, Teacher, Notes
                    row = [curr_date, s_id, s_name, g_subject, g_exam, g_score, user_name, g_note]
                    
                    db.worksheet("Grades").append_row(row)
                    st.success("تم الرصد!")

elif choice == "🔍 بحث عن طالب":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id_input = st.text_input("أدخل رقم هوية الطالب:")
    
    if st.button("بحث"):
        try:
            db = get_db_connection()
            sheet_students = db.worksheet("Students")
            df_st = pd.DataFrame(sheet_students.get_all_records())
            
            # البحث
            student_info = df_st[df_st['Student_ID'].astype(str) == str(student_id_input)]
            
            if not student_info.empty:
                st.subheader(f"الطالب: {student_info.iloc[0]['Full_Name']}")
                st.table(student_info)
                
                # تبويبات النتائج
                res_tab1, res_tab2 = st.tabs(["📂 سجل السلوك", "📊 كشف الدرجات"])
                
                with res_tab1:
                    sheet_log = db.worksheet("Behavior_Log")
                    df_logs = pd.DataFrame(sheet_log.get_all_records())
                    if not df_logs.empty:
                        s_logs = df_logs[df_logs['Student_ID'].astype(str) == str(student_id_input)]
                        if not s_logs.empty:
                            st.table(s_logs[['Date', 'Type', 'Note', 'Teacher']])
                        else:
                            st.info("سجل السلوك نظيف.")
                    else:
                        st.info("لا توجد بيانات.")

                with res_tab2:
                    sheet_grades = db.worksheet("Grades")
                    df_grades = pd.DataFrame(sheet_grades.get_all_records())
                    if not df_grades.empty:
                        s_grades = df_grades[df_grades['Student_ID'].astype(str) == str(student_id_input)]
                        if not s_grades.empty:
                            st.dataframe(s_grades[['Subject', 'Exam_Type', 'Score', 'Date']])
                        else:
                            st.info("لم يتم رصد درجات بعد.")
                    else:
                        st.info("لا توجد درجات.")
            else:
                st.warning("رقم الطالب غير صحيح.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
