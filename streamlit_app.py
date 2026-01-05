import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# --- تهيئة "ذاكرة" التطبيق (Session State) ---
# هذا الكود يمنع النظام من نسيان تسجيل الدخول عند ضغط أي زر
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# --- دوال التشفير ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- الاتصال بقاعدة البيانات ---
def get_db_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# --- القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
    st.title("نظام الإدارة المدرسية")
    
    menu = ["🏠 الرئيسية", "🔐 بوابة الموظفين", "🔍 بحث عن طالب"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    # زر تسجيل الخروج
    if st.session_state.logged_in:
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun() # إعادة تحميل الصفحة

    # أداة المطورين (يمكنك حذفها لاحقاً)
    with st.expander("🛠️ أداة تشفير كلمات المرور"):
        raw_pass = st.text_input("اكتب كلمة المرور:")
        if raw_pass:
            st.code(make_hashes(raw_pass))

# --- المحتوى ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.info("نظام متكامل لربط الإدارة بالمعلمين وأولياء الأمور.")

elif choice == "🔐 بوابة الموظفين":
    # 1. إذا لم يكن مسجلاً للدخول -> اظهر شاشة الدخول
    if not st.session_state.logged_in:
        st.header("تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            try:
                db = get_db_connection()
                sheet = db.worksheet("Users")
                users = sheet.get_all_records()
                df_users = pd.DataFrame(users)
                
                user_found = df_users[df_users['Username'].astype(str) == username]
                
                if not user_found.empty:
                    stored_password = user_found.iloc[0]['Password']
                    if check_hashes(password, stored_password):
                        # نجاح الدخول: حفظ البيانات في الذاكرة
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_found.iloc[0].to_dict()
                        st.success("تم الدخول بنجاح!")
                        st.rerun() # إعادة تحميل لتظهر اللوحة فوراً
                    else:
                        st.error("كلمة المرور غير صحيحة")
                else:
                    st.error("المستخدم غير موجود")
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")

    # 2. إذا كان مسجلاً للدخول -> اظهر لوحة التحكم (Form)
    else:
        user_name = st.session_state.user_info.get('Username')
        role = st.session_state.user_info.get('Role')
        
        st.success(f"مرحباً: {user_name} | الصلاحية: {role}")
        
        # --- نموذج رصد السلوك (للمعلمين والمدراء) ---
        # --- لوحة القيادة (Dashboard) ---
        st.markdown("### 📊 إحصائيات المدرسة السريعة")
        
        try:
            # جلب البيانات لحساب الإحصائيات
            sheet_log = db.worksheet("Behavior_Log")
            all_records = sheet_log.get_all_records()
            df_stats = pd.DataFrame(all_records)
            
            if not df_stats.empty:
                col1, col2, col3 = st.columns(3)
                
                # 1. عدد الرصد الكلي
                total_logs = len(df_stats)
                col1.metric("إجمالي الحالات المرصودة", total_logs)
                
                # 2. نوع الحالات (مخالفات vs تميز)
                # نعد كم مرة تكرر كل نوع
                type_counts = df_stats['Type'].value_counts()
                
                # عرض رسم بياني بسيط
                with col2:
                    st.write("توزيع الحالات:")
                    st.bar_chart(type_counts)
                
                # 3. آخر 5 حالات تم رصدها
                with col3:
                    st.write("آخر النشاطات:")
                    # عرض آخر 5 صفوف فقط والأعمدة المهمة
                    latest = df_stats.tail(5)[['Student_Name', 'Type', 'Time']]
                    st.dataframe(latest, hide_index=True)
                    
            else:
                st.info("لا توجد بيانات كافية لعرض الإحصائيات بعد.")
                
            st.markdown("---") # فاصل خطي
            
        except Exception as e:
            st.warning("لم نتمكن من تحميل الإحصائيات حالياً.")

        # --- (هنا يأتي كود استمارة الرصد القديم كما هو) ---
       # --- لوحة القيادة (Dashboard) ---
        st.markdown("### 📊 إحصائيات المدرسة السريعة")
        
        try:
            # جلب البيانات لحساب الإحصائيات
            sheet_log = db.worksheet("Behavior_Log")
            all_records = sheet_log.get_all_records()
            df_stats = pd.DataFrame(all_records)
            
            if not df_stats.empty:
                col1, col2, col3 = st.columns(3)
                
                # 1. عدد الرصد الكلي
                total_logs = len(df_stats)
                col1.metric("إجمالي الحالات المرصودة", total_logs)
                
                # 2. نوع الحالات (مخالفات vs تميز)
                # نعد كم مرة تكرر كل نوع
                type_counts = df_stats['Type'].value_counts()
                
                # عرض رسم بياني بسيط
                with col2:
                    st.write("توزيع الحالات:")
                    st.bar_chart(type_counts)
                
                # 3. آخر 5 حالات تم رصدها
                with col3:
                    st.write("آخر النشاطات:")
                    # عرض آخر 5 صفوف فقط والأعمدة المهمة
                    latest = df_stats.tail(5)[['Student_Name', 'Type', 'Time']]
                    st.dataframe(latest, hide_index=True)
                    
            else:
                st.info("لا توجد بيانات كافية لعرض الإحصائيات بعد.")
                
            st.markdown("---") # فاصل خطي
            
        except Exception as e:
            st.warning("لم نتمكن من تحميل الإحصائيات حالياً.")

        # --- (هنا يأتي كود استمارة الرصد القديم كما هو) ---
        st.header("📝 رصد سلوك / مخالفة طالب")
        st.header("📝 رصد سلوك / مخالفة طالب") 
        # جلب قائمة الطلاب لوضعها في القائمة المنسدلة
        try:
            db = get_db_connection()
            sheet_students = db.worksheet("Students")
            students_data = sheet_students.get_all_records()
            
            # تجهيز القائمة: (الرقم - الاسم) لسهولة البحث
            student_options = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students_data]
            
            with st.form("behavior_form"):
                selected_student = st.selectbox("اختر الطالب:", student_options)
                behavior_type = st.selectbox("نوع الملاحظة:", ["مخالفة سلوكية", "تأخر صباحي", "غياب حصة", "إشادة وتميز", "أخرى"])
                note_text = st.text_area("تفاصيل الملاحظة:")
                
                submitted = st.form_submit_button("💾 حفظ وإرسال")
                
                if submitted:
                    # تقسيم النص المختار لاستخراج رقم الطالب واسمه
                    s_id, s_name = selected_student.split(" - ", 1)
                    
                    # تجهيز البيانات
                    current_time = datetime.now().strftime("%H:%M:%S")
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    teacher_name = user_name # الشخص الذي قام بالرصد
                    
                    # البيانات التي ستذهب لصفحة Behavior_Log
                    # الترتيب: Date, Time, Student_ID, Student_Name, Type, Note, Teacher, Status
                    new_row = [current_date, current_time, s_id, s_name, behavior_type, note_text, teacher_name, "جديد"]
                    
                    # الإرسال لجوجل شيت
                    sheet_log = db.worksheet("Behavior_Log")
                    sheet_log.append_row(new_row)
                    
                    st.success(f"تم رصد الملاحظة للطالب {s_name} بنجاح! ✅")
        
        except Exception as e:
            st.error(f"خطأ أثناء جلب البيانات أو الحفظ: {e}")

elif choice == "🔍 بحث عن طالب":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id_input = st.text_input("أدخل رقم هوية الطالب:")
    if st.button("بحث"):
        try:
            db = get_db_connection()
            # 1. جلب بيانات الطالب
            sheet_students = db.worksheet("Students")
            df_st = pd.DataFrame(sheet_students.get_all_records())
            student_info = df_st[df_st['Student_ID'].astype(str) == str(student_id_input)]
            
            if not student_info.empty:
                st.subheader(f"الطالب: {student_info.iloc[0]['Full_Name']}")
                st.table(student_info)
                
                # 2. جلب سجل السلوك الخاص به
                st.markdown("---")
                st.write("📂 **سجل الملاحظات والسلوك:**")
                sheet_log = db.worksheet("Behavior_Log")
                all_logs = sheet_log.get_all_records()
                df_logs = pd.DataFrame(all_logs)
                
                if not df_logs.empty:
                    # تصفية السجلات لهذا الطالب فقط
                    student_logs = df_logs[df_logs['Student_ID'].astype(str) == str(student_id_input)]
                    
                    if not student_logs.empty:
                        # عرض أعمدة محددة فقط لولي الأمر
                        display_cols = ['Date', 'Type', 'Note', 'Teacher', 'Status']
                        st.dataframe(student_logs[display_cols])
                    else:
                        st.info("سجل الطالب نظيف، لا توجد ملاحظات. 🌟")
                else:
                    st.info("لا توجد أي سجلات في النظام.")
            else:
                st.warning("رقم الطالب غير صحيح.")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")


