import streamlit as st
from supabase import create_client, Client
import pandas as pd

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="ملف الإنجاز", page_icon="📄", layout="centered")

# تخصيص CSS لتصميم البطاقات واتجاه النص (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #F8F6F4;
    }
    
    .stApp {
        background-color: #F8F6F4;
    }
    
    /* تصميم بطاقة البند */
    .item-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #EAEAEA;
    }
    
    .item-title {
        font-size: 16px;
        font-weight: 700;
        color: #333;
        margin-bottom: 5px;
    }
    
    /* وسم الوزن */
    .weight-tag {
        background-color: #F0F0F0;
        color: #555;
        font-size: 12px;
        padding: 3px 8px;
        border-radius: 10px;
        display: inline-block;
    }
    
    /* مؤشرات الشواهد (النقاط) */
    .dots-container {
        display: flex;
        gap: 4px;
        margin-bottom: 5px;
    }
    .dot {
        width: 12px;
        height: 6px;
        border-radius: 3px;
    }
    .dot-filled { background-color: #D48842; }
    .dot-empty { background-color: #E0E0E0; }
    
    /* حالة الشواهد (نص) */
    .status-text {
        font-size: 12px;
        color: #D48842;
    }
    .status-empty {
        color: #A0A0A0;
    }
    
    /* الدائرة الرقمية للبند */
    .number-circle {
        width: 40px;
        height: 40px;
        background-color: #FDE8D7;
        color: #D48842;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# استدعاء البيانات
@st.cache_data(ttl=60)
def fetch_data():
    # في التطبيق الفعلي، يتم جلب البيانات من Supabase:
    # response = supabase.table("evaluation_items").select("*").execute()
    # return response.data
    
    # بيانات تجريبية مطابقة للملف المرفق
    return [
        {"id": 1, "title": "أداء الواجبات الوظيفية", "weight": 10, "evidences_count": 1, "target": 3},
        {"id": 2, "title": "التفاعل مع المجتمع المهني", "weight": 10, "evidences_count": 2, "target": 3},
        {"id": 3, "title": "التفاعل مع أولياء الأمور", "weight": 10, "evidences_count": 2, "target": 3},
        {"id": 4, "title": "التنويع في استراتيجيات التدريس", "weight": 10, "evidences_count": 1, "target": 3},
        {"id": 5, "title": "تحسين نتائج المتعلمين", "weight": 10, "evidences_count": 0, "target": 3},
        {"id": 6, "title": "إعداد وتنفيذ خطة التعلم", "weight": 10, "evidences_count": 0, "target": 3},
        {"id": 7, "title": "توظيف تقنيات ووسائل التعلم المناسبة", "weight": 10, "evidences_count": 0, "target": 3},
        {"id": 8, "title": "تهيئة بيئة تعليمية", "weight": 5, "evidences_count": 0, "target": 3},
        {"id": 9, "title": "الإدارة الصفية", "weight": 5, "evidences_count": 0, "target": 3},
        {"id": 10, "title": "تحليل نتائج المتعلمين وتشخيص مستوياتهم", "weight": 10, "evidences_count": 2, "target": 3},
        {"id": 11, "title": "تنوع أساليب التقويم", "weight": 10, "evidences_count": 0, "target": 3},
    ]

items_data = fetch_data()

# رأس الصفحة وإحصائيات الإنجاز
st.markdown("### بنود التقييم")
st.markdown("<p style='color: #666; font-size: 14px;'>11 بنداً • الهدف 3 شواهد لكل بند على الأقل</p>", unsafe_allow_html=True)

# حساب الإحصائيات
total_items = len(items_data)
items_with_evidence = sum(1 for item in items_data if item["evidences_count"] > 0)
empty_items = total_items - items_with_evidence

# عرض شريط التقدم
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(items_with_evidence / total_items)
    st.markdown(f"<div style='text-align: left; font-size: 14px; font-weight: bold;'>{items_with_evidence} من {total_items} فيها شواهد</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='text-align: center;'><h3 style='color:#D48842; margin:0;'>{empty_items}</h3><p style='font-size:12px; margin:0;'>فارغة</p></div>", unsafe_allow_html=True)

st.write("---")

# عرض البطاقات
for item in items_data:
    ev_count = item["evidences_count"]
    target = item["target"]
    
    # بناء النقاط (الشواهد)
    dots_html = ""
    for i in range(target):
        if i < ev_count:
            dots_html += "<div class='dot dot-filled'></div>"
        else:
            dots_html += "<div class='dot dot-empty'></div>"
            
    # تحديد النص وحالته
    if ev_count == 0:
        status_text = f"<div class='status-text status-empty'>لا شواهد بعد</div>"
    else:
        status_text = f"<div class='status-text'>{ev_count} شاهد • بقي {target - ev_count}</div>"

    # هيكل البطاقة
    card_html = f"""
    <div class="item-card">
        <div style="flex-grow: 1; margin-right: 15px;">
            <div class="dots-container">
                {dots_html}
            </div>
            {status_text}
        </div>
        <div style="text-align: left;">
            <div class="item-title">{item['title']} .{item['id']}</div>
            <div class="weight-tag">الوزن {item['weight']}%</div>
        </div>
        <div style="margin-left: 15px;">
            <div class="number-circle">{item['id']}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
