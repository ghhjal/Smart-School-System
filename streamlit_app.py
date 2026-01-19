import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime
from streamlit_option_menu import option_menu
import urllib.parse  # مكتبة لترميز نص الواتساب

# ---------------------------------------------------------
# 1. إعداد الصفحة (بدون قائمة جانبية)
# ---------------------------------------------------------
st.set_page_config(
    page_title="مدرستي الذكية",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. تصميم CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }
    
    .stApp { background-color: #f8f9fa; }
    
    /* إخفاء القائمة الجانبية والعناصر الافتراضية */
    section[data-testid="stSidebar"][aria-expanded="true"]{ display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    .stAppDeployButton {display: none;}
    
    /* تحسين القائمة العلوية */
    .nav-link {
        font-size: 14px !important;
        text-align: center !important;
        margin: 0px !important;
        padding: 10px !important;
    }
    
    /* البطاقات */
    div.css-1r6slb0, div.stForm {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 15px;
    }
    
    /* الأزرار */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    
    /* زر الواتساب */
    .wa-btn {
        text-decoration: none;
        background-color: #25D366;
        color: white !important;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        display: block;
        text-align: center;
        width: 100%;
    }
    .wa-btn:hover { background-color: #128C7E; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الدوال
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def get_db_connection():
    # تأكد من تطابق اسم ملف الاعتماد والمفتاح هنا مع ما لديك
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# ---------------------------------------------------------
# 4. شريط التنقل العلوي
# ---------------------------------------------------------
selected = option_menu(
    menu_title=None,
    options=["الرئيسية", "الموظفين", "ولي الأمر"],
    icons=["house-door-fill", "briefcase-fill", "people-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffff", "border-radius": "0"},
        "icon": {"color": "#4b6cb7", "font-size": "18px"}, 
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#4b6cb7", "color": "white"},
    }
)

if st.session_state.logged_in:
    c1, c2 = st.columns([6, 1])
    with c2:
        if st.button("🚪 خروج", key="logout_top"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()
    st.markdown("---")

# ---------------------------------------------------------
# 5. المحتوى الرئيسي
# ---------------------------------------------------------

# === الصفحة الرئيسية ===
if selected == "الرئيسية":
    st.markdown("<h3 style='text-align: center; color: #182848;'>🏫 بوابة مدرستي</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    try:
        db = get_db_connection()
        st_count = len(db.worksheet("Students").get_all_values()) - 1
    except: st_count = "-"
    
    col1.metric("الطلاب", st_count)
    col2.metric("الفصل", "2")
    col3.metric("السنة", "1445")
    
    st.markdown("#### 📢 الأخبار والإعلانات")
    try:
        news = db.worksheet("News").get_all_records()
        df_news = pd.DataFrame(news)
        if not df_news.empty:
            for i, row in df_news.tail(3).iloc[::-1].iterrows():
                st.info(f"**{row['Title']}**\n\n{row['Content']}\n\nStart -- {row['Date']}")
        else:
            st.write("لا توجد أخبار.")
    except: st.warning("جاري التحميل...")

# === بوابة الموظفين ===
elif selected == "الموظفين":
    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns([1,4,1])
        with c2:
            st.markdown("### 🔐 دخول الكادر")
            with st.form("login"):
                u = st.text_input("اسم المستخدم")
                p = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("تسجيل الدخول"):
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
                            st.error("خطأ في البيانات")
                    except Exception as e: st.error(f"خطأ: {e}")
    else:
        role = st.session_state.user_info.get('Role')
        name = st.session_state.user_info.get('Username')
        
        st.success(f"أهلاً بك: {name} ({role})")

        # 🅰️ لوحة المدير
        if role == "مدير":
            st.markdown("### 👮‍♂️ خدمات المدير")
            t1, t2, t3 = st.tabs(["مستخدمين", "أخبار", "استيراد"])
            
            with t1:
                with st.form("add_u"):
                    st.write("إضافة موظف:")
                    nu = st.text_input("الاسم")
                    np = st.text_input("السر", type="password")
                    nr = st.selectbox("الدور", ["معلم", "مدير"])
                    if st.form_submit_button("حفظ"):
                        try:
                            db = get_db_connection()
                            db.worksheet("Users").append_row([nu, make_hashes(np), nr, ""])
                            st.success("تم!")
                        except: st.error("خطأ")
            
            with t2:
                with st.form("add_n"):
                    st.write("نشر خبر:")
                    tt = st.text_input("العنوان")
                    tc = st.text_area("المحتوى")
                    if st.form_submit_button("نشر"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db = get_db_connection()
                        db.worksheet("News").append_row([dt, tt, tc, name])
                        st.success("تم!")

            with t3:
                st.write("رفع ملف Excel للطلاب:")
                up = st.file_uploader("الملف", type=['xlsx', 'csv'])
                if up and st.button("رفع"):
                    try:
                        df = pd.read_csv(up) if up.name.endswith('csv') else pd.read_excel(up)
                        df = df.astype(str)
                        db = get_db_connection()
                        db.worksheet("Students").append_rows(df.values.tolist())
                        st.success(f"تم رفع {len(df)} طالب")
                    except Exception as e: st.error(str(e))

        # 🅱️ لوحة المعلم
        else:
            st.markdown("### 🏫 خدمات المعلم")
            try:
                db = get_db_connection()
                students = db.worksheet("Students").get_all_records()
                s_list = [f"{s['Student_ID']} - {s['Full_Name']}" for s in students]
                df_st = pd.DataFrame(students)
                c_list = df_st['Class'].unique().tolist() if 'Class' in df_st.columns else []
            except: s_list, c_list = [], []

            # 🛠️ تم تعديل التبويبات هنا: حذف "درجة"
            t1, t2, t3 = st.tabs(["واجب", "غياب", "سلوك"])
            
            with t1: # واجب
                with st.form("hw"):
                    cl = st.selectbox("الفصل", c_list)
                    sb = st.selectbox("المادة", ["رياضيات", "علوم", "لغتي"])
                    tx = st.text_area("الواجب")
                    if st.form_submit_button("إرسال"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        db.worksheet("Homework").append_row([dt, cl, sb, tx, name])
                        st.success("تم")
            
            with t2: # غياب
                with st.form("att"):
                    ab = st.multiselect("الغائبون:", s_list)
                    if st.form_submit_button("حفظ"):
                        dt = datetime.now().strftime("%Y-%m-%d")
                        ab_ids = [x.split(" - ")[0] for x in ab]
                        rows = [[dt, s.split(" - ")[0], s.split(" - ")[1], "غائب" if s.split(" - ")[0] in ab_ids else "حاضر", name] for s in s_list]
                        db.worksheet("Attendance").append_rows(rows)
                        st.success("تم")

            with t3: # سلوك (تم التعديل)
                st.markdown("##### 📝 تسجيل ملاحظة جديدة")
                with st.form("beh"):
                    stt = st.selectbox("الطالب", s_list)
                    ty = st.selectbox("النوع", ["مخالفة", "تأخر", "إشادة"])
                    nt = st.text_input("ملاحظة")
                    
                    if st.form_submit_button("حفظ الملاحظة"):
                        sid, sn = stt.split(" - ", 1)
                        dt = datetime.now().strftime("%Y-%m-%d")
                        # التأكد من صحة الترتيب حسب أعمدة شيت جوجل لديك
                        db.worksheet("Behavior_Log").append_row([dt, "", sid, sn, ty, nt, name, "جديد"])
                        st.success("تم الحفظ")
                        st.rerun() # تحديث الصفحة لظهور الملاحظة فوراً

                # 🛠️ عرض الجدول والملاحظات السابقة مع زر الواتساب
                if stt:
                    current_sid = stt.split(" - ")[0]
                    st.markdown("---")
                    st.markdown(f"##### 📜 سجل ملاحظات: {stt.split(' - ')[1]}")
                    
                    try:
                        # جلب سجل السلوك
                        beh_data = db.worksheet("Behavior_Log").get_all_records()
                        df_beh = pd.DataFrame(beh_data)
                        
                        # تصفية البيانات للطالب المحدد فقط (تأكد أن اسم العمود في شيت جوجل هو Student_ID)
                        # إذا كان اسم العمود مختلف في الشيت (مثلاً "رقم الطالب") يرجى تعديل 'Student_ID' أدناه
                        if not df_beh.empty and 'Student_ID' in df_beh.columns:
                            student_history = df_beh[df_beh['Student_ID'].astype(str) == current_sid]
                            
                            if not student_history.empty:
                                # عرض الملاحظات كجدول مخصص
                                for idx, row in student_history.iterrows():
                                    with st.container():
                                        c1, c2, c3, c4 = st.columns([2, 2, 4, 2])
                                        c1.caption(f"📅 {row.get('Date', '-')}")
                                        
                                        # تلوين نوع الملاحظة
                                        type_color = "red" if row.get('Type') == "مخالفة" else "green" if row.get('Type') == "إشادة" else "orange"
                                        c2.markdown(f":{type_color}[{row.get('Type', '-')}]")
                                        
                                        c3.write(row.get('Note', '-'))
                                        
                                        # تجهيز رابط الواتساب
                                        msg_text = f"السلام عليكم، بخصوص الطالب {row.get('Student_Name')}: \nنوع الملاحظة: {row.get('Type')}\nالتفاصيل: {row.get('Note')}"
                                        encoded_msg = urllib.parse.quote(msg_text)
                                        wa_link = f"https://wa.me/?text={encoded_msg}"
                                        
                                        c4.markdown(f"<a href='{wa_link}' target='_blank' class='wa-btn'>📲 إرسال واتساب</a>", unsafe_allow_html=True)
                                        st.divider()
                            else:
                                st.info("لا توجد ملاحظات سابقة لهذا الطالب.")
                        else:
                            st.warning("لم يتم العثور على سجلات أو هناك خطأ في تسمية الأعمدة.")
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء جلب السجل: {e}")

# === بوابة ولي الأمر ===
elif selected == "ولي الأمر":
    st.markdown("### 👨‍👩‍👦 خدمة ولي الأمر")
    
    c1, c2 = st.columns([3,1])
    pid = c1.text_input("رقم الهوية")
    btn = c2.button("🔍", use_container_width=True)
    
    if btn and pid:
        try:
            db = get_db_connection()
            df = pd.DataFrame(db.worksheet("Students").get_all_records())
            res = df[df['Student_ID'].astype(str) == pid]
            
            if not res.empty:
                st.success(f"الطالب: {res.iloc[0]['Full_Name']}")
                
                # تم حذف تبويب الدرجات من العرض لولي الأمر أيضاً ليتوافق مع الطلب
                t2, t3 = st.tabs(["غياب", "تواصل"])
                
                with t2:
                    a = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                    ma = a[a['Student_ID'].astype(str) == pid] if not a.empty else pd.DataFrame()
                    if not ma.empty:
                        st.metric("أيام الغياب", len(ma[ma['Status']=='غائب']))
                        st.dataframe(ma[['Date', 'Status']], use_container_width=True)
                    else: st.info("لا يوجد")
                
                with t3:
                    with st.form("msg"):
                        m = st.text_area("الرسالة")
                        p = st.text_input("جوالك")
                        if st.form_submit_button("إرسال"):
                            db.worksheet("Messages").append_row([datetime.now().strftime("%Y-%m-%d"), res.iloc[0]['Full_Name'], p, m, "جديد"])
                            st.success("تم")
            else:
                st.error("غير موجود")
        except Exception as e: st.error("خطأ في الاتصال")
