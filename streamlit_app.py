import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime
from streamlit_option_menu import option_menu
import urllib.parse

# ---------------------------------------------------------
# 1. إعداد الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة زياد الذكية",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. تصميم CSS (تنسيق وواجهة)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }
    
    .stApp { background-color: #f8f9fa; }
    
    /* إخفاء القوائم الافتراضية */
    section[data-testid="stSidebar"][aria-expanded="true"]{ display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* تنسيق القائمة العلوية */
    .nav-link {
        font-size: 14px !important;
        text-align: center !important;
        margin: 0px !important;
        padding: 10px !important;
    }
    
    /* تنسيق البطاقات */
    div.stForm, div.css-1r6slb0, div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    /* الأزرار */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* زر الواتساب */
    .wa-btn {
        text-decoration: none;
        background-color: #25D366;
        color: white !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        display: block;
        text-align: center;
        width: 100%;
        margin-top: 5px;
        font-weight: bold;
    }
    .wa-btn:hover { background-color: #128C7E; }
    
    /* ألوان النصوص */
    .positive { color: #16a34a; font-weight: bold; }
    .negative { color: #dc2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. دوال الاتصال والتحقق
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}
    st.session_state.my_subjects = []
    st.session_state.my_classes = []

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def get_db_connection():
    # تأكد من تطابق اسم ملف secrets والمفتاح json
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open("Smart_School_DB")

# ---------------------------------------------------------
# 4. القائمة العلوية
# ---------------------------------------------------------
selected = option_menu(
    menu_title=None,
    options=["الرئيسية", "الموظفين", "ولي الأمر"],
    icons=["house", "person-badge", "people"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "white"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px"},
        "nav-link-selected": {"background-color": "#4b6cb7", "color": "white"},
    }
)

if st.session_state.logged_in:
    c1, c2 = st.columns([6, 1])
    with c2:
        if st.button("🚪 خروج", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()
    st.markdown("---")

# ---------------------------------------------------------
# 5. الصفحات
# ---------------------------------------------------------

# === الرئيسية ===
if selected == "الرئيسية":
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🏫 منصة الإدارة الذكية</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    try:
        db = get_db_connection()
        st_count = len(db.worksheet("Students").get_all_values()) - 1
        c1.metric("عدد الطلاب", st_count)
    except: c1.metric("عدد الطلاب", "-")
    
    c2.metric("الفصل الدراسي", "الثاني")
    c3.metric("العام", "1445هـ")
    
    st.info("مرحباً بك في النظام المدرسي الموحد. يرجى اختيار البوابة المناسبة من الأعلى.")

# === الموظفين ===
elif selected == "الموظفين":
    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns([1,3,1])
        with c2:
            st.markdown("### 🔐 تسجيل دخول المعلمين")
            with st.form("login_form"):
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
                            user_data = user.iloc[0].to_dict()
                            st.session_state.user_info = user_data
                            
                            # معالجة الصلاحيات (المواد والفصول)
                            raw_subs = str(user_data.get('Subjects', ''))
                            raw_cls = str(user_data.get('Classes', ''))
                            st.session_state.my_subjects = [x.strip() for x in raw_subs.split(',') if x.strip()]
                            st.session_state.my_classes = [x.strip() for x in raw_cls.split(',') if x.strip()]
                            
                            st.rerun()
                        else:
                            st.error("بيانات غير صحيحة")
                    except Exception as e: st.error(f"خطأ تقني: {e}")
    else:
        # واجهة المستخدم المسجل
        role = st.session_state.user_info.get('Role')
        name = st.session_state.user_info.get('Username')
        my_subs = st.session_state.my_subjects
        my_cls = st.session_state.my_classes
        
        st.success(f"مرحباً: {name} | الصلاحية: {role}")
        
        # 1. لوحة المدير
        if role == "مدير":
            st.write("---")
            st.subheader("🛠️ لوحة التحكم")
            t1, t2 = st.tabs(["إضافة مستخدم", "استيراد طلاب"])
            
            with t1:
                with st.form("add_user"):
                    nu = st.text_input("الاسم")
                    np = st.text_input("السر", type="password")
                    nr = st.selectbox("الدور", ["معلم", "مدير"])
                    ns = st.text_input("المواد (مفصولة بفاصلة)")
                    nc = st.text_input("الفصول (مفصولة بفاصلة)")
                    if st.form_submit_button("حفظ"):
                        try:
                            db = get_db_connection()
                            # الترتيب: Username, Password, Role, Email, Subjects, Classes
                            db.worksheet("Users").append_row([nu, make_hashes(np), nr, "", ns, nc])
                            st.success("تمت الإضافة")
                        except Exception as e: st.error(str(e))
            
            with t2:
                up = st.file_uploader("رفع ملف Excel", type=['xlsx'])
                if up and st.button("رفع البيانات"):
                    try:
                        df = pd.read_excel(up).astype(str)
                        db = get_db_connection()
                        db.worksheet("Students").append_rows(df.values.tolist())
                        st.success("تم الرفع بنجاح")
                    except Exception as e: st.error(str(e))

        # 2. لوحة المعلم
        else:
            if not my_cls:
                st.warning("⚠️ لا توجد فصول مرتبطة بحسابك، يرجى مراجعة المدير.")
            else:
                # جلب الطلاب وفلترتهم
                try:
                    db = get_db_connection()
                    all_students = db.worksheet("Students").get_all_records()
                    df_st = pd.DataFrame(all_students)
                    # فلترة حسب فصول المعلم
                    my_students_df = df_st[df_st['Class'].astype(str).isin(my_cls)]
                    s_list = [f"{r['Student_ID']} - {r['Full_Name']}" for i, r in my_students_df.iterrows()]
                except: s_list = []

                st.markdown(f"**🏫 الفصول:** {', '.join(my_cls)} | **📚 المواد:** {', '.join(my_subs)}")
                
                t1, t2, t3 = st.tabs(["📝 الواجبات", "📅 الغياب", "🏆 السلوك والنقاط"])
                
                # --- تبويب الواجبات ---
                with t1:
                    with st.form("hw_form"):
                        c_hw = st.selectbox("الفصل", my_cls)
                        s_hw = st.selectbox("المادة", my_subs if my_subs else ["عام"])
                        t_hw = st.text_area("نص الواجب")
                        if st.form_submit_button("إرسال الواجب"):
                            dt = datetime.now().strftime("%Y-%m-%d")
                            db.worksheet("Homework").append_row([dt, c_hw, s_hw, t_hw, name])
                            st.success("تم الإرسال")

                # --- تبويب الغياب ---
                with t2:
                    with st.form("att_form"):
                        c_att = st.selectbox("اختر الفصل للتحضير", my_cls)
                        # تصفية القائمة بناء على الفصل المختار (بسيط)
                        current_class_students = [s for s in s_list if s.split(" - ")[0] in my_students_df[my_students_df['Class']==c_att]['Student_ID'].astype(str).values] if c_att else []
                        
                        absen = st.multiselect("حدد الطلاب الغائبين", current_class_students)
                        if st.form_submit_button("حفظ الغياب"):
                            dt = datetime.now().strftime("%Y-%m-%d")
                            rows = []
                            for s in current_class_students:
                                sid = s.split(" - ")[0]
                                sname = s.split(" - ")[1]
                                stts = "غائب" if s in absen else "حاضر"
                                rows.append([dt, sid, sname, stts, name])
                            db.worksheet("Attendance").append_rows(rows)
                            st.success("تم الحفظ")

                # --- تبويب السلوك (المطور) ---
                with t3:
                    # إعدادات السلوك
                    behavior_config = {
                        "🌟 إيجابي": {"points": 10, "reasons": ["مشاركة فعالة", "حل الواجب بتميز", "تحسن ملحوظ", "مساعدة الزملاء"]},
                        "⚠️ نسيان": {"points": -2, "reasons": ["كتاب الطالب", "الدفتر", "أدوات الكتابة", "كتاب النشاط"]},
                        "⛔ سلبي": {"points": -5, "reasons": ["كثرة الكلام", "النوم", "تخريب", "تأخر", "عدم احترام"]},
                        "📢 إشعار": {"points": 0, "reasons": ["تنبيه عام", "استدعاء ولي أمر"]}
                    }
                    
                    c_sel, c_res = st.columns([3, 1])
                    with c_sel:
                        stt_beh = st.selectbox("اختر الطالب", s_list, key="beh_st_select")
                    
                    # حساب النقاط
                    total_pts = 0
                    if stt_beh:
                        try:
                            sid_score = stt_beh.split(" - ")[0]
                            logs = db.worksheet("Behavior_Log").get_all_records()
                            df_logs = pd.DataFrame(logs)
                            if not df_logs.empty and 'Points' in df_logs.columns:
                                st_logs = df_logs[df_logs['Student_ID'].astype(str) == sid_score]
                                total_pts = pd.to_numeric(st_logs['Points'], errors='coerce').fillna(0).sum()
                        except: pass
                    
                    with c_res:
                        st.metric("مجموع النقاط", int(total_pts))
                    
                    st.divider()
                    
                    # منطقة الإدخال التفاعلية (بدون Form)
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            b_type = st.selectbox("نوع السلوك", list(behavior_config.keys()), key="b_type")
                        with col2:
                            b_reas = st.selectbox("الملاحظة", behavior_config[b_type]["reasons"], key="b_reas")
                        
                        pts_val = behavior_config[b_type]["points"]
                        st.caption(f"النقاط المحتسبة: {pts_val}")
                        ex_note = st.text_input("ملاحظة إضافية", key="ex_note")
                        
                        if st.button("💾 حفظ السلوك", key="save_beh_btn", type="primary"):
                            if stt_beh:
                                sid, sn = stt_beh.split(" - ", 1)
                                dt = datetime.now().strftime("%Y-%m-%d")
                                full_note = f"{b_reas}" + (f" - {ex_note}" if ex_note else "")
                                db.worksheet("Behavior_Log").append_row([dt, "", sid, sn, b_type, full_note, name, "جديد", pts_val])
                                st.success("تم الرصد بنجاح!")
                                st.rerun()
                    
                    # عرض سجل الطالب
                    if stt_beh:
                        current_sid = stt_beh.split(" - ")[0]
                        st.markdown("##### 📜 السجل السابق")
                        try:
                            # إعادة الجلب للتحديث
                            logs = db.worksheet("Behavior_Log").get_all_records()
                            df_logs = pd.DataFrame(logs)
                            if not df_logs.empty and 'Student_ID' in df_logs.columns:
                                my_logs = df_logs[df_logs['Student_ID'].astype(str) == current_sid]
                                if not my_logs.empty:
                                    # عرض آخر 5 ملاحظات
                                    for idx, row in my_logs.tail(5).iloc[::-1].iterrows():
                                        with st.container():
                                            c_a, c_b, c_c, c_d = st.columns([2, 2, 4, 2])
                                            c_a.caption(row.get('Date'))
                                            
                                            typ = row.get('Type')
                                            clr = "green" if "إيجابي" in typ else "red" if "سلبي" in typ else "orange"
                                            c_b.markdown(f":{clr}[{typ}] ({row.get('Points')}ن)")
                                            
                                            c_c.write(row.get('Note'))
                                            
                                            # واتساب
                                            msg = f"ولي أمر الطالب {row.get('Student_Name')}:\nتم رصد سلوك: {typ}\nالتفاصيل: {row.get('Note')}\nالمعلم: {name}"
                                            lnk = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                                            c_d.markdown(f"<a href='{lnk}' target='_blank' class='wa-btn'>واتساب</a>", unsafe_allow_html=True)
                                            st.divider()
                                else: st.info("سجل نظيف")
                        except Exception as e: st.error("خطأ في جلب السجل")

# === ولي الأمر ===
elif selected == "ولي الأمر":
    st.markdown("### 👨‍👩‍👦 بوابة المتابعة")
    c1, c2 = st.columns([3,1])
    pid = c1.text_input("رقم هوية الطالب")
    if c2.button("بحث", key="p_search") and pid:
        try:
            db = get_db_connection()
            df = pd.DataFrame(db.worksheet("Students").get_all_records())
            res = df[df['Student_ID'].astype(str) == pid]
            
            if not res.empty:
                st.success(f"الطالب: {res.iloc[0]['Full_Name']}")
                
                t_p1, t_p2 = st.tabs(["الغياب", "تواصل مع المدرسة"])
                
                with t_p1:
                    att = pd.DataFrame(db.worksheet("Attendance").get_all_records())
                    if not att.empty:
                        my_att = att[att['Student_ID'].astype(str) == pid]
                        absent_days = my_att[my_att['Status'] == "غائب"]
                        st.metric("عدد أيام الغياب", len(absent_days))
                        if not absent_days.empty:
                            st.dataframe(absent_days[['Date', 'Status']], use_container_width=True)
                        else: st.info("لا يوجد غياب")
                
                with t_p2:
                    with st.form("msg_p"):
                        pm = st.text_area("نص الرسالة")
                        pp = st.text_input("رقم جوال للتواصل")
                        if st.form_submit_button("إرسال"):
                            db.worksheet("Messages").append_row([datetime.now().strftime("%Y-%m-%d"), res.iloc[0]['Full_Name'], pp, pm, "جديد"])
                            st.success("تم الإرسال")
            else:
                st.error("رقم الهوية غير موجود")
        except: st.error("خطأ في الاتصال")
