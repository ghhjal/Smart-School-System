import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# --- دوال التشفير والحماية ---
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
    
    # القائمة الرئيسية
    menu = ["🏠 الرئيسية", "🔐 تسجيل الدخول", "🔍 بحث عن طالب"]
    choice = st.radio("القائمة:", menu)
    
    st.markdown("---")
    # أداة مساعدة لتوليد كلمات المرور (احذفها لاحقاً عند الانتهاء)
    with st.expander("🛠️ أداة توليد كلمات المرور"):
        raw_pass = st.text_input("اكتب كلمة المرور لتشفيرها:")
        if raw_pass:
            hashed_pass = make_hashes(raw_pass)
            st.code(hashed_pass)
            st.info("انسخ الكود وضعه في عمود Password في جوجل شيت")

# --- المحتوى ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.info("يرجى تسجيل الدخول للوصول للخدمات.")

elif choice == "🔐 تسجيل الدخول":
    st.header("تسجيل دخول الموظفين")
    
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    
    if st.button("دخول"):
        try:
            db = get_db_connection()
            sheet = db.worksheet("Users") # تأكد أن اسم الصفحة في جوجل شيت هو Users
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # البحث عن المستخدم (تحويل العمود لنص لضمان المطابقة)
            user_found = df[df['Username'].astype(str) == username]
            
            if not user_found.empty:
                stored_password = user_found.iloc[0]['Password']
                user_role = user_found.iloc[0]['Role']
                # user_related_id = user_found.iloc[0]['Related_ID'] # موجود للاستخدام المستقبلي
                
                # مطابقة كلمة المرور المشفرة
                if check_hashes(password, stored_password):
                    st.success(f"مرحباً بك: {username}")
                    st.info(f"الصلاحية: {user_role}")
                    st.balloons()
                    
                    # منطقة خاصة بالمدير
                    if user_role == "مدير":
                        st.write("---")
                        st.warning("⚠️ لوحة تحكم المدير (قيد الإنشاء)")
                else:
                    st.error("كلمة المرور غير صحيحة")
            else:
                st.error("اسم المستخدم غير موجود")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

elif choice == "🔍 بحث عن طالب":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id = st.text_input("أدخل الهوية / الرقم الأكاديمي:")
    
    if st.button("بحث"):
        try:
            db = get_db_connection()
            sheet = db.worksheet("Students")
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            student = df[df['Student_ID'].astype(str) == str(student_id)]
            
            if not student.empty:
                st.success("تم العثور على الطالب:")
                st.table(student)
            else:
                st.warning("لم يتم العثور على طالب بهذا الرقم")
        except Exception as e:
            st.error("حدث خطأ، تأكد من اسم الصفحة Students في ملف الإكسل")
