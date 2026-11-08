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
st.markdown("**إعداد:** زياد المعمري | **التخصص:** لغة إنجليزية / تربية خاصة")
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

# ==========================================
# التبويب الأول: إضافة الشواهد
# ==========================================
with tab1:
    st.markdown("### إرفاق شاهد جديد")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        item_id = st.selectbox("اختر بند التقييم:", standards_list)
        evidence_description = st.text_area("وصف الشاهد بالتفصيل:", height=100)
    with col2:
        uploaded_file = st.file_uploader("ارفع ملف الشاهد (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])
    
    if st.button("حفظ الشاهد 💾", type="primary"):
        if uploaded_file and evidence_description:
            try:
                with st.spinner('جاري الرفع والحفظ...'):
                    # توليد اسم فريد
                    file_extension = uploaded_file.name.split('.')[-1]
                    unique_filename = f"{uuid.uuid4()}.{file_extension}"
                    file_bytes = uploaded_file.getvalue()
                    
                    # الرفع لـ Storage
                    supabase.storage.from_("achievements-files").upload(
                        path=unique_filename,
                        file=file_bytes,
                        file_options={"content-type": uploaded_file.type}
                    )
                    
                    # استخراج الرابط
                    file_url = supabase.storage.from_("achievements-files").get_public_url(unique_filename)
                    
                    # الحفظ في قاعدة البيانات
                    supabase.table("evidences").insert({
                        "item_name": item_id,
                        "description": evidence_description,
                        "file_url": file_url
                    }).execute()
                    
                    st.success("تم رفع الشاهد بنجاح! يمكنك رؤيته في تبويب 'إدارة وعرض الشواهد'.")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
        else:
            st.warning("الرجاء استكمال وصف الشاهد وإرفاق الملف.")

# ==========================================
# التبويب الثاني: عرض وإدارة الشواهد (مع الحذف)
# ==========================================
with tab2:
    st.markdown("### الشواهد المضافة")
    
    # أداة لتصفية الشواهد حسب المعيار (اختياري لتسهيل التصفح)
    filter_standard = st.selectbox("فرز حسب البند (اختر 'الكل' لعرض جميع الشواهد):", ["الكل"] + standards_list)
    st.write("---")

    # جلب البيانات من Supabase
    try:
        if filter_standard == "الكل":
            response = supabase.table("evidences").select("*").order("created_at", desc=True).execute()
        else:
            response = supabase.table("evidences").select("*").eq("item_name", filter_standard).order("created_at", desc=True).execute()
        
        records = response.data
        
        if not records:
            st.info("لا توجد شواهد مضافة في هذا البند حتى الآن.")
        else:
            # عرض البيانات بشكل شبكي (عمودين)
            cols = st.columns(2)
            for index, record in enumerate(records):
                col = cols[index % 2]
                with col:
                    # تنسيق البطاقة باستخدام HTML
                    st.markdown(f"""
                        <div class="evidence-card">
                            <div class="evidence-title">{record['item_name']}</div>
                            <div class="evidence-desc">{record['description']}</div>
                            <div class="evidence-meta">تاريخ الإضافة: {record.get('created_at', '')[:10]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # أزرار التحكم (عرض وحذف) أسفل كل بطاقة
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        st.link_button("👁️ عرض الملف", record['file_url'], use_container_width=True)
                    with btn_col2:
                        if st.button("🗑️ حذف الشاهد", key=f"del_{record['id']}", use_container_width=True):
                            # استخراج اسم الملف من الرابط لحذفه من التخزين
                            filename_to_delete = record['file_url'].split('/')[-1]
                            
                            # 1. حذف الملف من Storage
                            supabase.storage.from_("achievements-files").remove([filename_to_delete])
                            
                            # 2. حذف السجل من قاعدة البيانات
                            supabase.table("evidences").delete().eq("id", record['id']).execute()
                            
                            st.success("تم حذف الشاهد بنجاح!")
                            st.rerun() # تحديث الصفحة فوراً ليعكس الحذف
                            
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
