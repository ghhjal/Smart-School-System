import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime

# ---------------------------------------------------------
# 1. إعداد الصفحة لتبدو كتطبيق جوال
# ---------------------------------------------------------
st.set_page_config(
    page_title="مدرستي",
    layout="centered",  # نستخدم centered ليناسب شاشة الجوال الطولية
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. حقن CSS (تصميم الجوال والخطوط) 🎨
# ---------------------------------------------------------
mobile_style = """
<style>
/* استيراد خط تجوال العربي الجميل */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

/* تطبيق الخط على كامل التطبيق */
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl; /* اتجاه عربي */
}

/* إخفاء عناصر ستريم ليت الافتراضية */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden !important;}
[data-testid="stDecoration"] {visibility: hidden !important;}

/* تحسين الخلفية */
.stApp {
    background-color: #f0f2f5; /* لون رمادي فاتح جداً مريح للعين */
}

/* تصميم البطاقات (Cards) */
div.css-1r6slb0, div.stForm {
    background-color: white;
    padding: 20px;
    border-radius: 20px; /* حواف دائرية */
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* ظل خفيف */
    margin-bottom: 20px;
}

/* تحسين الأزرار لتشبه أزرار التطبيقات */
.stButton > button {
    width: 100%; /* عرض كامل */
    border-radius: 15px;
    background-color: #4CAF50; /* لون أخضر جذاب */
    color: white;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 16px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #45a049;
    transform: scale(1.02); /* تكبير بسيط عند الضغط */
}

/* تحسين حقول الإدخال */
.stTextInput > div > div > input {
    border-radius: 12px;
    border: 1px solid #ddd;
    padding: 10px;
    text-align: right;
}

/* تحسين القوائم المنسدلة */
.stSelectbox > div > div {
    border-radius: 12px;
}

/* عناوين ملونة */
h1, h2, h3 {
    color: #2c3e50;
    text-align: center;
}

/* رسائل النجاح والخطأ */
.stAlert {
    border-radius: 15px;
}
</style>
"""
st.markdown(mobile_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الدوال (نفس المنطق السابق)
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
# 4. واجهة التطبيق (UI)
# ---------------------------------------------------------

# --- شاشة تسجيل الدخول (بتصميم بطاقة) ---
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True) # مسافة علوية
    st.image("https://cdn-icons-png.flaticon.com/512/2997/2997322.png", width=100) # أيقونة معبرة
    st.title("مدرستي الذكية")
    st.markdown("##### بوابة الدخول الموحدة")
    
    with st.form("login_form"):
        st.markdown("### 🔐 تسجيل الدخول")
        username = st.text_input("اسم المستخدم", placeholder="User123")
        password = st.text_input("كلمة المرور", type="password", placeholder="••••••")
        
        login_btn = st.form_submit_button("دخول للنظام")
        
        if login_btn:
            try:
                with st.spinner('جاري التحقق...'):
                    db = get_db_connection()
                    users = db.worksheet("Users").get_all_records()
                    df = pd.DataFrame(users)
                    user = df[df['Username'].astype(str) == username]
                    if not user.empty and check_hashes(password, user.iloc[0]['Password']):
                        st.session_state.logged_in = True
                        st.session_state.user_info = user.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ البيانات غير صحيحة")
            except Exception as e:
                st.error(f"خطأ: {e}")

    # زر بحث ولي الأمر في شاشة الدخول (لتسهيل الوصول)
    with st.expander("👨‍👩‍👦 هل أنت ولي أمر؟ اضغط هنا"):
        pid = st.text_input("رقم هوية الطالب:")
        if st.button("🔍 بحث سريع"):
            st.session_state.temp_parent_search = pid
            st.session_state.view_mode = "parent_result"
            st.rerun()

# --- بعد تسجيل الدخول (واجهة التطبيق الداخلية) ---
else:
    user = st.session_state.user_info
    
    # رأس الصفحة (Header) يشبه التطبيقات
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🚪"): # زر خروج صغير
            st.session_state.logged_in = False
            st.rerun()
    with c2:
        st.markdown(f"**مرحباً، {user['Username']}** 👋")
    
    st.markdown("---")

    # تحديد الواجهة حسب الصلاحية
    role = user.get('Role')
    
    if role == "مدير":
        st.header("لوحة المدير 👮‍♂️")
        # استخدام التبويبات كقائمة سفلية أو علوية
        tab1, tab2, tab3 = st.tabs(["👥 الموظفين", "📢 الأخبار", "📥 استيراد"])
        
        with tab1:
            with st.form("add_user"):
                st.write("**إضافة مستخدم جديد**")
                nu = st.text_input("المستخدم")
                np = st.text_input("كلمة المرور", type="password")
                nr = st.selectbox("الصلاحية", ["معلم", "مدير"])
                if st.form_submit_button("إضافة"):
                    # (نفس كود الإضافة السابق)
                    try:
                        db = get_db_connection()
                        db.worksheet("Users").append_row([nu, make_hashes(np), nr, ""])
                        st.success("تم!")
                    except: st.error("خطأ")

        with tab2:
            st.info("نشر الأخبار قريباً...")
            
    else: # معلم
        st.header("فصلي الدراسي 🏫")
        
        # قائمة سريعة للمهام (أزرار كبيرة)
        task = st.radio("ماذا تريد أن تفعل اليوم؟", ["رصد الحضور 📅", "رصد الدرجات 💯", "سلوكيات ⚠️"], horizontal=True)
        
        try:
            db = get_db_connection()
            students = db.worksheet("Students").get_all_records()
            s_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
        except: s_list = []

        st.markdown("<br>", unsafe_allow_html=True)
        
        if "الحضور" in task:
            with st.form("att"):
                st.write("🔴 **حدد الغائبين فقط:**")
                absent = st.multiselect("", s_list)
                if st.form_submit_button("حفظ الغياب"):
                    # (كود الحفظ المختصر)
                    st.success("تم الحفظ!")
                    
        elif "الدرجات" in task:
            with st.form("grd"):
                st.write("📊 **رصد درجة:**")
                s = st.selectbox("الطالب", s_list)
                m = st.selectbox("المادة", ["رياضيات", "علوم", "لغتي"])
                sc = st.number_input("الدرجة", 0, 100)
                if st.form_submit_button("رصد"):
                    st.success("تم الرصد!")

# --- (كود عرض نتائج ولي الأمر إذا تم البحث من الخارج) ---
if 'view_mode' in st.session_state and st.session_state.view_mode == 'parent_result':
    st.markdown("---")
    st.header("نتائج البحث 👨‍👦")
    st.info(f"عرض ملف الطالب رقم: {st.session_state.temp_parent_search}")
    # (هنا تضع جداول العرض كما في الكود السابق)
    if st.button("رجوع"):
        st.session_state.view_mode = ""
        st.rerun()
