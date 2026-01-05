import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# --- دالة الاتصال بقاعدة البيانات (لكي لا نكرر الكود) ---
def get_db_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Smart_School_DB") # تأكد من اسم ملفك هنا

# --- القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100) # صورة تعبيرية
    st.title("نظام الإدارة المدرسية")
    choice = st.radio("اختر البوابة:", ["🏠 الرئيسية", "🔐 تسجيل الدخول", "🔍 بحث عن طالب (لولي الأمر)"])
    st.info("برمجة وتطوير: فريق المدرسة الذكية")

# --- محتوى الصفحات ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.write("هذا النظام يتيح للمعلم والمدير وولي الأمر التواصل الفعال.")
    
    # عرض إحصائيات سريعة (تجربة)
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الطلاب", "500", "+5")
    col2.metric("الحضور اليوم", "98%", "+2%")
    col3.metric("المخالفات", "3", "-1")

elif choice == "🔐 تسجيل الدخول":
    st.header("تسجيل دخول الموظفين")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == "admin" and password == "123": # سنجعلها حقيقية لاحقاً
            st.success("تم الدخول بنجاح! (هذه تجربة)")
        else:
            st.error("بيانات خاطئة")

elif choice == "🔍 بحث عن طالب (لولي الأمر)":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id = st.text_input("أدخل الهوية / الرقم الأكاديمي للطالب:")
    
    if st.button("بحث"):
        try:
            # الاتصال وجلب البيانات
            db = get_db_connection()
            sheet = db.worksheet("Students")
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # البحث داخل البيانات
            # نحول الرقم لنص لضمان المطابقة
            student_found = df[df['Student_ID'].astype(str) == student_id]
            
            if not student_found.empty:
                st.success(f"وجدنا الطالب: {student_found.iloc[0]['Full_Name']}")
                st.dataframe(student_found)
            else:
                st.warning("لم يتم العثور على طالب بهذا الرقم.")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")


