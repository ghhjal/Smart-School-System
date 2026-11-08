import streamlit as st
from supabase import create_client
import time
import uuid
import requests
from io import BytesIO
import fitz  # مكتبة PyMuPDF لدمج ملفات الـ PDF والصور

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="ملف الإنجاز المهني", page_icon="💼", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    body, [class*="css"] {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
    }
    .profile-header {
        background-color: #1a365d;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .profile-title { font-size: 20px; font-weight: 700; margin-bottom: 5px; }
    .profile-name { font-size: 18px; font-weight: 700; color: #fff; }
    .profile-major { font-size: 14px; color: #cbd5e1; }
    
    /* تكبير أزرار القائمة لتناسب الجوال */
    div[data-testid="stButton"] button {
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال بقاعدة البيانات وإدارة الجلسة والتنقل
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# تهيئة المتغيرات في الجلسة
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# ==========================================
# 3. صفحة تسجيل الدخول
# ==========================================
def login_page():
    st.title("🔒 تسجيل الدخول")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول", type="primary"):
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.success("تم تسجيل الدخول!")
                    time.sleep(1)
                    st.rerun()
                except Exception:
                    st.error("بيانات الدخول غير صحيحة.")
            else:
                st.warning("أدخل البيانات.")

# ==========================================
# 4. التطبيق الرئيسي (الصفحات)
# ==========================================
def main_app():
    # جلب السنة الدراسية النشطة
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None

    # زر الرجوع للرئيسية (يظهر في كل الصفحات عدا الرئيسية)
    if st.session_state.current_page != 'home':
        if st.button("🏠 عودة للرئيسية"):
            navigate_to('home')
        st.write("---")

    # ----------------------------------------
    # 🏠 الصفحة الرئيسية (نظام الشبكة 2x2 للموبايل)
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        st.markdown("""
            <div class="profile-header">
                <div class="profile-title">ملف الإنجاز الإلكتروني</div>
                <div class="profile-name">زياد المعمري</div>
                <div class="profile-major">التخصص: لغة إنجليزية / تربية خاصة</div>
            </div>
        """, unsafe_allow_html=True)
        
        # شبكة الأزرار 2x2
        st.write("### القائمة الرئيسية")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 معايير الأداء", use_container_width=True): navigate_to('standards')
            if st.button("📄 التقارير", use_container_width=True): navigate_to('reports')
        with col2:
            if st.button("📅 الأرشيف", use_container_width=True): navigate_to('archive')
            if st.button("🚪 خروج", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.current_page = 'home'
                st.rerun()

    # ----------------------------------------
    # 📋 صفحة معايير الأداء المهني (تم تحسينها برمجياً)
    # ----------------------------------------
    elif st.session_state.current_page == 'standards':
        st.title("معايير الأداء المهني")
        if not active_year:
            st.error("لا توجد سنة دراسية نشطة.")
            return

        standards_res = supabase.table("standards").select("*").order("id").execute()
        standards_list = standards_res.data
        standards_dict = {f"{s['id']}. {s['title']}": s['id'] for s in standards_list}

        tab1, tab2 = st.tabs(["📂 سجل الشواهد", "📤 إضافة شاهد"])

        with tab1:
            evidences_res = supabase.table("evidences").select("*, standards(title), evidence_files(*)").eq("year_id", active_year['id']).order("created_at").execute()
            
            evidences_by_standard = {}
            for rec in evidences_res.data:
                std_id = rec['standard_id']
                if std_id not in evidences_by_standard: evidences_by_standard[std_id] = []
                evidences_by_standard[std_id].append(rec)
            
            for std in standards_list:
                std_id = std['id']
                target = std['target_evidences']
                std_evidences = evidences_by_standard.get(std_id, [])
                count = len(std_evidences)
                
                status_icon = "✅" if count >= target else ("⏳" if count > 0 else "❌")
                
                with st.expander(f"{status_icon} {std['title']} ({count}/{target})"):
                    if count == 0:
                        st.info("لا توجد شواهد.")
                    else:
                        for idx, rec in enumerate(std_evidences):
                            st.write(f"**{idx+1}. {rec['title']}** - {rec['description']}")
                            files = rec.get("evidence_files", [])
                            if files:
                                cols = st.columns(len(files) if len(files) < 3 else 3)
                                for i, f_rec in enumerate(files):
                                    url_res = supabase.storage.from_("private-achievements").create_signed_url(f_rec['file_url'], 60)
                                    with cols[i % 3]: st.link_button(f"👁️ ملف {i+1}", url_res['signedURL'], use_container_width=True)
                            st.write("---")

        with tab2:
            with st.form("add_form", clear_on_submit=True):
                selected_std = st.selectbox("المعيار:", list(standards_dict.keys()))
                title = st.text_input("عنوان الشاهد:")
                desc = st.text_area("الوصف:")
                uploaded_files = st.file_uploader("المرفقات", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
                
                if st.form_submit_button("حفظ الشاهد 💾", type="primary"):
                    if title and uploaded_files:
                        with st.spinner('جاري الحفظ...'):
                            std_id = standards_dict[selected_std]
                            ev_data = supabase.table("evidences").insert({"standard_id": std_id, "year_id": active_year['id'], "title": title, "description": desc}).execute()
                            new_id = ev_data.data[0]['id']
                            
                            for up_file in uploaded_files:
                                ext = up_file.name.split('.')[-1]
                                path = f"{new_id}/{uuid.uuid4()}.{ext}"
                                supabase.storage.from_("private-achievements").upload(path=path, file=up_file.getvalue(), file_options={"content-type": up_file.type})
                                supabase.table("evidence_files").insert({"evidence_id": new_id, "file_url": path, "file_type": up_file.type}).execute()
                        st.success("تم الحفظ!")
                        time.sleep(1)
                        st.rerun()

    # ----------------------------------------
    # 📄 صفحة التقارير والطباعة (محرك الدمج)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.title("التقارير والطباعة")
        st.write("يمكنك هنا سحب كافة شواهد ومرفقات السنة الدراسية الحالية ودمجها في ملف PDF واحد جاهز للطباعة والمشاركة.")
        
        if st.button("📥 توليد ملف الإنجاز الشامل (PDF)", type="primary", use_container_width=True):
            if not active_year:
                st.error("لا توجد سنة دراسية نشطة.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 1. جلب كافة الملفات
                    status_text.text("جاري جلب البيانات من قاعدة البيانات...")
                    res = supabase.table("evidence_files").select("*, evidences(year_id)").execute()
                    
                    # تصفية ملفات السنة الحالية فقط
                    current_year_files = [f for f in res.data if f['evidences']['year_id'] == active_year['id']]
                    
                    if not current_year_files:
                        st.warning("لا توجد مرفقات في السنة الحالية لدمجها.")
                    else:
                        # 2. إنشاء مستند PDF رئيسي فارغ
                        merged_pdf = fitz.open()
                        total_files = len(current_year_files)
                        
                        # 3. تحميل ودمج الملفات
                        for i, file_record in enumerate(current_year_files):
                            status_text.text(f"جاري معالجة ودمج الملف ({i+1}/{total_files})...")
                            
                            # استخراج رابط مؤقت للتحميل
                            url_res = supabase.storage.from_("private-achievements").create_signed_url(file_record['file_url'], 60)
                            download_url = url_res['signedURL']
                            
                            # تحميل الملف كـ Bytes
                            response = requests.get(download_url)
                            file_bytes = response.content
                            
                            if file_record['file_type'].startswith('image/'):
                                # تحويل الصورة إلى PDF ثم إضافتها
                                img_doc = fitz.open(stream=file_bytes, filetype="image")
                                pdf_bytes = img_doc.convert_to_pdf()
                                img_pdf = fitz.open("pdf", pdf_bytes)
                                merged_pdf.insert_pdf(img_pdf)
                            elif file_record['file_type'] == 'application/pdf':
                                # إضافة الـ PDF مباشرة
                                doc = fitz.open(stream=file_bytes, filetype="pdf")
                                merged_pdf.insert_pdf(doc)
                                
                            progress_bar.progress((i + 1) / total_files)
                            
                        # 4. حفظ المستند المدمج في الذاكرة
                        status_text.text("جاري تجهيز الملف النهائي...")
                        pdf_out = BytesIO()
                        merged_pdf.save(pdf_out)
                        merged_pdf.close()
                        
                        status_text.text("✅ تم تجهيز الملف الشامل بنجاح!")
                        
                        # زر تحميل الملف النهائي
                        st.download_button(
                            label="⬇️ تحميل ملف الإنجاز الشامل (PDF)",
                            data=pdf_out.getvalue(),
                            file_name=f"ملف_إنجاز_زياد_المعمري_{active_year['year_name']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"حدث خطأ أثناء توليد التقرير: {e}")

    # ----------------------------------------
    # مساحات باقي الصفحات
    # ----------------------------------------
    else:
        st.info("سيتم برمجة هذه الصفحة لاحقاً.")

# تشغيل التطبيق
if st.session_state.user is None:
    login_page()
else:
    main_app()
