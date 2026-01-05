import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")
# --- إخفاء العلامات المائية، القوائم، وزر النشر (Deploy) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display: none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {visibility: hidden !important;}
            [data-testid="stHeader"] {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# --- 2. تهيئة الذاكرة ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# --- 3. دوال مساعدة ---
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

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
    st.title("نظام الإدارة المدرسية")
    
    menu = ["🏠 الرئيسية", "🔐 بوابة الموظفين", "🔍 بحث عن طالب"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    if st.session_state.logged_in:
        st.write(f"مرحباً: {st.session_state.user_info.get('Username')}")
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

# --- 5. المحتوى الرئيسي ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.info("نظام متكامل لربط الإدارة بالمعلمين وأولياء الأمور.")
    
    # عرض سريع للإحصائيات العامة (للجميع)
    try:
        db = get_db_connection()
        count_students = len(db.worksheet("Students").get_all_values()) - 1 # خصم صف العناوين
        st.metric("عدد الطلاب المسجلين", count_students)
    except:
        pass

elif choice == "🔐 بوابة الموظفين":
    if not st.session_state.logged_in:
        # --- شاشة تسجيل الدخول ---
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
                    user_found = df_users[df_users['Username'].astype(str) == username]
                    
                    if not user_found.empty:
                        stored_password = user_found.iloc[0]['Password']
                        if check_hashes(password, stored_password):
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_found.iloc[0].to_dict()
                            st.success("تم الدخول بنجاح!")
                            st.rerun()
                        else:
                            st.error("كلمة المرور غير صحيحة")
                    else:
                        st.error("المستخدم غير موجود")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
    else:
        # --- لوحة التحكم (بعد الدخول) ---
        user_name = st.session_state.user_info.get('Username')
        role = st.session_state.user_info.get('Role')
        
        # ---------------------------------------------------------
        #  🔥 ميزة المدير الخاصة (إضافة موظفين)
        # ---------------------------------------------------------
        if role == "مدير":
            with st.expander("👮‍♂️ لوحة تحكم المدير (إضافة موظفين)", expanded=False):
                st.warning("هذه المنطقة خاصة بالمدير فقط لإضافة معلمين جدد.")
                with st.form("add_user_form"):
                    col_u1, col_u2 = st.columns(2)
                    new_user = col_u1.text_input("اسم المستخدم الجديد:")
                    new_pass = col_u2.text_input("كلمة المرور:", type="password")
                    
                    col_u3, col_u4 = st.columns(2)
                    new_role = col_u3.selectbox("الصلاحية:", ["معلم", "إداري", "مدير"])
                    new_related_id = col_u4.text_input("الرقم الوظيفي (اختياري):")
                    
                    submit_add_user = st.form_submit_button("➕ إضافة المستخدم للنظام")
                    
                    if submit_add_user and new_user and new_pass:
                        try:
                            db = get_db_connection()
                            hashed_pass = make_hashes(new_pass)
                            # الترتيب في جوجل شيت: Username, Password, Role, Related_ID
                            db.worksheet("Users").append_row([new_user, hashed_pass, new_role, new_related_id])
                            st.success(f"تم إنشاء حساب للموظف {new_user} بنجاح!")
                        except Exception as e:
                            st.error(f"خطأ: {e}")
            st.markdown("---")

        # ---------------------------------------------------------
        #  باقي اللوحة (الإحصائيات والتبويبات)
        # ---------------------------------------------------------
        st.success(f"أهلاً بك: {user_name} ({role})")
        
        # قسم الإحصائيات
        try:
            db = get_db_connection()
            sheet_log = db.worksheet("Behavior_Log")
            all_records = sheet_log.get_all_records()
            df_stats = pd.DataFrame(all_records)
            if not df_stats.empty:
                col1, col2, col3 = st.columns(3)
                col1.metric("حالات السلوك", len(df_stats))
                with col2:
                    st.bar_chart(df_stats['Type'].value_counts())
                with col3:
                    st.dataframe(df_stats[['Student_Name', 'Type']].tail(3), hide_index=True)
        except:
            pass
            
        st.markdown("---")
        
        # التبويبات (سلوك / درجات)
        tab1, tab2 = st.tabs(["📝 رصد السلوك", "💯 رصد الدرجات"])
        
        try:
            sheet_students = db.worksheet("Students")
            students_data = sheet_students.get_all_records()
            student_options = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students_data]
        except:
            student_options = []

        with tab1:
            with st.form("behavior_form"):
                b_student = st.selectbox("الطالب:", student_options)
                b_type = st.selectbox("نوع الملاحظة:", ["مخالفة سلوكية", "تأخر صباحي", "غياب حصة", "إشادة وتميز"])
                b_note = st.text_area("التفاصيل:")
                if st.form_submit_button("💾 حفظ"):
                    s_id, s_name = b_student.split(" - ", 1)
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    curr_time = datetime.now().strftime("%H:%M:%S")
                    row = [curr_date, curr_time, s_id, s_name, b_type, b_note, user_name, "جديد"]
                    db.worksheet("Behavior_Log").append_row(row)
                    st.success("تم الحفظ!")
                    st.rerun()

        with tab2:
            with st.form("grades_form"):
                g_student = st.selectbox("الطالب:", student_options)
                g_subject = st.selectbox("المادة:", ["رياضيات", "لغة عربية", "علوم", "إنجليزي", "فقه"])
                g_exam = st.selectbox("نوع التقييم:", ["اختبار شهري", "اختبار نهائي", "مشاركة", "واجبات"])
                g_score = st.number_input("الدرجة:", 0, 100)
                g_note = st.text_input("ملاحظة:")
                if st.form_submit_button("📤 رصد الدرجة"):
                    s_id, s_name = g_student.split(" - ", 1)
                    curr_date = datetime.now().strftime("%Y-%m-%d")
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
            student_info = df_st[df_st['Student_ID'].astype(str) == str(student_id_input)]
            
            if not student_info.empty:
                st.subheader(f"الطالب: {student_info.iloc[0]['Full_Name']}")
                st.table(student_info)
                
                res_tab1, res_tab2 = st.tabs(["📂 السلوك", "📊 الدرجات"])
                
                with res_tab1:
                    sheet_log = db.worksheet("Behavior_Log")
                    df_logs = pd.DataFrame(sheet_log.get_all_records())
                    if not df_logs.empty:
                        s_logs = df_logs[df_logs['Student_ID'].astype(str) == str(student_id_input)]
                        if not s_logs.empty:
                            st.table(s_logs[['Date', 'Type', 'Note', 'Teacher']])
                        else:
                            st.info("لا توجد ملاحظات.")
                    else:
                        st.info("السجل فارغ.")

                with res_tab2:
                    sheet_grades = db.worksheet("Grades")
                    df_grades = pd.DataFrame(sheet_grades.get_all_records())
                    if not df_grades.empty:
                        s_grades = df_grades[df_grades['Student_ID'].astype(str) == str(student_id_input)]
                        if not s_grades.empty:
                            st.dataframe(s_grades[['Subject', 'Exam_Type', 'Score']])
                        else:
                            st.info("لا توجد درجات.")
                    else:
                        st.info("لا توجد درجات.")
            else:
                st.warning("الرقم غير صحيح.")
        except Exception as e:
            st.error(f"خطأ: {e}")



