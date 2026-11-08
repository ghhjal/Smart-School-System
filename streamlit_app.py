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
    # 📄 صفحة التقارير (تصميم A4 صارم وطباعة مستقلة)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.title("تصدير ملف الإنجاز (PDF)")
        
        if not active_year:
            st.error("لا توجد سنة دراسية نشطة.")
        else:
            if st.button("تجهيز التقرير الاحترافي للطباعة 🖨️", type="primary", use_container_width=True):
                with st.spinner("جاري جمع البيانات وتجهيز التقرير..."):
                    
                    # 1. جلب البيانات الأساسية
                    standards_res = supabase.table("standards").select("*").order("id").execute()
                    stds = standards_res.data
                    
                    evidences_res = supabase.table("evidences").select("*, standards(title, weight, target_evidences), evidence_files(*)").eq("year_id", active_year['id']).order("created_at").execute()
                    all_evidences = evidences_res.data
                    
                    total_evidences = len(all_evidences)
                    
                    # حساب البنود التي تحتوي على شواهد فقط
                    active_stds = [std for std in stds if len([e for e in all_evidences if e['standard_id'] == std['id']]) > 0]
                    covered_stds = len(active_stds)
                    
                    # 2. بناء هيكل CSS صارم لمقاس A4 (يمنع خروج التواقيع لصفحة أخرى)
                    html_content = f"""
                    <!DOCTYPE html>
                    <html dir="rtl" lang="ar">
                    <head>
                        <meta charset="UTF-8">
                        <title>ملف الإنجاز - {active_year['year_name']}</title>
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
                            
                            body {{ font-family: 'Tajawal', sans-serif; background-color: #cbd5e1; margin: 0; padding: 20px; }}
                            
                            /* إعدادات ورقة A4 الصارمة */
                            .page {{ 
                                background-color: white;
                                width: 210mm; 
                                height: 296mm; /* ارتفاع ثابت يمنع الصفحات الفارغة */
                                padding: 10mm 15mm; 
                                margin: 0 auto 20mm auto; 
                                box-shadow: 0 10px 20px rgba(0,0,0,0.15); 
                                box-sizing: border-box; 
                                page-break-after: always;
                                page-break-inside: avoid;
                                display: flex; 
                                flex-direction: column; /* تحويل الصفحة لعمود مرن */
                                overflow: hidden;
                            }}
                            
                            /* الغلاف والفهرس */
                            .cover-page {{ border: 4px solid #146c59; border-radius: 15px; padding: 40px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; box-sizing: border-box; }}
                            .cover-title {{ color: #146c59; font-size: 40px; font-weight: bold; margin-bottom: 15px; }}
                            .cover-subtitle {{ font-size: 22px; margin-bottom: 50px; font-weight: bold; }}
                            .info-table {{ width: 85%; border-collapse: collapse; margin: 0 auto; font-size: 18px; }}
                            .info-table th, .info-table td {{ border: 1px solid #ccc; padding: 15px; text-align: center; }}
                            .info-table th {{ background-color: #f8fafc; width: 30%; font-weight: bold; color: #146c59; }}
                            
                            .header-container {{ display: flex; justify-content: space-between; border-bottom: 2px solid #146c59; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; font-weight: bold; flex-shrink: 0; }}
                            .header-right {{ color: #146c59; }}
                            .header-left {{ text-align: left; }}
                            
                            .index-title {{ color: #146c59; font-size: 26px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom:10px; }}
                            .index-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 15px; }}
                            .index-table th {{ background-color: #e6f2ef; color: #146c59; padding: 12px; text-align: center; border-bottom: 2px solid #146c59; }}
                            .index-table td {{ padding: 12px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
                            
                            /* تفاصيل الشواهد */
                            .content-wrapper {{ flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }}
                            
                            .std-header {{ background-color: #146c59; color: white; padding: 10px 15px; font-size: 16px; font-weight: bold; border-radius: 8px 8px 0 0; margin-bottom: 0; flex-shrink: 0; }}
                            .ev-header {{ background-color: #0f5243; color: white; padding: 8px 15px; font-size: 14px; margin-bottom: 15px; border-radius: 0 0 8px 8px; display: flex; justify-content: space-between; flex-shrink: 0; }}
                            
                            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; flex-shrink: 0; }}
                            .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; text-align: center; border-radius: 8px; }}
                            .meta-title {{ font-size: 12px; color: #64748b; font-weight: bold; margin-bottom: 5px; }}
                            .meta-value {{ font-size: 14px; font-weight: bold; color: #0f172a; }}
                            
                            .desc-section {{ margin-bottom: 15px; line-height: 1.6; font-size: 14px; text-align: justify; padding: 10px; background: #fafafa; border-right: 4px solid #146c59; border-radius: 5px; flex-shrink: 0; }}
                            
                            /* قسم الصور المرن (يتقلص تلقائياً ليناسب الصفحة) */
                            .images-grid {{ flex-grow: 1; display: flex; justify-content: center; align-items: center; gap: 15px; min-height: 0; padding: 5px 0; overflow: hidden; }}
                            .images-grid img {{ max-width: 100%; max-height: 100%; object-fit: contain; border: 1px solid #cbd5e1; border-radius: 8px; }}
                            .pdf-notice {{ background: #f1f5f9; padding: 10px; text-align: center; border-radius: 8px; font-size: 13px; color: #334155; margin-bottom: 10px; border: 1px dashed #94a3b8; flex-shrink: 0; }}
                            
                            /* التواقيع (تلتصق بالأسفل دائماً) */
                            .signatures {{ display: flex; justify-content: space-between; margin-top: auto; border-top: 2px solid #e2e8f0; padding-top: 15px; text-align: center; flex-shrink: 0; }}
                            .sig-box {{ width: 40%; }}
                            
                            /* قواعد الطباعة الصارمة */
                            @media print {{
                                body {{ background-color: white; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                                .page {{ width: 210mm; height: 296mm; margin: 0; padding: 10mm 15mm; box-shadow: none; border: none; }}
                                @page {{ size: A4 portrait; margin: 0; }}
                            }}
                        </style>
                    </head>
                    <body>
                    """
                    
                    # 3. صفحة الغلاف
                    html_content += f"""
                    <div class="page">
                        <div class="cover-page">
                            <div class="cover-title">ملف الإنجاز</div>
                            <div class="cover-subtitle">شواهد الأداء الوظيفي</div>
                            <table class="info-table">
                                <tr><th>الاسم</th><td>زياد المعمري</td></tr>
                                <tr><th>التخصص</th><td>لغة إنجليزية / تربية خاصة</td></tr>
                                <tr><th>المدرسة</th><td>ابتدائية عبادة بن قيس الأنصاري</td></tr>
                                <tr><th>المرحلة</th><td>ابتدائي / متوسط</td></tr>
                                <tr><th>المدينة</th><td>المدينة المنورة</td></tr>
                                <tr><th>دورة الأداء</th><td>{active_year['year_name']}</td></tr>
                                <tr><th>عدد الشواهد</th><td>{total_evidences}</td></tr>
                                <tr><th>البنود المغطاة</th><td>{covered_stds} من {len(stds)}</td></tr>
                            </table>
                        </div>
                    </div>
                    """
                    
                    # الترويسة المشتركة
                    shared_header = f"""
                    <div class="header-container">
                        <div class="header-right">
                            زياد المعمري<br>
                            <span style="font-size:11px; font-weight:normal; color:#666;">شواهد الأداء الوظيفي<br>دورة {active_year['year_name']}</span>
                        </div>
                        <div class="header-left">
                            المملكة العربية السعودية<br>
                            <span style="font-size:11px; font-weight:normal; color:#666;">وزارة التعليم<br>ابتدائية عبادة بن قيس الأنصاري</span>
                        </div>
                    </div>
                    """
                    
                    # 4. صفحة الفهرس (تستبعد البنود الفارغة)
                    html_content += f"""
                    <div class="page">
                        {shared_header}
                        <div class="index-title">فهرس البنود المنجزة</div>
                        <table class="index-table">
                            <tr><th>م</th><th>البند</th><th>الوزن</th><th>الشواهد المرفوعة</th><th>المعتمد</th></tr>
                    """
                    for std in stds:
                        count = len([e for e in all_evidences if e['standard_id'] == std['id']])
                        # الشرط المطلوب: استبعاد البند الذي لا يحتوي على شواهد
                        if count == 0:
                            continue
                            
                        target = std['target_evidences']
                        html_content += f"<tr><td>{std['id']}</td><td style='text-align:right;'>{std['title']}</td><td>{std['weight']}%</td><td style='color:green; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
                    html_content += "</table></div>"
                    
                    # 5. صفحات الشواهد
                    for ev in all_evidences:
                        std = ev['standards']
                        sub_item_title = ev['title']
                        created_date = ev['created_at'][:10]
                        
                        files = ev.get('evidence_files', [])
                        img_html = ""
                        pdf_count = 0
                        
                        for f in files:
                            if f['file_type'].startswith('image/'):
                                url_res = supabase.storage.from_("private-achievements").create_signed_url(f['file_url'], 3600)
                                img_html += f"<img src='{url_res['signedURL']}'>"
                            elif f['file_type'] == 'application/pdf':
                                pdf_count += 1
                                
                        pdf_notice = f"<div class='pdf-notice'>📌 يوجد مرفق PDF عدد ({pdf_count}) محفوظ في النظام.</div>" if pdf_count > 0 else ""
                        images_section = f"<div class='images-grid'>{img_html}</div>" if img_html else ""
                        
                        html_content += f"""
                        <div class="page">
                            {shared_header}
                            
                            <div class="content-wrapper">
                                <div class="std-header">{ev['standard_id']}. {std['title']} · <span style="font-size:14px; font-weight:normal;">الوزن {std['weight']}%</span></div>
                                <div class="ev-header">
                                    <span>البند الفرعي / عنوان الشاهد: {sub_item_title}</span>
                                </div>
                                
                                <div class="meta-grid">
                                    <div class="meta-box"><div class="meta-title">تاريخ الرفع / التنفيذ</div><div class="meta-value">{created_date}</div></div>
                                    <div class="meta-box"><div class="meta-title">نوع الشاهد</div><div class="meta-value">شاهد تنفيذي / إلكتروني</div></div>
                                </div>
                                
                                <div class="desc-section">
                                    <div class="desc-title">الوصف والإيضاح</div>
                                    {ev['description'] or 'لا يوجد وصف مضاف.'}
                                </div>
                                
                                {pdf_notice}
                                {images_section}
                            </div>
                            
                            <div class="signatures">
                                <div class="sig-box">
                                    <div style="color:#666; font-size:12px; margin-bottom:20px;">المعلم:</div>
                                    <div style="border-bottom:1px solid #333; margin-bottom:5px;">زياد المعمري</div>
                                </div>
                                <div class="sig-box">
                                    <div style="color:#666; font-size:12px; margin-bottom:20px;">مدير المدرسة:</div>
                                    <div style="font-weight:bold; margin-bottom:5px;">عبدالمجيد الحربي</div>
                                    <div style="font-size:12px; color:#666;">التاريخ: {created_date}</div>
                                </div>
                            </div>
                        </div>
                        """
                    
                    html_content += "</body></html>"
                    
                    # 6. زر الطباعة
                    import streamlit.components.v1 as components
                    st.success("✅ تم تجهيز التقرير! انقر على الزر أدناه لفتحه في نافذة مستقلة وطباعته.")
                    
                    safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    
                    print_button_html = f"""
                    <div style="text-align: center; margin-top: 15px;">
                        <button onclick="openPrintWindow()" style="width: 100%; padding: 15px; background-color: #065f46; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; font-family: 'Tajawal', sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            🖨️ فتح التقرير للطباعة (مقاس A4)
                        </button>
                    </div>
                    <script>
                        function openPrintWindow() {{
                            var win = window.open('', '_blank');
                            win.document.write(`{safe_html}`);
                            win.document.close();
                            setTimeout(function() {{ win.print(); }}, 1500);
                        }}
                    </script>
                    """
                    components.html(print_button_html, height=85)
# تشغيل التطبيق
if st.session_state.user is None:
    login_page()
else:
    main_app()                    
