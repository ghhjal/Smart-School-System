import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# --- 2. تهيئة الذاكرة (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# --- 3. دوال مساعدة (تشفير واتصال) ---
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
    
    # زر الخروج
    if st.session_state.logged_in:
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

    # أداة التشفير (مؤقتة)
    with st.expander("🛠️ أداة تشفير كلمات المرور"):
        raw_pass = st.text_input("اكتب كلمة المرور:")
        if raw_pass:
            st.code(make_hashes(raw_pass))

# --- 5. المحتوى الرئيسي ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.info("نظام متكامل لربط الإدارة بالمعلمين وأولياء الأمور.")
    st.write("استخدم القائمة الجانبية للتنقل.")

elif choice == "🔐 بوابة الموظفين":
    # أ) إذا لم يسجل الدخول
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

    # ب) إذا كان مسجلاً للدخول (هنا نضع لوحة التحكم)
    else:
        user_name = st.session_state.user_info.get('Username')
        role = st.session_state.user_info.get('Role')
        st.success(f"👤 المستخدم: {user_name} | الصلاحية: {role}")
        
        # ---------------------------------------------------------
        #  بداية لوحة الإحصائيات (Dashboard)
        # ---------------------------------------------------------
        st.markdown("### 📊 نظرة عامة على المدرسة")
        try:
            db = get_db_connection()
            sheet_log = db.worksheet("Behavior_Log")
            all_records = sheet_log.get_all_records()
            df_stats = pd.DataFrame(all_records)
            
            if not df_stats.empty:
                col1, col2, col3 = st.columns(3)
                
                # بطاقة 1: العدد الكلي
                col1.metric("إجمالي الملاحظات", len(df_stats))
                
                # بطاقة 2: الرسم البياني
                with col2:
                    st.caption("توزيع الحالات")
                    # نعد القيم في عمود Type
                    type_counts = df_stats['Type'].value_counts()
                    st.bar_chart(type_counts)
                
                # بطاقة 3: آخر 3 أنشطة
                with col3:
                    st.caption("آخر النشاطات")
                    if 'Student_Name' in df_stats.columns and 'Type' in df_stats.columns:
                        latest = df_stats[['Student_Name', 'Type']].tail(3)
                        st.dataframe(latest, hide_index=True)
            else:
                st.info("لا توجد بيانات إحصائية حتى الآن.")
                
        except Exception as e:
            st.warning(f"جاري تحميل الإحصائيات... (أو حدث خطأ بسيط: {e})")
        
        st.markdown("---")
        
        # ---------------------------------------------------------
        #  نهاية لوحة الإحصائيات وبداية نموذج الرصد
        # ---------------------------------------------------------

        st.header("📝 رصد سلوك جديد")
        
        try:
            # جلب قائمة الطلاب
            sheet_students = db.worksheet("Students")
            students_data = sheet_students.get_all_records()
            student_options = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students_data]
            
            with st.form("behavior_form"):
                selected_student = st.selectbox("اختر الطالب:", student_options)
                behavior_type = st.selectbox("نوع الملاحظة:", ["مخالفة سلوكية", "تأخر صباحي", "غياب حصة", "إشادة وتميز", "أخرى"])
                note_text = st.text_area("تفاصيل الملاحظة:")
                
                submitted = st.form_submit_button("💾 حفظ وإرسال")
                
                if submitted:
                    s_id, s_name = selected_student.split(" - ", 1)
                    current_time = datetime.now().strftime("%H:%M:%S")
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    new_row = [current_date, current_time, s_id, s_name, behavior_type, note_text, user_name, "جديد"]
                    
                    sheet_log.append_row(new_row)
                    st.success(f"تم الرصد للطالب {s_name} بنجاح!")
                    # تحديث الصفحة لرؤية الإحصائيات الجديدة
                    st.rerun() 
                    
        except Exception as e:
            st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")

elif choice == "🔍 بحث عن طالب":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id_input = st.text_input("أدخل رقم هوية الطالب:")
    
    if st.button("بحث"):
        try:
            db = get_db_connection()
            
            # 1. بيانات الطالب
            sheet_students = db.worksheet("Students")
            df_st = pd.DataFrame(sheet_students.get_all_records())
            # البحث كنص
            student_info = df_st[df_st['Student_ID'].astype(str) == str(student_id_input)]
            
            if not student_info.empty:
                st.subheader(f"بيانات الطالب: {student_info.iloc[0]['Full_Name']}")
                st.table(student_info)
                
                # 2. سجل السلوك
                st.write("📂 **سجل الملاحظات:**")
                sheet_log = db.worksheet("Behavior_Log")
                all_logs = sheet_log.get_all_records()
                df_logs = pd.DataFrame(all_logs)
                
                if not df_logs.empty:
                    # تصفية حسب رقم الطالب
                    student_logs = df_logs[df_logs['Student_ID'].astype(str) == str(student_id_input)]
                    
                    if not student_logs.empty:
                        # عرض الأعمدة المهمة فقط
                        view_cols = ['Date', 'Type', 'Note', 'Teacher']
                        # نتأكد أن الأعمدة موجودة قبل عرضها لتجنب الأخطاء
                        existing_cols = [c for c in view_cols if c in student_logs.columns]
                        st.table(student_logs[existing_cols])
                    else:
                        st.info("سجل الطالب نظيف! 🌟")
                else:
                    st.info("لا توجد سجلات في النظام.")
            else:
                st.warning("رقم الطالب غير موجود.")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
