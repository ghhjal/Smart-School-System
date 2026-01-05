import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials # المكتبة الحديثة

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام مدرستي الذكي", layout="wide", page_icon="🎓")

# --- دالة الاتصال بقاعدة البيانات (التحديث الجديد) ---
def get_db_connection():
    # تحديد الصلاحيات
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # جلب المفاتيح من خزنة Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # إنشاء بيانات الاعتماد بالطريقة الحديثة
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )
    
    # تفويض العميل
    client = gspread.authorize(credentials)
    
    # فتح الملف (تأكد أن الاسم مطابق لاسم ملفك في جوجل شيت)
    return client.open("Smart_School_DB")

# --- القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
    st.title("نظام الإدارة المدرسية")
    choice = st.radio("اختر البوابة:", ["🏠 الرئيسية", "🔐 تسجيل الدخول", "🔍 بحث عن طالب (لولي الأمر)"])
    st.info("برمجة وتطوير: فريق المدرسة الذكية")

# --- محتوى الصفحات ---

if choice == "🏠 الرئيسية":
    st.title("مرحباً بك في النظام المدرسي الذكي 🎓")
    st.write("هذا النظام يتيح للمعلم والمدير وولي الأمر التواصل الفعال.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الطلاب", "500", "+5")
    col2.metric("الحضور اليوم", "98%", "+2%")
    col3.metric("المخالفات", "3", "-1")

elif choice == "🔐 تسجيل الدخول":
    st.header("تسجيل دخول الموظفين")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == "admin" and password == "123":
            st.success("تم الدخول بنجاح! (هذه تجربة)")
        else:
            st.error("بيانات خاطئة")

elif choice == "🔍 بحث عن طالب (لولي الأمر)":
    st.header("خدمة الاستعلام لولي الأمر")
    student_id = st.text_input("أدخل الهوية / الرقم الأكاديمي للطالب:")
    
    if st.button("بحث"):
        try:
            with st.spinner('جاري البحث...'):
                db = get_db_connection()
                # ملاحظة هامة: تأكد أن اسم الصفحة في جوجل شيت هو Students تماماً
                sheet = db.worksheet("Students")
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                
                # تحويل العمود لنص للبحث
                # نستخدم str() للتأكد من مطابقة النصوص
                student_found = df[df['Student_ID'].astype(str) == str(student_id)]
                
                if not student_found.empty:
                    st.success(f"وجدنا الطالب: {student_found.iloc[0]['Full_Name']}")
                    st.table(student_found) # عرض البيانات كجدول ثابت
                else:
                    st.warning("لم يتم العثور على طالب بهذا الرقم.")
                
        except Exception as e:
            st.error(f"حدث خطأ تقني: {e}")
            st.info("تلميح: تأكد أن اسم الصفحة في جوجل شيت هو 'Students' وأن الصف الأول يحتوي على العناوين.")
