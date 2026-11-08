import streamlit as st
from supabase import create_client, Client
import uuid

# 1. الاتصال بـ Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# 2. إعدادات واجهة ملف الإنجاز
st.set_page_config(page_title="ملف الإنجاز الإلكتروني", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    body {direction: rtl; text-align: right; font-family: 'Tajawal', sans-serif;}
    </style>
""", unsafe_allow_html=True)

st.title("ملف الإنجاز الإلكتروني للمعلم")
st.subheader("إعداد: زياد المعمري")
st.write("**التخصص:** لغة إنجليزية / تربية خاصة")
st.write("**جهة العمل:** مكتب تعليم أُحد - الإدارة العامة للتعليم بمنطقة المدينة المنورة")
st.write("---")

# 3. واجهة إضافة شاهد جديد
st.markdown("### إضافة شاهد جديد")

# تحديد البند الذي يتبعه هذا الشاهد (كمثال)
item_id = st.selectbox("اختر بند التقييم:", [
    "1. أداء الواجبات الوظيفية", 
    "2. التفاعل مع المجتمع المهني",
    "4. التنويع في استراتيجيات التدريس"
])

evidence_description = st.text_input("وصف الشاهد:")

# أداة رفع الملفات (تدعم PDF والصور)
uploaded_file = st.file_uploader("ارفع ملف الشاهد (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

if st.button("حفظ الشاهد ورفع الملف"):
    if uploaded_file is not None and evidence_description:
        try:
            with st.spinner('جاري رفع الملف وحفظ البيانات...'):
                # أ. توليد اسم فريد للملف لتجنب تكرار الأسماء
                file_extension = uploaded_file.name.split('.')[-1]
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                
                # ب. قراءة بيانات الملف
                file_bytes = uploaded_file.getvalue()
                
                # ج. الرفع إلى مجلد achievements-files في Supabase Storage
                supabase.storage.from_("achievements-files").upload(
                    path=unique_filename,
                    file=file_bytes,
                    file_options={"content-type": uploaded_file.type}
                )
                
                # د. استخراج الرابط العام (Public URL) للملف المرفوع
                file_url = supabase.storage.from_("achievements-files").get_public_url(unique_filename)
                
                # هـ. إدخال البيانات في جدول قاعدة البيانات (تأكد من إنشاء جدول evidences في Supabase)
                # الجدول يفترض أن يحتوي على الأعمدة: item_name, description, file_url
                data, count = supabase.table("evidences").insert({
                    "item_name": item_id,
                    "description": evidence_description,
                    "file_url": file_url
                }).execute()
                
                st.success("تم رفع الشاهد وحفظه بنجاح! 🎉")
                st.markdown(f"[عرض الملف المرفوع]({file_url})")
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء الرفع: {e}")
    else:
        st.warning("الرجاء إدخال الوصف وإرفاق ملف قبل الحفظ.")
