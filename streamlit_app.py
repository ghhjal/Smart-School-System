import streamlit as st
from supabase import create_client
import time
import uuid
import requests
from io import BytesIO
import fitz  # PyMuPDF لدمج الملفات

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
    
    /* تصميم الإحصائيات العصرية */
    .modern-stat {
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .stat-blue { background: linear-gradient(135deg, #1e3a8a, #3b82f6); }
    .stat-green { background: linear-gradient(135deg, #065f46, #10b981); }
    .modern-stat h2 { margin: 0; font-size: 32px; font-weight: bold; color: white; }
    .modern-stat p { margin: 0; font-size: 16px; opacity: 0.9; }
    
    /* تكبير أزرار القائمة لتناسب الجوال */
    div[data-testid="stButton"] button {
        height: 70px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
    }
    
    /* الصور المصغرة */
    img { border-radius: 10px; border: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال بـ Supabase والجلسة
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state: st.session_state.user = None
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'

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
# 4. التطبيق الرئيسي
# ==========================================
def main_app():
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None

    if st.session_state.current_page != 'home':
        if st.button("🏠 عودة للرئيسية"): navigate_to('home')
        st.write("---")

    # ----------------------------------------
    # 🏠 الصفحة الرئيسية (إحصائيات عصرية + شبكة 2x2)
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        st.markdown("""
            <div class="profile-header">
                <div class="profile-title">ملف الإنجاز الإلكتروني</div>
                <div class="profile-name">زياد المعمري</div>
                <div class="profile-major">التخصص: لغة إنجليزية / تربية خاصة</div>
            </div>
        """, unsafe_allow_html=True)
        
        # حساب الإحصائيات
        standards_res = supabase.table("standards").select("id").execute()
        total_stds = len(standards_res.data)
        
        evidences_count = 0
        completion_rate = 0
        if active_year:
            ev_res = supabase.table("evidences").select("standard_id").eq("year_id", active_year['id']).execute()
            evidences_count = len(ev_res.data)
            unique_stds_with_ev = len(set([e['standard_id'] for e in ev_res.data]))
            completion_rate = int((unique_stds_with_ev / total_stds) * 100) if total_stds else 0

        # عرض البطاقات العصرية
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="modern-stat stat-blue"><h2>{evidences_count}</h2><p>إجمالي الشواهد</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="modern-stat stat-green"><h2>{completion_rate}%</h2><p>نسبة الإنجاز</p></div>', unsafe_allow_html=True)
        
        st.progress(completion_rate / 100.0)
        st.write(f"**السنة الدراسية الحالية:** {active_year['year_name'] if active_year else 'غير محدد'}")
        st.write("---")
        
        # شبكة الأزرار
        st.write("### القائمة الرئيسية")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 معايير الأداء", use_container_width=True): navigate_to('standards')
            if st.button("📄 التقارير", use_container_width=True): navigate_to('reports')
        with c2:
            if st.button("📅 الأرشيف", use_container_width=True): navigate_to('archive')
            if st.button("🚪 خروج", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.current_page = 'home'
                st.rerun()

    # ----------------------------------------
    # 📋 صفحة معايير الأداء المهني (بنية هرمية)
    # ----------------------------------------
    elif st.session_state.current_page == 'standards':
        st.title("معايير الأداء المهني والشواهد")
        if not active_year:
            st.error("لا توجد سنة دراسية نشطة.")
            return

        # جلب المعايير الرئيسية
        standards_res = supabase.table("standards").select("*").order("id").execute()
        standards_list = standards_res.data
        standards_dict = {f"{s['id']}. {s['title']}": s['id'] for s in standards_list}

        # جلب البنود الفرعية (الشواهد المستهدفة)
        sub_items_res = supabase.table("sub_items").select("*").execute()
        sub_items_list = sub_items_res.data

        # جلب الشواهد المرفوعة (الملفات الفعلية)
        evidences_res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", active_year['id']).execute()
        evidences_list = evidences_res.data

        tab1, tab2 = st.tabs(["📂 سجل المعايير والشواهد", "➕ إدارة المعايير (إضافة بنود)"])

        # --- تبويب عرض المعايير والبنود الفرعية ---
        with tab1:
            for std in standards_list:
                std_id = std['id']
                std_title = std['title']
                std_weight = std['weight']
                
                # تصفية البنود الفرعية والشواهد الخاصة بهذا المعيار
                std_sub_items = [item for item in sub_items_list if item['standard_id'] == std_id]
                std_evidences = [ev for ev in evidences_list if ev['standard_id'] == std_id]
                
                # حساب الإنجاز (مثال مبسط: نعتبر البند مكتمل إذا ارتبط به شاهد)
                # (في تطوير لاحق، يجب ربط الشاهد بالبند الفرعي id بدلاً من المعيار فقط)
                count_ev = len(std_evidences)
                target = std['target_evidences']
                status_icon = "✅" if count_ev >= target else ("⏳" if count_ev > 0 else "❌")

                with st.expander(f"{status_icon} {std_id}. {std_title} - الوزن: {std_weight}%"):
                    
                    # عرض البنود الفرعية المطلوبة كقائمة (مثل الصورة)
                    if std_sub_items:
                        st.markdown("**الشواهد المطلوبة (البنود الفرعية):**")
                        for item in std_sub_items:
                            # تصميم يشبه القائمة في صورتك
                            st.markdown(f"""
                            <div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 5px; background-color: #f9f9f9;">
                                <div style="color: #065f46; font-weight: bold; margin-bottom: 2px;">💡 {item['title']}</div>
                                <div style="font-size: 13px; color: #666;">الأمثلة: {item['description'] or 'لا يوجد'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("لم يتم إضافة بنود فرعية لهذا المعيار.")
                    
                    st.write("---")
                    st.markdown("**الشواهد المرفوعة فعلياً:**")
                    
                    if count_ev == 0:
                        st.info("لا توجد شواهد مرفوعة.")
                    else:
                        for idx, rec in enumerate(std_evidences):
                            st.write(f"**{idx+1}. {rec['title']}**")
                            st.caption(rec['description'])
                            
                            # عرض الصور والمرفقات
                            files = rec.get("evidence_files", [])
                            if files:
                                cols = st.columns(len(files) if len(files) < 3 else 3)
                                for i, f_rec in enumerate(files):
                                    url_res = supabase.storage.from_("private-achievements").create_signed_url(f_rec['file_url'], 60)
                                    sec_url = url_res['signedURL']
                                    with cols[i % 3]:
                                        if f_rec['file_type'].startswith('image/'):
                                            st.image(sec_url, use_container_width=True)
                                        else:
                                            st.link_button(f"📄 ملف PDF {i+1}", sec_url, use_container_width=True)
                            
                            # أزرار الحذف
                            if st.button("🗑️ حذف الشاهد", key=f"del_ev_{rec['id']}", help="حذف هذا الشاهد ومرفقاته"):
                                old_paths = [f['file_url'] for f in files]
                                if old_paths: supabase.storage.from_("private-achievements").remove(old_paths)
                                supabase.table("evidences").delete().eq("id", rec['id']).execute()
                                st.rerun()
                            st.write("---")

                    # زر سريع لإضافة شاهد لهذا المعيار تحديداً
                    with st.popover(f"➕ إضافة شاهد لهذا البند"):
                        with st.form(f"quick_add_{std_id}", clear_on_submit=True):
                            title = st.text_input("عنوان الشاهد:")
                            desc = st.text_area("الوصف:")
                            uploaded_files = st.file_uploader("المرفقات", type=["pdf", "jpg", "png"], accept_multiple_files=True, key=f"file_{std_id}")
                            
                            if st.form_submit_button("حفظ", type="primary"):
                                if title and uploaded_files:
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

        # --- تبويب إدارة البنود الفرعية (الإضافة المرنة) ---
        with tab2:
            st.markdown("### إدارة البنود الفرعية")
            st.write("يمكنك هنا إضافة الشواهد المطلوبة تحت كل معيار (كأمثلة وتوجيهات لك).")
            
            with st.form("add_sub_item_form", clear_on_submit=True):
                selected_std = st.selectbox("المعيار الرئيسي:", list(standards_dict.keys()))
                sub_title = st.text_input("اسم البند الفرعي (المطلوب):")
                sub_desc = st.text_area("أمثلة وشرح على هذا البند (اختياري):")
                
                if st.form_submit_button("إضافة بند فرعي ➕", type="primary"):
                    if sub_title:
                        std_id = standards_dict[selected_std]
                        supabase.table("sub_items").insert({
                            "standard_id": std_id,
                            "title": sub_title,
                            "description": sub_desc
                        }).execute()
                        st.success("تم إضافة البند الفرعي بنجاح!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("يرجى إدخال اسم البند الفرعي.")

    # ----------------------------------------
    # 📄 صفحة التقارير والطباعة
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
                    status_text.text("جاري جلب البيانات من قاعدة البيانات...")
                    res = supabase.table("evidence_files").select("*, evidences(year_id)").execute()
                    current_year_files = [f for f in res.data if f['evidences']['year_id'] == active_year['id']]
                    
                    if not current_year_files:
                        st.warning("لا توجد مرفقات في السنة الحالية لدمجها.")
                    else:
                        merged_pdf = fitz.open()
                        total_files = len(current_year_files)
                        
                        for i, file_record in enumerate(current_year_files):
                            status_text.text(f"جاري معالجة ودمج الملف ({i+1}/{total_files})...")
                            url_res = supabase.storage.from_("private-achievements").create_signed_url(file_record['file_url'], 60)
                            download_url = url_res['signedURL']
                            
                            response = requests.get(download_url)
                            file_bytes = response.content
                            
                            if file_record['file_type'].startswith('image/'):
                                img_doc = fitz.open(stream=file_bytes, filetype="image")
                                pdf_bytes = img_doc.convert_to_pdf()
                                img_pdf = fitz.open("pdf", pdf_bytes)
                                merged_pdf.insert_pdf(img_pdf)
                            elif file_record['file_type'] == 'application/pdf':
                                doc = fitz.open(stream=file_bytes, filetype="pdf")
                                merged_pdf.insert_pdf(doc)
                                
                            progress_bar.progress((i + 1) / total_files)
                            
                        status_text.text("جاري تجهيز الملف النهائي...")
                        pdf_out = BytesIO()
                        merged_pdf.save(pdf_out)
                        merged_pdf.close()
                        status_text.text("✅ تم تجهيز الملف الشامل بنجاح!")
                        
                        st.download_button(
                            label="⬇️ تحميل ملف الإنجاز الشامل (PDF)",
                            data=pdf_out.getvalue(),
                            file_name=f"ملف_إنجاز_زياد_المعمري_{active_year['year_name']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"حدث خطأ أثناء توليد التقرير: {e}")
    else:
        st.info("قيد التطوير.")

# تشغيل التطبيق
if st.session_state.user is None:
    login_page()
else:
    main_app()
