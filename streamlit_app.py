import streamlit as st
from supabase import create_client
import time
import uuid
import json
import datetime
from hijri_converter import Gregorian
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة والتصميم العام (CSS)
# ==========================================
st.set_page_config(
    page_title="ملف الإنجاز المهني",
    page_icon="🟢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSidebar {display: none !important;}
    
    body, [class*="css"] {
        direction: rtl; 
        text-align: right; 
        font-family: 'Tajawal', sans-serif;
        background-color: #f7f6f2;
    }
    
    .stApp {
        background-color: #f7f6f2;
    }
    
    /* الهيدر الترحيبي */
    .greeting-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0 15px 0; border-bottom: 1px solid #e5e5e0; margin-bottom: 15px;
    }
    .greeting-title { font-size: 24px; font-weight: 700; color: #143d34; margin: 0;}
    .greeting-date { font-size: 13px; color: #7f8c8d; margin-top: 4px;}
    .icon-btn { 
        background: #146c59; color: white; width: 38px; height: 38px; 
        border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
        font-weight: bold; margin-right: 6px; font-size: 16px;
    }

    /* بانر المدرسة */
    .school-banner {
        background: linear-gradient(135deg, #146c59, #0f5243);
        color: white; padding: 18px 20px; border-radius: 16px;
        margin-bottom: 18px; box-shadow: 0 4px 12px rgba(20, 108, 89, 0.15);
    }
    .school-name { font-size: 13px; opacity: 0.9; margin-bottom: 4px; }
    .holiday-text { font-size: 18px; font-weight: 700; margin: 0; }
    
    /* بطاقة نسبة الإنجاز */
    .progress-card {
        background: white; padding: 18px 20px; border-radius: 16px; 
        margin-bottom: 18px; border: 1px solid #eceae4;
        display: flex; align-items: center; justify-content: space-between; gap: 20px;
    }
    .progress-bar-bg {
        background: #eceae4; height: 8px; border-radius: 4px; width: 100%; overflow: hidden; margin-top: 8px;
    }
    .progress-bar-fill {
        background: #146c59; height: 100%; border-radius: 4px;
    }
    .stat-mini {
        text-align: center; min-width: 65px; border-right: 1px solid #eee; padding-right: 15px;
    }
    
    /* بطاقة المعيار */
    .std-card {
        background: white; border: 1px solid #eceae4; border-radius: 16px;
        padding: 16px 20px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .std-num {
        width: 42px; height: 42px; border-radius: 12px;
        background: #f5efe6; color: #b56c27;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 18px; margin-left: 14px; flex-shrink: 0;
    }
    .std-num-empty {
        background: #f9ebea; color: #c0392b;
    }
    .std-title { font-size: 16px; font-weight: 700; color: #222; margin-bottom: 6px; }
    .weight-badge {
        background: #f0efeb; color: #555; font-size: 12px; padding: 3px 10px;
        border-radius: 10px; display: inline-block; margin-left: 6px;
    }
    .dots-row { display: flex; gap: 5px; margin-bottom: 6px; }
    .dot { width: 14px; height: 6px; border-radius: 3px; }
    .dot-on { background: #c57b30; }
    .dot-off { background: #e0ded8; }
    
    /* البنود الفرعية (أفكار تبدأ منها) */
    .idea-card {
        background: white; border: 1px solid #eceae4; padding: 12px 16px;
        border-radius: 12px; margin-bottom: 8px; font-size: 14px; color: #333;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    /* بطاقة الشاهد المرفوع */
    .ev-box {
        background: white; border: 1px solid #d1e8e2; border-radius: 14px;
        padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    /* مساحة سفلية */
    .spacer { height: 40px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. القيم الافتراضية للبنود الفرعية الـ 11
# ==========================================
DEFAULT_SUB_ITEMS = {
    1: [
        "تقرير الحضور والانتظار من النظام",
        "سجل تنفيذ المناوبة والإشراف اليومي",
        "تكليفات اللجان مع محاضر الإنجاز",
        "مبادرة انضباط أو قيم وطنية نفذتها مع وصف أثرها"
    ],
    2: [
        "شهادة دورة مع ملخص ما طبقته منها في الفصل",
        "تقرير زيارة تبادلية مع زميل ونموذج الملاحظة",
        "تأمل ذاتي مكتوب بعد درس",
        "محضر مجتمع تعلم مهني شاركت فيه أو قدمته",
        "خطة إرشاد معلم جديد وسجل لقاءاتها",
        "ورشة قدمتها لمعلمي المدرسة أو المكتب"
    ],
    3: [
        "سجل تواصل مجمّع: التاريخ والموضوع والإجراء (بلا لقطات محادثات)",
        "رسائل دورية عن تقدم الطلاب",
        "محضر لقاء ولي أمر وخطة دعم مشتركة",
        "نشرة إرشادية لدعم التعلم في البيت"
    ],
    4: [
        "تحضير درس يوضح الاستراتيجية المستخدمة",
        "أعمال طلاب ناتجة عن الاستراتيجية (بلا أسماء ولا وجوه)",
        "مصفوفة الاستراتيجيات المستخدمة خلال الفصل",
        "درس تطبيقي قدمته لزملائك عن استراتيجية"
    ],
    5: [
        "خطة علاجية مع نتائج قبلية وبعدية مجمعة",
        "نماذج تغذية راجعة مكتوبة على أعمال الطلاب",
        "برنامج إثرائي للمتفوقين",
        "رسم بياني لتطور نسب الإتقان"
    ],
    6: [
        "خطة توزيع المنهج الفصلية",
        "تحضير دروس بأنشطة متمايزة",
        "محضر تخطيط مشترك مع معلمي المادة",
        "تعديل على الخطة بعد تحليل النتائج مع بيان السبب"
    ],
    7: [
        "تقرير نشاط منصة مدرستي (واجبات واختبارات ودروس)",
        "وسيلة تعليمية محسوسة أو رقمية من إعدادك",
        "درس تفاعلي باختبار قصير أو سبورة تفاعلية",
        "ورشة لزملائك عن أداة رقمية"
    ],
    8: [
        "صور الفصل والجداريات دون طلاب",
        "لوحة تعزيز أو نظام نقاط",
        "ركن قراءة أو ركن تعلم",
        "ميثاق صف أعده الطلاب (بلا أسماء)"
    ],
    9: [
        "قواعد الصف وإجراءاته المعلنة",
        "سجل متابعة السلوك بأرقام مجمعة",
        "توزيع الأدوار والمجموعات",
        "خطة تعديل سلوك فردية (بلا اسم)"
    ],
    10: [
        "اختبار تشخيصي وتحليله لكل مهارة",
        "تصنيف الطلاب: متقن وقريب ومتعثر",
        "تحليل نتائج نافس أو اختبار الفترة",
        "قرار تدريسي اتخذته بناءً على التحليل",
        "تقرير تشخيصي شاركته مع زملائك"
    ],
    11: [
        "اختبار قصير مع مهمة أدائية وسلم تقدير",
        "قائمة رصد أو بطاقة ملاحظة",
        "اختبار إلكتروني مع تقريره",
        "نماذج تقويم ذاتي وتقويم أقران"
    ]
}

# ==========================================
# 3. الاتصال بقاعدة البيانات وإدارة الجلسة
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'view_standard_id' not in st.session_state:
    st.session_state.view_standard_id = 1
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id is not None:
        st.session_state.view_standard_id = std_id
    st.rerun()

# ==========================================
# 4. دوال التاريخ والترحيب
# ==========================================
def get_greeting_and_dates():
    tz = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz)
    today = now.date()
    
    greeting = "صباح الخير" if now.hour < 12 else "مساء الخير"
    
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[today.weekday()]
    g_date = f"{today.day} {months_ar[today.month - 1]} {today.year}م"
    
    h_obj = Gregorian(today.year, today.month, today.day).to_hijri()
    h_months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    h_date = f"{h_obj.day} {h_months[h_obj.month - 1]} {h_obj.year}هـ"
    
    return greeting, f"{day_name} • {h_date} • {g_date}"

# ==========================================
# 5. صفحة تسجيل الدخول (كانت مفقودة سابقاً)
# ==========================================
def login_page():
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="school-banner" style="text-align: center;">
            <div style="font-size: 26px; font-weight: bold; margin-bottom: 5px;">ملف الإنجاز المهني</div>
            <div style="font-size: 14px; opacity: 0.9;">بوابة توثيق شواهد الأداء الوظيفي</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("#### 🔒 تسجيل الدخول")
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        submit = st.form_submit_button("دخول للنظام", type="primary", use_container_width=True)
        
        if submit:
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.success("تم تسجيل الدخول بنجاح!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception:
                    st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
            else:
                st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")

# ==========================================
# 6. التطبيق الرئيسي
# ==========================================
def main_app():
    # جلب السنة الدراسية النشطة
    year_res = supabase.table("academic_years").select("*").eq("is_active", True).execute()
    active_year = year_res.data[0] if year_res.data else None

    # جلب بيانات المعلم والمدرسة بأمان
    default_profile = {
        "full_name": "زياد المعمري",
        "specialization": "لغة إنجليزية / تربية خاصة",
        "school_name": "ابتدائية عبادة بن قيس الأنصاري",
        "education_stage": "ابتدائي / متوسط",
        "city": "المدينة المنورة",
        "principal_name": "عبدالمجيد الحربي",
        "banner_note": "الأسبوع 11 • إجازة الخريف بعد 11 يوماً"
    }
    try:
        profile_res = supabase.table("user_profile").select("*").eq("id", 1).execute()
        user_info = {**default_profile, **profile_res.data[0]} if profile_res.data else default_profile
    except Exception:
        user_info = default_profile

    # شريط التنقل العلوي السريع (متوافق مع الجوال)
    nav1, nav2, nav3, nav4, nav5 = st.columns(5)
    with nav1:
        if st.button("🏠 الرئيسية", use_container_width=True): navigate_to('home')
    with nav2:
        if st.button("📋 البنود", use_container_width=True): navigate_to('standard_view', st.session_state.view_standard_id)
    with nav3:
        if st.button("➕ إضافة", type="primary", use_container_width=True): navigate_to('quick_add')
    with nav4:
        if st.button("📄 التقرير", use_container_width=True): navigate_to('reports')
    with nav5:
        if st.button("⚙️ حسابي", use_container_width=True): navigate_to('settings')

    st.write("---")

    # الهيدر الترحيبي بالتاريخ الهجري والميلادي
    greeting, today_str = get_greeting_and_dates()
    first_name = user_info['full_name'].split()[0] if user_info['full_name'] else "المعلم"
    first_letter = first_name[0] if first_name else "ز"
    
    st.markdown(f"""
        <div class="greeting-header">
            <div>
                <h1 class="greeting-title">{greeting}، أ. {first_name}</h1>
                <div class="greeting-date">{today_str}</div>
            </div>
            <div>
                <span class="icon-btn">{first_letter}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # جلب المعايير والشواهد
    standards_res = supabase.table("standards").select("*").order("id").execute()
    stds = standards_res.data
    
    evidences = []
    if active_year:
        ev_res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", active_year['id']).order("created_at", desc=True).execute()
        evidences = ev_res.data

    # ----------------------------------------
    # 🏠 1. الصفحة الرئيسية (لوحة الإنجاز والبنود الـ 11)
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        banner_text = user_info.get('banner_note', 'الأسبوع الدراسي الحالي')
        st.markdown(f"""
            <div class="school-banner">
                <div class="school-name">{user_info['school_name']}</div>
                <div class="holiday-text">{banner_text}</div>
            </div>
        """, unsafe_allow_html=True)

        # حساب إحصائيات البنود
        total_stds = len(stds)
        stds_with_ev = 0
        stds_reached_target = 0
        empty_stds = 0

        ev_by_std = {}
        for s in stds:
            c = len([e for e in evidences if e['standard_id'] == s['id']])
            ev_by_std[s['id']] = c
            if c > 0:
                stds_with_ev += 1
            else:
                empty_stds += 1
            if c >= s.get('target_evidences', 3):
                stds_reached_target += 1

        pct = int((stds_with_ev / total_stds) * 100) if total_stds else 0

        # بطاقة نسبة الإنجاز
        st.markdown(f"""
            <div class="progress-card">
                <div style="flex-grow: 1;">
                    <div style="display:flex; justify-content:space-between; font-weight:700; font-size:15px;">
                        <span>{stds_with_ev} من {total_stds} فيها شواهد</span>
                        <span style="color:#146c59;">{pct}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {pct}%;"></div>
                    </div>
                </div>
                <div class="stat-mini">
                    <div style="font-size:20px; font-weight:700; color:#146c59;">{stds_reached_target}</div>
                    <div style="font-size:11px; color:#777;">وصلت الهدف</div>
                </div>
                <div class="stat-mini">
                    <div style="font-size:20px; font-weight:700; color:#c0392b;">{empty_stds}</div>
                    <div style="font-size:11px; color:#777;">فارغة</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # أزرار الفلترة
        f_col1, f_col2, f_col3 = st.columns(3)
        less_than_3 = sum(1 for s in stds if ev_by_std[s['id']] < s.get('target_evidences', 3))
        with f_col1:
            if st.button(f"الكل • {total_stds}", use_container_width=True):
                st.session_state.filter_mode = 'all'
                st.rerun()
        with f_col2:
            if st.button(f"فارغة • {empty_stds}", use_container_width=True):
                st.session_state.filter_mode = 'empty'
                st.rerun()
        with f_col3:
            if st.button(f"أقل من 3 • {less_than_3}", use_container_width=True):
                st.session_state.filter_mode = 'less3'
                st.rerun()

        # عرض بطاقات البنود الـ 11
        for std in stds:
            s_id = std['id']
            count = ev_by_std[s_id]
            target = std.get('target_evidences', 3)

            if st.session_state.filter_mode == 'empty' and count > 0:
                continue
            if st.session_state.filter_mode == 'less3' and count >= target:
                continue

            dots_html = "".join([
                f"<div class='dot {'dot-on' if i < count else 'dot-off'}'></div>"
                for i in range(target)
            ])
            
            if count == 0:
                status_txt = "<span style='color:#c0392b; font-size:12px;'>لا شواهد بعد</span>"
                num_cls = "std-num std-num-empty"
            elif count >= target:
                status_txt = f"<span style='color:#146c59; font-size:12px;'>مكتمل ({count} شواهد)</span>"
                num_cls = "std-num"
            else:
                status_txt = f"<span style='color:#c57b30; font-size:12px;'>{count} شاهد • بقي {target - count}</span>"
                num_cls = "std-num"

            st.markdown(f"""
                <div class="std-card">
                    <div style="display:flex; align-items:center;">
                        <div class="{num_cls}">{s_id}</div>
                        <div>
                            <div class="std-title">{s_id}. {std['title']}</div>
                            <span class="weight-badge">الوزن {std['weight']}%</span>
                        </div>
                    </div>
                    <div style="text-align:left;">
                        <div class="dots-row">{dots_html}</div>
                        {status_txt}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📂 فتح البند {s_id}: {std['title']}", key=f"open_std_{s_id}", use_container_width=True):
                navigate_to('standard_view', s_id)

    # ----------------------------------------
    # 📋 2. صفحة تفاصيل البند الفردي والشواهد
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        std_id = st.session_state.view_standard_id
        std_list = [s for s in stds if s['id'] == std_id]
        std_data = std_list[0] if std_list else stds[0]

        c_back, c_title = st.columns([1, 4])
        with c_back:
            if st.button("➡️ رجوع", use_container_width=True):
                navigate_to('home')
        with c_title:
            st.markdown(f"### البند {std_id}: {std_data['title']} (الوزن {std_data['weight']}%)")

        # جلب الشواهد الخاصة بهذا البند
        std_evidences = [e for e in evidences if e['standard_id'] == std_id]
        st.markdown(f"#### شواهدك المرفوعة ({len(std_evidences)})")

        if not std_evidences:
            st.info("لا توجد شواهد مرفوعة في هذا البند حتى الآن. اختر من الأفكار بالأسفل لإضافة شاهدك الأول.")
        else:
            for idx, ev in enumerate(std_evidences):
                files = ev.get("evidence_files", [])
                exec_date = ev['created_at'][:10]
                
                st.markdown(f"""
                    <div class="ev-box">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; font-size:16px; color:#146c59;">📄 {ev['title']}</span>
                            <span style="background:#e6f2ef; color:#146c59; padding:3px 10px; border-radius:10px; font-size:12px;">تاريخ الرفع: {exec_date}</span>
                        </div>
                        <div style="font-size:14px; color:#444; line-height:1.6;">{ev.get('description') or ''}</div>
                    </div>
                """, unsafe_allow_html=True)

                # عرض الصور المصغرة وملفات الـ PDF
                if files:
                    cols = st.columns(min(len(files), 3))
                    for i, f_rec in enumerate(files):
                        try:
                            url_res = supabase.storage.from_("private-achievements").create_signed_url(f_rec['file_url'], 300)
                            sec_url = url_res['signedURL']
                            with cols[i % 3]:
                                if f_rec.get('file_type', '').startswith('image/'):
                                    st.image(sec_url, use_container_width=True)
                                else:
                                    st.link_button(f"📎 عرض ملف PDF ({i+1})", sec_url, use_container_width=True)
                        except Exception:
                            st.caption("تعذر تحميل المرفق")

                # تعديل أو حذف الشاهد
                ed_col, del_col = st.columns(2)
                with ed_col:
                    with st.expander("✏️ تعديل الشاهد"):
                        with st.form(f"edit_form_{ev['id']}"):
                            new_t = st.text_input("عنوان الشاهد:", value=ev['title'])
                            new_d = st.text_area("وصف الشاهد:", value=ev.get('description', ''))
                            new_files = st.file_uploader("استبدال المرفقات (اختياري):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key=f"up_{ev['id']}")
                            if st.form_submit_button("حفظ التعديل 💾", type="primary"):
                                supabase.table("evidences").update({"title": new_t, "description": new_d}).eq("id", ev['id']).execute()
                                if new_files:
                                    old_paths = [f['file_url'] for f in files]
                                    if old_paths:
                                        supabase.storage.from_("private-achievements").remove(old_paths)
                                    supabase.table("evidence_files").delete().eq("evidence_id", ev['id']).execute()
                                    for nf in new_files:
                                        ext = nf.name.split('.')[-1]
                                        path = f"{ev['id']}/{uuid.uuid4()}.{ext}"
                                        supabase.storage.from_("private-achievements").upload(path=path, file=nf.getvalue(), file_options={"content-type": nf.type})
                                        supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": path, "file_type": nf.type}).execute()
                                st.success("تم التحديث!")
                                time.sleep(0.5)
                                st.rerun()
                with del_col:
                    with st.expander("🗑️ حذف الشاهد"):
                        st.warning("هل أنت متأكد من حذف الشاهد ومرفقاته؟")
                        if st.button("تأكيد الحذف النهائي", key=f"confirm_del_{ev['id']}", type="primary"):
                            old_paths = [f['file_url'] for f in files]
                            if old_paths:
                                supabase.storage.from_("private-achievements").remove(old_paths)
                            supabase.table("evidences").delete().eq("id", ev['id']).execute()
                            st.success("تم الحذف!")
                            time.sleep(0.5)
                            st.rerun()

        st.write("---")

        # جلب البنود الفرعية (من قاعدة البيانات أو من القائمة الافتراضية)
        try:
            sub_res = supabase.table("sub_items").select("*").eq("standard_id", std_id).execute()
            db_subs = [item['title'] for item in sub_res.data] if sub_res.data else []
        except Exception:
            db_subs = []
            
        sub_options = db_subs if db_subs else DEFAULT_SUB_ITEMS.get(std_id, [])

        st.markdown("#### 💡 أفكار تبدأ منها (بنود التقييم الفرعية)")
        for idea in sub_options:
            st.markdown(f"""
                <div class="idea-card">
                    <span>💡 {idea}</span>
                    <span style="color:#146c59; font-weight:bold;">⊕</span>
                </div>
            """, unsafe_allow_html=True)

        # نموذج إضافة شاهد لهذا البند
        st.markdown("#### ➕ إضافة شاهد لهذا البند")
        with st.form(f"add_ev_std_{std_id}", clear_on_submit=True):
            chosen_idea = st.selectbox("اختر البند الفرعي:", sub_options + ["أخرى (كتابة عنوان مخصص)"])
            custom_title = st.text_input("عنوان مخصص للشاهد (اتركه فارغاً إذا اخترت من القائمة أعلاه):")
            desc = st.text_area("وصف الشاهد (الهدف، التنفيذ، الأثر):")
            uploaded_files = st.file_uploader("ارفع المرفقات (صور أو PDF - يدعم عدة ملفات):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
            
            if st.form_submit_button("حفظ الشاهد ورفع المرفقات 💾", type="primary", use_container_width=True):
                final_title = custom_title.strip() if (chosen_idea == "أخرى (كتابة عنوان مخصص)" or custom_title.strip()) else chosen_idea
                if final_title and uploaded_files and active_year:
                    with st.spinner("جاري رفع المرفقات وحفظ الشاهد..."):
                        ev_data = supabase.table("evidences").insert({
                            "standard_id": std_id,
                            "year_id": active_year['id'],
                            "title": final_title,
                            "description": desc
                        }).execute()
                        new_id = ev_data.data[0]['id']
                        for up_file in uploaded_files:
                            ext = up_file.name.split('.')[-1]
                            path = f"{new_id}/{uuid.uuid4()}.{ext}"
                            supabase.storage.from_("private-achievements").upload(
                                path=path,
                                file=up_file.getvalue(),
                                file_options={"content-type": up_file.type}
                            )
                            supabase.table("evidence_files").insert({
                                "evidence_id": new_id,
                                "file_url": path,
                                "file_type": up_file.type
                            }).execute()
                        st.success("تم حفظ الشاهد بنجاح!")
                        time.sleep(0.7)
                        st.rerun()
                else:
                    st.warning("يرجى اختيار العنوان وإرفاق ملف واحد على الأقل.")

        # إمكانية إضافة بند فرعي جديد للقائمة
        with st.expander("⚙️ إضافة فكرة / بند فرعي جديد لهذا المعيار"):
            with st.form(f"new_sub_{std_id}", clear_on_submit=True):
                new_sub_title = st.text_input("اسم البند الفرعي الجديد:")
                if st.form_submit_button("إضافة للقائمة"):
                    if new_sub_title:
                        supabase.table("sub_items").insert({"standard_id": std_id, "title": new_sub_title}).execute()
                        st.success("تمت الإضافة!")
                        time.sleep(0.5)
                        st.rerun()

    # ----------------------------------------
    # ➕ 3. صفحة الإضافة السريعة
    # ----------------------------------------
    elif st.session_state.current_page == 'quick_add':
        st.markdown("### ➕ إضافة شاهد سريع")
        std_dict = {f"{s['id']}. {s['title']}": s['id'] for s in stds}
        selected_std_label = st.selectbox("اختر البند الرئيسي:", list(std_dict.keys()))
        sel_std_id = std_dict[selected_std_label]
        
        ideas = DEFAULT_SUB_ITEMS.get(sel_std_id, [])
        with st.form("quick_add_form", clear_on_submit=True):
            chosen_idea = st.selectbox("اختر الشاهد الفرعي:", ideas + ["أخرى..."])
            custom_t = st.text_input("أو اكتب عنواناً مخصصاً:")
            desc = st.text_area("وصف الشاهد:")
            up_files = st.file_uploader("المرفقات (صور أو PDF):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
            if st.form_submit_button("حفظ الشاهد 💾", type="primary", use_container_width=True):
                final_t = custom_t.strip() if custom_t.strip() else chosen_idea
                if final_t and up_files and active_year:
                    ev_data = supabase.table("evidences").insert({
                        "standard_id": sel_std_id,
                        "year_id": active_year['id'],
                        "title": final_t,
                        "description": desc
                    }).execute()
                    new_id = ev_data.data[0]['id']
                    for f in up_files:
                        ext = f.name.split('.')[-1]
                        path = f"{new_id}/{uuid.uuid4()}.{ext}"
                        supabase.storage.from_("private-achievements").upload(path=path, file=f.getvalue(), file_options={"content-type": f.type})
                        supabase.table("evidence_files").insert({"evidence_id": new_id, "file_url": path, "file_type": f.type}).execute()
                    st.success("تم الحفظ بنجاح!")
                    time.sleep(0.7)
                    navigate_to('standard_view', sel_std_id)
                else:
                    st.warning("يرجى إكمال البيانات وإرفاق ملف.")

    # ----------------------------------------
    # 📄 4. صفحة التقارير والطباعة (A4 كامل)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.markdown("### 📄 تصدير وطباعة ملف الإنجاز (PDF)")
        if not active_year:
            st.error("لا توجد سنة دراسية نشطة.")
        else:
            if st.button("تجهيز التقرير الاحترافي للطباعة 🖨️", type="primary", use_container_width=True):
                with st.spinner("جاري تجهيز صفحات A4..."):
                    ev_res = supabase.table("evidences").select("*, standards(title, weight, target_evidences), evidence_files(*)").eq("year_id", active_year['id']).order("standard_id").execute()
                    all_evidences = ev_res.data
                    
                    total_evidences = len(all_evidences)
                    active_stds = [s for s in stds if len([e for e in all_evidences if e['standard_id'] == s['id']]) > 0]
                    covered_stds = len(active_stds)
                    
                    html_content = """
                    <!DOCTYPE html>
                    <html dir="rtl" lang="ar">
                    <head>
                        <meta charset="UTF-8">
                        <title>ملف الإنجاز المهني</title>
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
                            body { font-family: 'Tajawal', sans-serif; background-color: #cbd5e1; margin: 0; padding: 20px; }
                            .page { background-color: white; width: 210mm; height: 296mm; padding: 10mm 15mm; margin: 0 auto 20mm auto; box-shadow: 0 10px 20px rgba(0,0,0,0.15); box-sizing: border-box; page-break-after: always; page-break-inside: avoid; display: flex; flex-direction: column; overflow: hidden; }
                            .cover-page { border: 4px solid #146c59; border-radius: 15px; padding: 40px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; box-sizing: border-box; }
                            .cover-title { color: #146c59; font-size: 40px; font-weight: bold; margin-bottom: 15px; }
                            .cover-subtitle { font-size: 22px; margin-bottom: 50px; font-weight: bold; }
                            .info-table { width: 85%; border-collapse: collapse; margin: 0 auto; font-size: 18px; }
                            .info-table th, .info-table td { border: 1px solid #ccc; padding: 14px; text-align: center; }
                            .info-table th { background-color: #f8fafc; width: 32%; font-weight: bold; color: #146c59; }
                            .header-container { display: flex; justify-content: space-between; border-bottom: 2px solid #146c59; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; font-weight: bold; flex-shrink: 0; }
                            .header-right { color: #146c59; }
                            .header-left { text-align: left; }
                            .index-title { color: #146c59; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
                            .index-table { width: 100%; border-collapse: collapse; font-size: 15px; }
                            .index-table th { background-color: #e6f2ef; color: #146c59; padding: 10px; text-align: center; border-bottom: 2px solid #146c59; }
                            .index-table td { padding: 10px; text-align: center; border-bottom: 1px solid #e2e8f0; }
                            .content-wrapper { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }
                            .std-header { background-color: #146c59; color: white; padding: 10px 15px; font-size: 16px; font-weight: bold; border-radius: 8px 8px 0 0; flex-shrink: 0; }
                            .ev-header { background-color: #0f5243; color: white; padding: 8px 15px; font-size: 14px; margin-bottom: 15px; border-radius: 0 0 8px 8px; flex-shrink: 0; }
                            .meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; flex-shrink: 0; }
                            .meta-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; text-align: center; border-radius: 8px; }
                            .meta-title { font-size: 12px; color: #64748b; font-weight: bold; }
                            .meta-value { font-size: 14px; font-weight: bold; color: #0f172a; }
                            .desc-section { margin-bottom: 15px; line-height: 1.6; font-size: 14px; padding: 10px; background: #fafafa; border-right: 4px solid #146c59; border-radius: 5px; flex-shrink: 0; }
                            .images-grid { flex-grow: 1; display: flex; justify-content: center; align-items: center; gap: 15px; min-height: 0; padding: 5px 0; overflow: hidden; }
                            .images-grid img { max-width: 100%; max-height: 100%; object-fit: contain; border: 1px solid #cbd5e1; border-radius: 8px; }
                            .pdf-notice { background: #f1f5f9; padding: 10px; text-align: center; border-radius: 8px; font-size: 13px; color: #334155; margin-bottom: 10px; border: 1px dashed #94a3b8; flex-shrink: 0; }
                            .signatures { display: flex; justify-content: space-between; margin-top: auto; border-top: 2px solid #e2e8f0; padding-top: 15px; text-align: center; flex-shrink: 0; }
                            .sig-box { width: 40%; }
                            @media print {
                                body { background-color: white; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                                .page { width: 210mm; height: 296mm; margin: 0; padding: 10mm 15mm; box-shadow: none; border: none; }
                                @page { size: A4 portrait; margin: 0; }
                            }
                        </style>
                    </head>
                    <body>
                    """
                    
                    html_content += f"""
                    <div class="page">
                        <div class="cover-page">
                            <div class="cover-title">ملف الإنجاز</div>
                            <div class="cover-subtitle">شواهد الأداء الوظيفي</div>
                            <table class="info-table">
                                <tr><th>الاسم</th><td>{user_info['full_name']}</td></tr>
                                <tr><th>التخصص</th><td>{user_info['specialization']}</td></tr>
                                <tr><th>المدرسة</th><td>{user_info['school_name']}</td></tr>
                                <tr><th>المرحلة</th><td>{user_info['education_stage']}</td></tr>
                                <tr><th>المدينة</th><td>{user_info['city']}</td></tr>
                                <tr><th>دورة الأداء</th><td>{active_year['year_name']}</td></tr>
                                <tr><th>عدد الشواهد</th><td>{total_evidences}</td></tr>
                                <tr><th>البنود المغطاة</th><td>{covered_stds} من {len(stds)}</td></tr>
                            </table>
                        </div>
                    </div>
                    """
                    
                    shared_header = f"""
                    <div class="header-container">
                        <div class="header-right">
                            {user_info['full_name']}<br>
                            <span style="font-size:11px; font-weight:normal; color:#666;">شواهد الأداء الوظيفي - دورة {active_year['year_name']}</span>
                        </div>
                        <div class="header-left">
                            المملكة العربية السعودية<br>
                            <span style="font-size:11px; font-weight:normal; color:#666;">وزارة التعليم - {user_info['school_name']}</span>
                        </div>
                    </div>
                    """
                    
                    html_content += f"""
                    <div class="page">
                        {shared_header}
                        <div class="index-title">فهرس البنود المنجزة</div>
                        <table class="index-table">
                            <tr><th>م</th><th>البند</th><th>الوزن</th><th>الشواهد المرفوعة</th><th>المستهدف</th></tr>
                    """
                    for std in stds:
                        count = len([e for e in all_evidences if e['standard_id'] == std['id']])
                        if count == 0:
                            continue
                        target = std.get('target_evidences', 3)
                        html_content += f"<tr><td>{std['id']}</td><td style='text-align:right;'>{std['title']}</td><td>{std['weight']}%</td><td style='color:#146c59; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
                    html_content += "</table></div>"
                    
                    for ev in all_evidences:
                        std = ev['standards']
                        created_date = ev['created_at'][:10]
                        files = ev.get('evidence_files', [])
                        img_html = ""
                        pdf_count = 0
                        for f in files:
                            if f.get('file_type', '').startswith('image/'):
                                url_res = supabase.storage.from_("private-achievements").create_signed_url(f['file_url'], 3600)
                                img_html += f"<img src='{url_res['signedURL']}'>"
                            elif f.get('file_type') == 'application/pdf':
                                pdf_count += 1
                                
                        pdf_notice = f"<div class='pdf-notice'>📌 يوجد مرفق PDF عدد ({pdf_count}) محفوظ في النظام.</div>" if pdf_count > 0 else ""
                        images_section = f"<div class='images-grid'>{img_html}</div>" if img_html else ""
                        
                        html_content += f"""
                        <div class="page">
                            {shared_header}
                            <div class="content-wrapper">
                                <div class="std-header">{ev['standard_id']}. {std['title']} · الوزن {std['weight']}%</div>
                                <div class="ev-header">الشاهد: {ev['title']}</div>
                                <div class="meta-grid">
                                    <div class="meta-box"><div class="meta-title">تاريخ التنفيذ / الرفع</div><div class="meta-value">{created_date}</div></div>
                                    <div class="meta-box"><div class="meta-title">نوع الشاهد</div><div class="meta-value">شاهد موثق</div></div>
                                </div>
                                <div class="desc-section"><strong>الوصف:</strong><br>{ev.get('description') or 'لا يوجد وصف مضاف.'}</div>
                                {pdf_notice}
                                {images_section}
                            </div>
                            <div class="signatures">
                                <div class="sig-box">
                                    <div style="color:#666; font-size:12px; margin-bottom:20px;">المعلم:</div>
                                    <div style="font-weight:bold;">{user_info['full_name']}</div>
                                </div>
                                <div class="sig-box">
                                    <div style="color:#666; font-size:12px; margin-bottom:20px;">مدير المدرسة:</div>
                                    <div style="font-weight:bold;">{user_info['principal_name']}</div>
                                </div>
                            </div>
                        </div>
                        """
                    
                    html_content += "</body></html>"
                    safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    
                    components.html(f"""
                        <div style="text-align: center; margin-top: 10px;">
                            <button onclick="openPrintWindow()" style="width: 100%; padding: 15px; background-color: #146c59; color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; font-family: 'Tajawal', sans-serif;">
                                🖨️ فتح التقرير للطباعة (A4)
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
                    """, height=85)

    # ----------------------------------------
    # ⚙️ 5. صفحة الإعدادات والنسخ الاحتياطي
    # ----------------------------------------
    elif st.session_state.current_page == 'settings':
        st.markdown("### ⚙️ إعدادات الحساب والنسخ الاحتياطي")
        t1, t2, t3 = st.tabs(["👤 بيانات المعلم والمدرسة", "💾 النسخ الاحتياطي", "🚪 الخروج"])
        
        with t1:
            with st.form("profile_form"):
                c1, c2 = st.columns(2)
                with c1:
                    n_name = st.text_input("اسم المعلم:", value=user_info['full_name'])
                    n_spec = st.text_input("التخصص:", value=user_info['specialization'])
                    n_city = st.text_input("المدينة:", value=user_info['city'])
                with c2:
                    n_school = st.text_input("اسم المدرسة:", value=user_info['school_name'])
                    n_stage = st.text_input("المرحلة الدراسية:", value=user_info['education_stage'])
                    n_prin = st.text_input("اسم مدير المدرسة:", value=user_info['principal_name'])
                
                if st.form_submit_button("حفظ البيانات 💾", type="primary", use_container_width=True):
                    try:
                        supabase.table("user_profile").upsert({
                            "id": 1,
                            "full_name": n_name,
                            "specialization": n_spec,
                            "school_name": n_school,
                            "education_stage": n_stage,
                            "city": n_city,
                            "principal_name": n_prin
                        }).execute()
                        st.success("تم حفظ البيانات بنجاح!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"تأكد من إنشاء جدول user_profile في Supabase: {e}")

        with t2:
            st.write("تصدير نسخة احتياطية كاملة لبياناتك بصيغة JSON:")
            if st.button("📦 تجهيز ملف النسخة الاحتياطية", type="primary", use_container_width=True):
                backup = {
                    "standards": stds,
                    "evidences": evidences
                }
                st.download_button(
                    label="⬇️ تحميل النسخة الاحتياطية (JSON)",
                    data=json.dumps(backup, ensure_ascii=False, indent=4),
                    file_name=f"portfolio_backup_{datetime.date.today()}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with t3:
            if st.button("🚪 تسجيل الخروج من الحساب", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.rerun()

    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

# ==========================================
# 7. نقطة تشغيل التطبيق
# ==========================================
if st.session_state.user is None:
    login_page()
else:
    main_app()
