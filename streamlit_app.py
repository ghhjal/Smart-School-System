import streamlit as st
from supabase import create_client
import uuid

# 1. الاتصال بـ Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# 2. إعدادات الواجهة و CSS الاحترافي
st.set_page_config(page_title="ملف الإنجاز الإلكتروني", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    body, [class*="css"] {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
    }
    
    /* تصميم بطاقة عرض الشواهد */
    .evidence-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    .evidence-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .evidence-title {
        color: #1f2937;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .evidence-desc {
        color: #4b5563;
        font-size: 15px;
        margin-bottom: 15px;
        line-height: 1.6;
    }
    .evidence-meta {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ملف الإنجاز الإلكتروني للمعلم")
st.markdown("**إعداد:** زياد المعمري | **التخصص:** لغة إنجليزية ")
st.write("---")

# قائمة المعايير الـ 11 كاملة
standards_list = [
    "1. أداء الواجبات الوظيفية",
    "2. التفاعل مع المجتمع المهني",
    "3. التفاعل مع أولياء الأمور",
    "4. التنويع في استراتيجيات التدريس",
    "5. تحسين نتائج المتعلمين",
    "6. إعداد وتنفيذ خطة التعلم",
    "7. توظيف تقنيات ووسائل التعلم المناسبة",
    "8. تهيئة بيئة تعليمية",
    "9. الإدارة الصفية",
    "10. تحليل نتائج المتعلمين وتشخيص مستوياتهم",
    "11. تنوع أساليب التقويم"
]

# تقسيم الواجهة إلى تبويبات (Tabs)
tab1, tab2 = st.tabs(["📤 إضافة شاهد جديد", "📂 إدارة وعرض الشواهد"])

def main_app():
    # القائمة الجانبية (Navigation)
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

    # ==========================================
    # 🏠 صفحة لوحة التحكم (الرئيسية)
    # ==========================================
    if menu_selection == "🏠 لوحة التحكم":
        st.markdown("""
            <div class="profile-header">
                <div class="profile-title">ملف الإنجاز المهني</div>
                <div class="profile-subtitle">ملف الإنجاز الإلكتروني للمعلم</div>
                <div class="profile-name">زياد المعمري</div>
                <div class="profile-major">التخصص: لغة إنجليزية / تربية خاصة</div>
            </div>
        """, unsafe_allow_html=True)
        
        # إحصائيات سريعة
        year_name = active_year['year_name'] if active_year else "غير محدد"
        # حساب عدد الشواهد الكلي للسنة الحالية
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

    # ==========================================
    # 📋 صفحة معايير الأداء المهني (العمل الحقيقي هنا)
    # ==========================================
    elif menu_selection == "📋 معايير الأداء المهني":
        st.title("معايير الأداء المهني والشواهد")
        
        if not active_year:
            st.error("⚠️ لا توجد سنة دراسية نشطة! يرجى إعداد السنة الدراسية أولاً.")
            return

        # جلب المعايير من قاعدة البيانات لملء القائمة المنسدلة
        standards_res = supabase.table("standards").select("*").order("id").execute()
        standards_list = standards_res.data
        standards_dict = {f"{s['id']}. {s['title']}": s['id'] for s in standards_list}

        tab1, tab2 = st.tabs(["📤 إضافة شاهد جديد", "📂 سجل الشواهد للعام الحالي"])

        # --- تبويب إضافة شاهد ---
        with tab1:
            import uuid
            st.markdown("### إرفاق شاهد جديد")
            
            with st.form("add_evidence_form", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_standard = st.selectbox("اختر بند التقييم:", list(standards_dict.keys()))
                    evidence_title = st.text_input("عنوان الشاهد (مثال: شهادة دورة كذا...):")
                    evidence_description = st.text_area("وصف الشاهد والتفاصيل:", height=100)
                
                with col2:
                    # تفعيل خيار رفع عدة ملفات
                    uploaded_files = st.file_uploader("المرفقات (صور، PDF) - يمكنك تحديد عدة ملفات", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
                
                submit_evidence = st.form_submit_button("حفظ الشاهد ورفع الملفات 💾", type="primary")

                if submit_evidence:
                    if evidence_title and uploaded_files:
                        try:
                            with st.spinner('جاري تشفير ورفع الملفات وحفظ الشاهد...'):
                                standard_id = standards_dict[selected_standard]
                                
                                # 1. إدخال الشاهد في جدول evidences أولاً
                                evidence_data = supabase.table("evidences").insert({
                                    "standard_id": standard_id,
                                    "year_id": active_year['id'],
                                    "title": evidence_title,
                                    "description": evidence_description
                                }).execute()
                                
                                new_evidence_id = evidence_data.data[0]['id']
                                
                                # 2. رفع الملفات واحدًا تلو الآخر وربطها بالشاهد
                                for up_file in uploaded_files:
                                    file_ext = up_file.name.split('.')[-1]
                                    # بناء مسار الملف: (رقم الشاهد / اسم عشوائي) للتنظيم
                                    file_path = f"{new_evidence_id}/{uuid.uuid4()}.{file_ext}"
                                    
                                    # الرفع للمجلد الخاص
                                    supabase.storage.from_("private-achievements").upload(
                                        path=file_path,
                                        file=up_file.getvalue(),
                                        file_options={"content-type": up_file.type}
                                    )
                                    
                                    # تسجيل الملف في جدول evidence_files
                                    supabase.table("evidence_files").insert({
                                        "evidence_id": new_evidence_id,
                                        "file_url": file_path, # نحفظ المسار وليس الرابط العام
                                        "file_type": up_file.type
                                    }).execute()
                                
                                st.success("تم رفع الشاهد ومرفقاته بنجاح وتأمينها! 🎉")
                        except Exception as e:
                            st.error(f"حدث خطأ أثناء الحفظ: {str(e)}")
                    else:
                        st.warning("الرجاء إدخال عنوان الشاهد وإرفاق ملف واحد على الأقل.")

        # --- تبويب استعراض الشواهد ---
        with tab2:
            st.markdown(f"### الشواهد المرفوعة لعام ({active_year['year_name']})")
            
            # جلب الشواهد مع المرفقات المتعلقة بها
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
                        
                        # عرض المرفقات بأمان
                        files = rec.get("evidence_files", [])
                        if files:
                            st.write("**المرفقات:**")
                            cols = st.columns(len(files) if len(files) < 4 else 4)
                            for i, file_record in enumerate(files):
                                # توليد رابط آمن (Signed URL) صالح لمدة 60 ثانية فقط للعرض!
                                signed_url_res = supabase.storage.from_("private-achievements").create_signed_url(file_record['file_url'], 60)
                                secure_url = signed_url_res['signedURL']
                                
                                with cols[i % 4]:
                                    st.link_button(f"👁️ عرض المرفق {i+1}", secure_url, use_container_width=True)
                        else:
                            st.caption("لا توجد مرفقات.")
                            
                        # زر الحذف (يمكن تطويره لاحقاً ليشمل حذف الملفات من التخزين)
                        if st.button("🗑️ حذف هذا الشاهد", key=f"del_{rec['id']}"):
                            st.warning("تم إيقاف الحذف المباشر حالياً لبرمجته بشكل آمن في الخطوة القادمة.")
