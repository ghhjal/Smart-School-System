import streamlit as st
from supabase import create_client
import time
import uuid

# ==========================================
# 1. إعدادات الصفحة والتصميم (CSS)
# ==========================================
st.set_page_config(page_title="ملف الإنجاز المهني", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    body, [class*="css"] {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
    }
    
    /* تصميم بطاقة التعريف العلوية */
    .profile-header {
        background-color: #1a365d;
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .profile-title { font-size: 24px; font-weight: 700; margin-bottom: 5px; }
    .profile-subtitle { font-size: 14px; color: #cbd5e1; margin-bottom: 15px; }
    .profile-name { font-size: 20px; font-weight: 700; color: #fff; }
    .profile-major { font-size: 14px; color: #cbd5e1; }
    
    /* تصميم الإحصائيات */
    .stat-box {
        text-align: center;
        padding: 15px;
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .stat-icon { font-size: 24px; color: #475569; margin-bottom: 10px; }
    .stat-number { font-size: 28px; font-weight: 700; color: #0f172a; }
    .stat-label { font-size: 14px; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال بقاعدة البيانات وإدارة الجلسة
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state.user = None

# ==========================================
# 3. صفحة تسجيل الدخول
# ==========================================
def login_page():
    st.title("🔒 تسجيل الدخول")
    st.write("ملف الإنجاز المهني محمي، يرجى تسجيل الدخول للوصول إلى لوحة التحكم.")
    
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        submit = st.form_submit_button("دخول", type="primary")
        
        if submit:
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.success("تم تسجيل الدخول بنجاح! جاري التوجيه...")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
            else:
                st.warning("الرجاء إدخال البريد الإلكتروني وكلمة المرور.")

# ==========================================
# 4. التطبيق الرئيسي (بعد تسجيل الدخول)
# ==========================================
def main_app():
    # القائمة الجانبية
    with st.sidebar:
        st.markdown("### قائمة التنقل")
        menu_selection = st.radio("اختر الصفحة:", [
            "🏠 لوحة التحكم",
            "📋 معايير الأداء المهني",
            "📅 الأرشيف السنوي",
            "📄 التقارير والطباعة",
            "🔍 البحث في الشواهد",
            "⚙️ الإعدادات والنسخ الاحتياطي"
        ])
        
        st.write("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    # جلب السنة الدراسية النشطة
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None

    # ----------------------------------------
    # 🏠 لوحة التحكم
    # ----------------------------------------
    if menu_selection == "🏠 لوحة التحكم":
        st.markdown("""
            <div class="profile-header">
                <div class="profile-title">ملف الإنجاز المهني</div>
                <div class="profile-subtitle">ملف الإنجاز الإلكتروني للمعلم</div>
                <div class="profile-name">زياد المعمري</div>
                <div class="profile-major">التخصص: لغة إنجليزية / تربية خاصة</div>
            </div>
        """, unsafe_allow_html=True)
        
        year_name = active_year['year_name'] if active_year else "غير محدد"
        evidences_count = 0
        if active_year:
            count_res = supabase.table("evidences").select("id", count="exact").eq("year_id", active_year['id']).execute()
            evidences_count = count_res.count if count_res.count else 0
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="stat-box"><div class="stat-icon">📁</div><div class="stat-number">11</div><div class="stat-label">المعايير</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box"><div class="stat-icon">📄</div><div class="stat-number">{evidences_count}</div><div class="stat-label">الشواهد</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-box"><div class="stat-icon">📊</div><div class="stat-number">--%</div><div class="stat-label">اكتمال الملف</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-box"><div class="stat-icon">📅</div><div class="stat-number">{year_name}</div><div class="stat-label">السنة الدراسية</div></div>', unsafe_allow_html=True)

    # ----------------------------------------
    # 📋 معايير الأداء المهني وإدارة الشواهد
    # ----------------------------------------
    elif menu_selection == "📋 معايير الأداء المهني":
        st.title("معايير الأداء المهني والشواهد")
        
        if not active_year:
            st.error("⚠️ لا توجد سنة دراسية نشطة! يرجى إعداد السنة الدراسية أولاً.")
            return

        standards_res = supabase.table("standards").select("*").order("id").execute()
        standards_list = standards_res.data
        standards_dict = {f"{s['id']}. {s['title']}": s['id'] for s in standards_list}

        tab1, tab2 = st.tabs(["📤 إضافة شاهد جديد", "📂 سجل الشواهد للعام الحالي"])

        # --- تبويب الإضافة ---
        with tab1:
            st.markdown("### إرفاق شاهد جديد")
            with st.form("add_evidence_form", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_standard = st.selectbox("اختر بند التقييم:", list(standards_dict.keys()))
                    evidence_title = st.text_input("عنوان الشاهد (مثال: شهادة دورة كذا...):")
                    evidence_description = st.text_area("وصف الشاهد والتفاصيل:", height=100)
                with col2:
                    uploaded_files = st.file_uploader("المرفقات (صور، PDF) - يمكنك تحديد عدة ملفات", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
                
                submit_evidence = st.form_submit_button("حفظ الشاهد ورفع الملفات 💾", type="primary")

                if submit_evidence:
                    if evidence_title and uploaded_files:
                        try:
                            with st.spinner('جاري تشفير ورفع الملفات وحفظ الشاهد...'):
                                standard_id = standards_dict[selected_standard]
                                
                                # إدخال الشاهد
                                evidence_data = supabase.table("evidences").insert({
                                    "standard_id": standard_id,
                                    "year_id": active_year['id'],
                                    "title": evidence_title,
                                    "description": evidence_description
                                }).execute()
                                
                                new_evidence_id = evidence_data.data[0]['id']
                                
                                # رفع الملفات المتعددة
                                for up_file in uploaded_files:
                                    file_ext = up_file.name.split('.')[-1]
                                    file_path = f"{new_evidence_id}/{uuid.uuid4()}.{file_ext}"
                                    
                                    supabase.storage.from_("private-achievements").upload(
                                        path=file_path,
                                        file=up_file.getvalue(),
                                        file_options={"content-type": up_file.type}
                                    )
                                    
                                    supabase.table("evidence_files").insert({
                                        "evidence_id": new_evidence_id,
                                        "file_url": file_path,
                                        "file_type": up_file.type
                                    }).execute()
                                
                                st.success("تم رفع الشاهد ومرفقاته بنجاح وتأمينها! 🎉")
                        except Exception as e:
                            st.error(f"حدث خطأ أثناء الحفظ: {str(e)}")
                    else:
                        st.warning("الرجاء إدخال عنوان الشاهد وإرفاق ملف واحد على الأقل.")

        # --- تبويب العرض (الروابط المؤقتة الآمنة) ---
        with tab2:
            st.markdown(f"### الشواهد المرفوعة لعام ({active_year['year_name']})")
            
            evidences_res = supabase.table("evidences").select(
                "*, standards(title), evidence_files(*)"
            ).eq("year_id", active_year['id']).order("created_at", desc=True).execute()
            
            records = evidences_res.data
            
            if not records:
                st.info("لا توجد شواهد مضافة حتى الآن في هذه السنة الدراسية.")
            else:
                for rec in records:
                    with st.expander(f"📁 {rec['title']} - (المعيار: {rec['standards']['title']})"):
                        st.write(f"**الوصف:** {rec['description']}")
                        st.write(f"**تاريخ الإضافة:** {rec['created_at'][:10]}")
                        
                        files = rec.get("evidence_files", [])
                        if files:
                            st.write("**المرفقات:**")
                            cols = st.columns(len(files) if len(files) < 4 else 4)
                            for i, file_record in enumerate(files):
                                # توليد الرابط الآمن
                                signed_url_res = supabase.storage.from_("private-achievements").create_signed_url(file_record['file_url'], 60)
                                secure_url = signed_url_res['signedURL']
                                
                                with cols[i % 4]:
                                    st.link_button(f"👁️ عرض المرفق {i+1}", secure_url, use_container_width=True)
                        else:
                            st.caption("لا توجد مرفقات.")
                            
                        if st.button("🗑️ حذف هذا الشاهد", key=f"del_{rec['id']}"):
                            st.warning("سيتم برمجة الحذف الآمن للملفات وقاعدة البيانات في الخطوة التالية.")

    # باقي الصفحات (قيد التطوير)
    else:
        st.info("سيتم بناء هذه الصفحة لاحقاً بناءً على الخطة المعتمدة.")

# ==========================================
# 5. مشغل التطبيق
# ==========================================
if st.session_state.user is None:
    login_page()
else:
    main_app()
