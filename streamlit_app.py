import streamlit as st
from supabase import create_client
import time
import uuid
import json
import datetime
import zipfile
import urllib.request
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape
from hijri_converter import Gregorian
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(
    page_title="منصة زياد الذكية | ملف الإنجاز المهني",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. منظومة المظاهر (Themes) المتعددة
# ==========================================
THEMES = {
    "emerald": {
        "name": "🟢 الأخضر الوزاري الفاخر",
        "primary": "#0f5243",
        "primary_light": "#146c59",
        "primary_dark": "#09352b",
        "bg": "#f4f6f5",
        "accent": "#d97706",
        "tint": "#e6f2ef"
    },
    "royal": {
        "name": "🔵 الأزرق الملكي الاحترافي",
        "primary": "#1e3a8a",
        "primary_light": "#2563eb",
        "primary_dark": "#172554",
        "bg": "#f0f4f8",
        "accent": "#0284c7",
        "tint": "#dbeafe"
    },
    "bronze": {
        "name": "🟤 الذهبي الكلاسيكي الفاخر",
        "primary": "#78350f",
        "primary_light": "#92400e",
        "primary_dark": "#451a03",
        "bg": "#faf6f0",
        "accent": "#b45309",
        "tint": "#fef3c7"
    },
    "slate": {
        "name": "⚫ الرمادي العصري الرسمي",
        "primary": "#1e293b",
        "primary_light": "#334155",
        "primary_dark": "#0f172a",
        "bg": "#f1f5f9",
        "accent": "#475569",
        "tint": "#e2e8f0"
    }
}

# ==========================================
# 3. البنود الفرعية الافتراضية للمعايير الـ 11
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
# 4. محرك الصياغة المزدوج (Gemini 2.5 Flash + محرك القوالب التربوية الذكي)
# ==========================================
PEDAGOGICAL_CONTEXT = {
    1: {
        "target": "المجتمع المدرسي واللجان التنظيمية والطلاب",
        "verbs": ["الالتزام التام بتطبيق", "توثيق وتفعيل", "المبادرة بتنفيذ"],
        "outcomes": ["تعزيز الانضباط المدرسي واستقرار سير العملية التعليمية", "ترسيخ القيم الوطنية والمهنية داخل البيئة المدرسية", "رفع كفاءة العمل التنظيمي والتكامل مع إدارة المدرسة"]
    },
    2: {
        "target": "الزملاء المعلمون ومجتمعات التعلم المهنية",
        "verbs": ["المشاركة الفاعلة في", "نقل الخبرة وتطبيق", "تفعيل التطوير المهني عبر"],
        "outcomes": ["تبادل الخبرات التربوية وتجويد الممارسات التدريسية", "تطوير الكفايات المهنية وتطبيق المستجدات التربوية داخل الصف", "إثراء مجتمع التعلم المهني بالمدرسة"]
    },
    3: {
        "target": "أولياء أمور الطلاب والأسرة",
        "verbs": ["مد جسور التواصل التربوي عبر", "تفعيل الشراكة الأسرية من خلال", "تنظيم وتوثيق"],
        "outcomes": ["تعزيز الشراكة الفاعلة بين المدرسة والمنزل لدعم تعلم الطلاب", "إطلاع أولياء الأمور بشكل دوري ومنظم على تقدم أبنائهم", "توحيد الجهود التربوية لرفع المستوى التحصيلي والسلوكي"]
    },
    4: {
        "target": "طلاب الصف الدراسي بمختلف أنماط تعلمهم (السمعي، البصري، الحركي)",
        "verbs": ["توظيف وتطبيق", "تنويع طرائق التدريس باستخدام", "تصميم وتنفيذ موقف تعليمي قائم على"],
        "outcomes": ["مراعاة الفروق الفردية ورفع دافعية المتعلمين نحو المشاركة الفاعلة", "تحويل المتعلم إلى محور أساسي في العملية التعليمية وتنمية مهارات التفكير", "تحسين جودة الفهم والاستيعاب لدى جميع فئات الطلاب"]
    },
    5: {
        "target": "الطلاب المستهدفون في خطط المعالجة التعليمية والإثراء",
        "verbs": ["إعداد وتطبيق", "بناء وتنفيذ", "متابعة تقدم الطلاب عبر"],
        "outcomes": ["ردم الفجوات المهارية ومعالجة الفاقد التعليمي بصورة منهجية", "الارتقاء بمستوى التحصيل الدراسي ورفع نسب الإتقان في المهارات الأساسية", "تنمية قدرات الطلاب المتميزين وتحفيزهم نحو الإبداع"]
    },
    6: {
        "target": "المنهج الدراسي وطلاب الصف الدراسي",
        "verbs": ["التخطيط المنهجي المسبق عبر", "تنظيم وتنفيذ", "بناء ومواءمة"],
        "outcomes": ["ضمان تسلسل الخبرات التعليمية وتغطية المقررات وفق الإطار الزمني المعتمد", "تصميم أنشطة تعلم متمايزة تلائم مستويات الطلاب وقدراتهم", "تحقيق الترابط الوثيق بين أهداف التعلم وأدوات التقويم"]
    },
    7: {
        "target": "الطلاب عبر البيئة الصفية والمنصات الرقمية",
        "verbs": ["دمج التقنية الحديثة وتوظيف", "تصميم وتفعيل", "إثراء الموقف التعليمي باستخدام"],
        "outcomes": ["تسهيل استيعاب المفاهيم المجردة وتحويلها إلى خبرات تفاعلية مشوقة", "تفعيل أدوات التعلم الرقمي ومنصة مدرستي بكفاءة عالية", "تنمية المهارات الرقمية وزيادة التفاعل الصفي"]
    },
    8: {
        "target": "البيئة الصفية وطلاب الفصل",
        "verbs": ["تهيئة وتنظيم", "تصميم وتفعيل", "ابتكار وتجهيز"],
        "outcomes": ["توفير بيئة تعليمية آمنة وجاذبة ومحفزة على التعلم والإبداع", "تعزيز الدافعية الإيجابية والانتماء الصفي لدى المتعلمين", "تلبية الاحتياجات النفسية والتربوية للطلاب"]
    },
    9: {
        "target": "طلاب الفصل الدراسي",
        "verbs": ["إرساء وتطبيق", "تنظيم وإدارة", "متابعة وضبط"],
        "outcomes": ["تحقيق بيئة صفية منظمة يسودها الاحترام المتبادل والانضباط الذاتي", "استثمار زمن الحصة الدراسية بفاعلية قصوى لصالح تعلم الطلاب", "تعزيز السلوكيات الإيجابية وتوزيع الأدوار القيادية والتعاونية"]
    },
    10: {
        "target": "الطلاب وفق نتائج الاختبارات التشخيصية والفترية",
        "verbs": ["إجراء التحليل الإحصائي والتربوي لـ", "تشخيص مستويات الطلاب عبر", "قراءة وتفسير مؤشرات"],
        "outcomes": ["التحديد الدقيق لنقاط القوة وأولويات التحسين في المهارات المستهدفة", "اتخاذ قرارات تدريسية مبنية على البيانات والنتائج الفعلية", "توجيه الخطط العلاجية والإثرائية بدقة وموضوعية"]
    },
    11: {
        "target": "طلاب الصف الدراسي",
        "verbs": ["تنويع أدوات وأساليب القياس عبر", "تصميم وتطبيق", "تقييم أداء المتعلمين باستخدام"],
        "outcomes": ["قياس مدى تحقق نواتج التعلم بموضوعية وشمولية", "تفعيل التقويم من أجل التعلم وتقديم تغذية راجعة فورية وبنّاءة", "تمكين الطلاب من ممارسة التقويم الذاتي وتقويم الأقران"]
    }
}

def generate_smart_evidence_text(std_id, std_title, ev_title, raw_notes="", variant=0):
    clean_notes = raw_notes.strip()
    ctx = PEDAGOGICAL_CONTEXT.get(std_id, PEDAGOGICAL_CONTEXT[4])
    
    gemini_key = st.secrets.get("gemini_api_key", "") or st.session_state.get("custom_gemini_key", "")
    if gemini_key:
        try:
            prompt_text = (
                f"أنت خبير تربوي في وزارة التعليم السعودية. قم بصياغة توثيق احترافي لشاهد أداء وظيفي للمعلم.\n"
                f"المعيار: {std_id}. {std_title}\n"
                f"عنوان الشاهد: {ev_title}\n"
                f"الكلمات المفتاحية أو النقاط المدخلة من المعلم: {clean_notes if clean_notes else 'تنفيذ الشاهد وفق الخطة المعتمدة'}\n\n"
                f"أرجع النتيجة بصيغة JSON فقط يحتوي على المفاتيح التالية باللغة العربية الفصحى:\n"
                f'{{"description": "فقرة وصفية رسمية من 3 إلى 4 أسطر تدمج النقاط المدخلة وتربطها بالمعيار وأثرها على المتعلمين", '
                f'"goal": "هدف تربوي مركز في سطر واحد", '
                f'"target_group": "الفئة المستهدفة بدقة", '
                f'"implementation": "آلية التنفيذ الميداني في سطر واحد", '
                f'"impact": "الأثر التربوي المتحقق في سطر واحد"}}'
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                raw_json = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                parsed = json.loads(raw_json)
                if parsed.get("description"):
                    return {
                        "description": parsed.get("description", ""),
                        "goal": parsed.get("goal", f"تحقيق مستهدفات معيار ({std_title}) عبر ({ev_title})."),
                        "target_group": parsed.get("target_group", ctx["target"]),
                        "implementation": parsed.get("implementation", clean_notes or ev_title),
                        "impact": parsed.get("impact", ctx["outcomes"][0]),
                        "engine": "gemini-2.5-flash"
                    }
        except Exception:
            pass

    is_already_long = len(clean_notes) > 160 and ("مؤشرات" in clean_notes or "مستهدفات" in clean_notes or "انطلاقاً" in clean_notes)
    if is_already_long:
        seed_notes = st.session_state.get(f"last_raw_notes_{std_id}", "")
    else:
        seed_notes = clean_notes
        st.session_state[f"last_raw_notes_{std_id}"] = seed_notes

    verb = ctx["verbs"][variant % len(ctx["verbs"])]
    outcome = ctx["outcomes"][variant % len(ctx["outcomes"])]
    outcome_alt = ctx["outcomes"][(variant + 1) % len(ctx["outcomes"])]
    target_group = ctx["target"]

    if seed_notes:
        focus_phrase = f"مع التركيز التطبيقي على ({seed_notes})"
        impl_detail = f"تطبيق ({ev_title}) ميدانياً من خلال ({seed_notes}) وتوثيق الشواهد المرتبطة به."
    else:
        focus_phrase = "وفق الأسس التربوية الحديثة والخطة الفصلية المعتمدة"
        impl_detail = f"الإعداد المنهجي والتنفيذ الميداني لـ ({ev_title}) ومتابعة أثره بشكل دوري."

    style_templates = [
        (
            f"انطلاقاً من مستهدفات معيار «{std_title}»، تم {verb} «{ev_title}» {focus_phrase}، "
            f"حيث جرى تهيئة المتطلبات اللازمة وتنفيذ الإجراءات بصورة منظمة تضمن جودة التطبيق. "
            f"وقد أسهمت هذه الممارسة بفاعلية في {outcome}، وانعكس أثرها إيجاباً على {target_group}."
        ),
        (
            f"تحقيقاً لمؤشرات الأداء المهني في بند «{std_title}»، قمت بـ{verb} «{ev_title}» {focus_phrase}. "
            f"وقد تضمن العمل التخطيط المسبق والتنفيذ المرحلي والتقويم المستمر للمخرجات، "
            f"مما أثمر عن {outcome_alt}، ورفع مستوى التفاعل والإنجاز لدى {target_group}."
        ),
        (
            f"في إطار تجويد الممارسات التعليمية والتربوية ضمن عنصر «{std_title}»، تم {verb} «{ev_title}» {focus_phrase}. "
            f"وقد أظهرت نتائج المتابعة والتوثيق فاعلية هذا الإجراء في {outcome}، "
            f"بما يلبي الاحتياجات الفعلية لـ{target_group} ويحقق غايات التميز المدرسي."
        ),
        (
            f"توثيقاً للممارسات المهنية الداعمة لمعيار «{std_title}»، جرى العمل على {verb} «{ev_title}» {focus_phrase}، "
            f"وفق منهجية تكاملية تراعي الدقة والجودة في الأداء. "
            f"وقد نتج عن ذلك {outcome_alt}، وتحقيق أثر تربوي مستدام لدى {target_group}."
        )
    ]

    chosen_description = style_templates[variant % len(style_templates)]
    goal_text = f"تحقيق مؤشرات معيار ({std_title}) والارتقاء بجودة الأداء عبر ({ev_title})."

    return {
        "description": chosen_description,
        "goal": goal_text,
        "target_group": target_group,
        "implementation": impl_detail,
        "impact": outcome,
        "engine": "smart-template"
    }

# ==========================================
# 5. الاتصال بقاعدة البيانات والتخزين المؤقت السريع
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_visitor' not in st.session_state:
    st.session_state.is_visitor = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'view_standard_id' not in st.session_state:
    st.session_state.view_standard_id = 0
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'
if 'ai_variant' not in st.session_state:
    st.session_state.ai_variant = 0
if 'custom_gemini_key' not in st.session_state:
    st.session_state.custom_gemini_key = ""

def clear_app_cache():
    st.cache_data.clear()

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id is not None:
        st.session_state.view_standard_id = std_id
    st.rerun()

def run_ai_draft_callback(std_id, std_title, sub_options):
    desc_key = f"draft_desc_{std_id}"
    goal_key = f"draft_goal_{std_id}"
    target_key = f"draft_target_{std_id}"
    impl_key = f"draft_impl_{std_id}"
    impact_key = f"draft_impact_{std_id}"
    title_key = f"title_in_{std_id}"
    idea_key = f"idea_sel_{std_id}"

    chosen_idea = st.session_state.get(idea_key, sub_options[0] if sub_options else "")
    typed_title = st.session_state.get(title_key, "").strip()
    ev_title = typed_title if typed_title else chosen_idea
    current_notes = st.session_state.get(desc_key, "")

    ai_res = generate_smart_evidence_text(
        std_id=std_id,
        std_title=std_title,
        ev_title=ev_title,
        raw_notes=current_notes,
        variant=st.session_state.ai_variant
    )
    st.session_state.ai_variant += 1
    st.session_state[desc_key] = ai_res["description"]
    st.session_state[goal_key] = ai_res["goal"]
    st.session_state[target_key] = ai_res["target_group"]
    st.session_state[impl_key] = ai_res["implementation"]
    st.session_state[impact_key] = ai_res["impact"]
    st.session_state[f"ai_status_{std_id}"] = ai_res["engine"]

@st.cache_data(ttl=180)
def get_user_profile():
    default_profile = {
        "full_name": "زياد المعمري",
        "specialization": "لغة إنجليزية / تربية خاصة",
        "school_name": "ابتدائية عبادة بن قيس الأنصاري",
        "education_stage": "ابتدائي / متوسط",
        "city": "المدينة المنورة",
        "principal_name": "عبدالمجيد الحربي",
        "theme": "emerald",
        "visitor_code": "1448",
        "allow_visitor": True
    }
    try:
        res = supabase.table("user_profile").select("*").eq("id", 1).execute()
        if res.data:
            return {**default_profile, **res.data[0]}
    except Exception:
        pass
    return default_profile

@st.cache_data(ttl=180)
def fetch_all_years():
    res = supabase.table("academic_years").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []

@st.cache_data(ttl=300)
def fetch_standards_and_subs():
    stds = supabase.table("standards").select("*").order("id").execute().data
    try:
        subs = supabase.table("sub_items").select("*").execute().data
    except Exception:
        subs = []
    return stds, subs

@st.cache_data(ttl=120)
def fetch_year_evidences(year_id):
    if not year_id:
        return []
    res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", year_id).order("created_at", desc=True).execute()
    return res.data if res.data else []

@st.cache_data(ttl=1800)
def get_signed_urls_batch(paths_tuple):
    if not paths_tuple:
        return {}
    url_map = {}
    storage_paths = [p for p in paths_tuple if not p.startswith("http")]
    for p in paths_tuple:
        if p.startswith("http"):
            url_map[p] = p
    if storage_paths:
        try:
            res = supabase.storage.from_("private-achievements").create_signed_urls(storage_paths, 3600)
            for item in res:
                if item.get("path") and item.get("signedURL"):
                    url_map[item["path"]] = item["signedURL"]
        except Exception:
            for sp in storage_paths:
                try:
                    single = supabase.storage.from_("private-achievements").create_signed_url(sp, 3600)
                    url_map[sp] = single.get("signedURL", "")
                except Exception:
                    pass
    return url_map

# ==========================================
# 6. محرك توليد ملف Word قابل للتعديل (.docx)
# ==========================================
def generate_editable_docx(user_info, active_year, stds, evidences):
    stds_map = {s['id']: s for s in stds}
    sorted_evs = sorted(evidences, key=lambda x: x.get('standard_id', 0))
    total_ev = len(sorted_evs)
    covered_stds = len(set(e['standard_id'] for e in sorted_evs))

    def w_para(text, bold=False, size_pt=12, color="1E293B", align="right", space_after=140):
        sz = int(size_pt * 2)
        b_tag = "<w:b/><w:bCs/>" if bold else ""
        return f"""
        <w:p>
            <w:pPr>
                <w:bidi/>
                <w:jc w:val="{align}"/>
                <w:spacing w:after="{space_after}"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
                    {b_tag}
                    <w:color w:val="{color}"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:rtl/>
                </w:rPr>
                <w:t>{xml_escape(str(text))}</w:t>
            </w:r>
        </w:p>
        """

    def w_table(rows_data, header_bg="0F5243"):
        tbl_xml = """
        <w:tbl>
            <w:tblPr>
                <w:bidiVisual/>
                <w:tblW w:w="5000" w:type="pct"/>
                <w:tblBorders>
                    <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                    <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                    <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                    <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                </w:tblBorders>
            </w:tblPr>
        """
        for r_idx, row in enumerate(rows_data):
            tbl_xml += "<w:tr>"
            for c_text, is_header in row:
                fill = header_bg if is_header else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                txt_color = "FFFFFF" if is_header else "0F172A"
                tbl_xml += f"""
                <w:tc>
                    <w:tcPr>
                        <w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>
                        <w:tcMar>
                            <w:top w:w="120" w:type="dxa"/>
                            <w:bottom w:w="120" w:type="dxa"/>
                            <w:left w:w="150" w:type="dxa"/>
                            <w:right w:w="150" w:type="dxa"/>
                        </w:tcMar>
                    </w:tcPr>
                    {w_para(c_text, bold=is_header, size_pt=11, color=txt_color, align="center", space_after=0)}
                </w:tc>
                """
            tbl_xml += "</w:tr>"
        tbl_xml += "</w:tbl>"
        return tbl_xml

    body_parts = []
    body_parts.append(w_para("المملكة العربية السعودية - وزارة التعليم", bold=True, size_pt=14, color="0F5243", align="center", space_after=120))
    body_parts.append(w_para("منصة زياد الذكية لتوثيق الأداء المهني", bold=True, size_pt=13, color="B45309", align="center", space_after=300))
    body_parts.append(w_para("ملف الإنجاز المهني الإلكتروني", bold=True, size_pt=24, color="0F5243", align="center", space_after=120))
    body_parts.append(w_para("توثيق شواهد الأداء الوظيفي للمعلم", bold=True, size_pt=15, color="475569", align="center", space_after=400))

    cover_rows = [
        [("البيان", True), ("التفاصيل", True)],
        [("اسم المعلم", False), (user_info.get("full_name", ""), False)],
        [("التخصص", False), (user_info.get("specialization", ""), False)],
        [("المدرسة", False), (user_info.get("school_name", ""), False)],
        [("المرحلة الدراسية", False), (user_info.get("education_stage", ""), False)],
        [("المدينة", False), (user_info.get("city", ""), False)],
        [("مدير المدرسة", False), (user_info.get("principal_name", ""), False)],
        [("العام الدراسي", False), (f"{active_year.get('year_name', '')}هـ", False)],
        [("إجمالي الشواهد الموثقة", False), (f"{total_ev} شاهد ({covered_stds} من {len(stds)} معايير)", False)]
    ]
    body_parts.append(w_table(cover_rows))
    body_parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    body_parts.append(w_para("فهرس معايير الأداء الوظيفي المنجزة", bold=True, size_pt=18, color="0F5243", align="right", space_after=240))
    index_rows = [[("م", True), ("معيار الأداء الوظيفي", True), ("الوزن النسبي", True), ("الشواهد الموثقة", True), ("المستهدف", True)]]
    for s in stds:
        cnt = len([e for e in sorted_evs if e['standard_id'] == s['id']])
        if cnt == 0:
            continue
        index_rows.append([
            (str(s['id']), False),
            (s['title'], False),
            (f"{s['weight']}%", False),
            (str(cnt), False),
            (str(s.get('target_evidences', 3)), False)
        ])
    body_parts.append(w_table(index_rows))
    body_parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    for idx, ev in enumerate(sorted_evs):
        std = stds_map.get(ev['standard_id'], {"title": "", "weight": 10})
        exec_date = ev.get('execution_date') or ev['created_at'][:10]
        files = ev.get('evidence_files', [])
        links_list = [f['file_url'] for f in files if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http')]
        att_summary = f"عدد المرفقات المحفوظة: {len(files)}" + (f" | الرابط: {links_list[0]}" if links_list else "")

        body_parts.append(w_para(f"المعيار {ev['standard_id']}: {std['title']} (الوزن {std['weight']}%)", bold=True, size_pt=16, color="0F5243", align="right", space_after=140))
        ev_rows = [
            [("عنوان الشاهد", True), (ev.get("title", ""), False)],
            [("تاريخ التنفيذ الفعلي", True), (str(exec_date), False)],
            [("وصف الشاهد والأثر", True), (ev.get("description") or "تم تنفيذ الشاهد وتوثيقه وفق خطة توزيع المنهج.", False)],
            [("المرفقات والروابط", True), (att_summary, False)],
            [("المعلم", True), (user_info.get("full_name", ""), False)],
            [("مدير المدرسة", True), (user_info.get("principal_name", ""), False)]
        ]
        body_parts.append(w_table(ev_rows))
        body_parts.append(w_para("ملاحظات إضافية / تعديل:", bold=True, size_pt=11, color="64748B", align="right", space_after=200))
        if idx < len(sorted_evs) - 1:
            body_parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body>
            {''.join(body_parts)}
            <w:sectPr>
                <w:bidi/>
                <w:pgSz w:w="11906" w:h="16838"/>
                <w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>
            </w:sectPr>
        </w:body>
    </w:document>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
        <Default Extension="xml" ContentType="application/xml"/>
        <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    </Types>"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    </Relationships>"""

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as docx_zip:
        docx_zip.writestr("[Content_Types].xml", content_types_xml.strip())
        docx_zip.writestr("_rels/.rels", rels_xml.strip())
        docx_zip.writestr("word/document.xml", document_xml.strip())
    return buf.getvalue()

def generate_excel_csv(stds, evidences):
    stds_map = {s['id']: s['title'] for s in stds}
    lines = ["رقم المعيار,اسم المعيار,عنوان الشاهد,تاريخ التنفيذ,الوصف,عدد المرفقات"]
    for ev in sorted(evidences, key=lambda x: x.get('standard_id', 0)):
        s_id = ev.get('standard_id', '')
        s_title = str(stds_map.get(s_id, '')).replace(',', ' - ')
        title = str(ev.get('title', '')).replace(',', ' - ').replace('\n', ' ')
        exec_d = ev.get('execution_date') or ev.get('created_at', '')[:10]
        desc = str(ev.get('description', '') or '').replace(',', ' - ').replace('\n', ' ')
        f_cnt = len(ev.get('evidence_files', []))
        lines.append(f"{s_id},{s_title},{title},{exec_d},{desc},{f_cnt}")
    return "\ufeff" + "\n".join(lines)

user_info = get_user_profile()
active_theme_key = user_info.get("theme", "emerald")
if active_theme_key not in THEMES:
    active_theme_key = "emerald"
th = THEMES[active_theme_key]

ZIYAD_LOGO_SVG = '<svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="16" fill="white" fill-opacity="0.15"/><rect x="2" y="2" width="60" height="60" rx="14" stroke="white" stroke-opacity="0.35" stroke-width="2"/><path d="M32 14L12 24L32 34L52 24L32 14Z" fill="#FBBF24"/><path d="M20 29V41C20 44.5 25.5 48 32 48C38.5 48 44 44.5 44 41V29L32 35L20 29Z" fill="white"/><path d="M48 26V40" stroke="#FBBF24" stroke-width="3" stroke-linecap="round"/></svg>'

# ==========================================
# 7. التصميم الشامل
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;600;700;800&family=Readex+Pro:wght@400;500;600;700&display=swap');

:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
    --text-color: #0f172a !important;
    --background-color: {th['bg']} !important;
    --secondary-background-color: #ffffff !important;
    --primary-color: {th['primary']} !important;
    color-scheme: light only !important;
    direction: rtl; 
    text-align: right; 
    font-family: 'Readex Pro', 'Cairo', sans-serif;
    background-color: {th['bg']} !important;
    color: #0f172a !important;
    overflow-x: hidden !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overscroll-behavior-x: none !important;
    touch-action: pan-y !important;
}}

header {{visibility: hidden; height: 0 !important;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
.stSidebar {{display: none !important;}}

.block-container {{
    padding: 0.5rem 0.65rem 1.8rem 0.65rem !important;
    max-width: 720px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}}
[data-testid="stVerticalBlock"] {{
    gap: 0.45rem !important;
    max-width: 100% !important;
}}
div.element-container {{
    max-width: 100% !important;
}}

h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {{
    font-family: 'Readex Pro', 'Cairo', sans-serif;
    color: #0f172a !important;
    word-wrap: break-word !important;
}}

span[data-testid="stIconMaterial"], .material-icons, [class*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    direction: ltr !important;
}}

div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input,
input, textarea {{
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: {th['primary']} !important;
}}

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {{
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] svg {{
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    fill: #0f172a !important;
    background-color: transparent !important;
}}

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"] {{
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}}
li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
    background-color: {th['tint']} !important;
    color: {th['primary']} !important;
}}

input::placeholder, textarea::placeholder {{
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}}

div[data-testid="stAlert"], div[data-testid="stAlert"] > div, div[role="alert"] {{
    background-color: {th['tint']} !important;
    background: {th['tint']} !important;
    color: {th['primary_dark']} !important;
    border: 1px solid {th['primary']} !important;
    border-radius: 14px !important;
}}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div[role="alert"] p {{
    color: {th['primary_dark']} !important;
    -webkit-text-fill-color: {th['primary_dark']} !important;
    font-weight: 600 !important;
}}

div[data-testid="stFileUploader"] section {{
    background-color: #ffffff !important;
    border: 1.5px dashed #94a3b8 !important;
    border-radius: 14px !important;
    color: #0f172a !important;
}}
div[data-testid="stFileUploader"] section span,
div[data-testid="stFileUploader"] section small,
div[data-testid="stFileUploader"] section div {{
    color: #475569 !important;
}}
div[data-testid="stFileUploader"] section button {{
    background-color: {th['tint']} !important;
    color: {th['primary']} !important;
    border: 1px solid {th['primary']} !important;
    border-radius: 10px !important;
}}

[data-testid="stForm"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 14px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.03) !important;
}}

[data-testid="stExpander"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    margin-bottom: 6px !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpanderDetails"] {{
    background-color: #ffffff !important;
    color: {th['primary']} !important;
    font-weight: 700 !important;
}}

button[data-baseweb="tab"] {{
    background-color: transparent !important;
    color: #475569 !important;
    font-weight: 700 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {th['primary']} !important;
    border-bottom-color: {th['primary']} !important;
}}

div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {{
    background-color: #e6f4f1 !important;
    color: {th['primary']} !important;
    border: 1px solid #b7e0d6 !important;
    border-radius: 99px !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    padding: 0.35rem 0.9rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}}
div[data-testid="stButton"] button p, div[data-testid="stDownloadButton"] button p {{
    color: {th['primary']} !important;
    -webkit-text-fill-color: {th['primary']} !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}}
div[data-testid="stDownloadButton"] button {{
    background-color: #ffffff !important;
    border: 1.5px solid #0f172a !important;
    border-radius: 14px !important;
    min-height: 48px !important;
}}
div[data-testid="stDownloadButton"] button p {{
    color: #0369a1 !important;
    -webkit-text-fill-color: #0369a1 !important;
    font-size: 14.5px !important;
}}
div[data-testid="stButton"] button:hover {{
    background-color: #d1ebe5 !important;
}}
div[data-testid="stButton"] button[kind="primary"], div[data-testid="stFormSubmitButton"] button, div[data-testid="stDownloadButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, {th['primary']}, {th['primary_light']}) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    min-height: 50px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(15, 82, 67, 0.2) !important;
}}
div[data-testid="stButton"] button[kind="primary"] p, div[data-testid="stFormSubmitButton"] button p, div[data-testid="stDownloadButton"] button[kind="primary"] p {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 15px !important;
}}

div[data-testid="stRadio"] {{
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
}}
div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
    display: none !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    gap: 5px !important;
    background: #ffffff !important;
    padding: 5px !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
    justify-content: space-between !important;
}}
div[data-testid="stRadio"] label {{
    flex: 1 1 0% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 9px 4px !important;
    border-radius: 10px !important;
    background: transparent !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    overflow: hidden !important;
}}
div[data-testid="stRadio"] input[type="radio"],
div[data-testid="stRadio"] label > div:first-child,
div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stRadio"] label p {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}
div[data-testid="stRadio"] label:has(input:checked) {{
    background: {th['primary']} !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
}}
div[data-testid="stRadio"] label:has(input:checked) p {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}}

.hero-wrapper {{
    background: linear-gradient(135deg, {th['primary_dark']} 0%, {th['primary']} 55%, {th['primary_light']} 100%);
    color: white !important;
    padding: 16px 18px;
    border-radius: 20px;
    margin-bottom: 4px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255,255,255,0.12);
    box-sizing: border-box;
    width: 100%;
}}
.hero-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    padding-bottom: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 6px;
}}
.brand-box {{ display: flex; align-items: center; gap: 10px; }}
.brand-title {{ font-size: 15.5px; font-weight: 700; color: #fbbf24 !important; margin: 0; }}
.brand-sub {{ font-size: 10.5px; color: rgba(255,255,255,0.88) !important; margin: 2px 0 0 0; }}
.date-pill {{
    background: rgba(255,255,255,0.14);
    padding: 4px 10px;
    border-radius: 99px;
    font-size: 11px;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2);
}}
.hero-body {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 10px;
}}
.welcome-line {{ font-size: 13px; color: #fde68a !important; font-weight: 600; margin-bottom: 2px; }}
.teacher-name {{ font-size: 21px; font-weight: 800; color: #ffffff !important; margin: 0 0 8px 0; }}
.meta-badges {{ display: flex; flex-wrap: wrap; gap: 5px; }}
.meta-pill {{
    background: rgba(0,0,0,0.25);
    color: #ffffff !important;
    padding: 4px 9px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
}}
.year-badge {{
    background: #fbbf24;
    color: #1e293b !important;
    padding: 6px 12px;
    border-radius: 11px;
    font-size: 12.5px;
    font-weight: 700;
}}

.kpi-grid {{
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px; margin-bottom: 8px; width: 100%; box-sizing: border-box;
}}
.kpi-card {{
    background: #ffffff; border-radius: 14px; padding: 10px 4px; text-align: center;
    border: 1px solid #e2e8f0; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}}
.kpi-val {{ font-size: 18px; font-weight: 700; color: {th['primary']} !important; text-align: center; }}
.kpi-lbl {{ font-size: 10.5px; color: #475569 !important; margin-top: 2px; font-weight: 600; text-align: center; }}

.progress-card {{
    background: #ffffff; padding: 12px 16px; border-radius: 14px; 
    margin-bottom: 6px; border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box;
}}
.progress-bar-bg {{
    background: #e2e8f0; height: 9px; border-radius: 5px; width: 100%; overflow: hidden; margin-top: 6px;
}}
.progress-bar-fill {{
    background: linear-gradient(90deg, {th['primary']}, {th['primary_light']});
    height: 100%; border-radius: 5px;
}}

.std-card {{
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 15px;
    padding: 12px 14px; margin-bottom: 2px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02); width: 100%; box-sizing: border-box;
}}
.std-num {{
    width: 38px; height: 38px; border-radius: 11px;
    background: {th['tint']}; color: {th['primary']} !important;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px; margin-left: 10px; flex-shrink: 0;
}}
.std-num-empty {{ background: #fee2e2; color: #dc2626 !important; }}
.std-title {{ font-size: 14.5px; font-weight: 700; color: #0f172a !important; margin-bottom: 3px; }}
.weight-badge {{
    background: #f1f5f9; color: #475569 !important; font-size: 11px; padding: 2px 8px;
    border-radius: 7px; display: inline-block; font-weight: 600;
}}
.dots-row {{ display: flex; gap: 4px; margin-bottom: 4px; justify-content: flex-end; }}
.dot {{ width: 12px; height: 5px; border-radius: 3px; }}
.dot-on {{ background: {th['primary']}; }}
.dot-off {{ background: #e2e8f0; }}

.thumbs-container {{
    display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 4px 0; align-items: center;
}}
.thumb-link {{
    position: relative; display: inline-block; width: 90px; height: 90px;
    border-radius: 11px; overflow: hidden; border: 2px solid {th['tint']};
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
}}
.thumb-link img {{ width: 100%; height: 100%; object-fit: cover; }}
.thumb-overlay {{
    position: absolute; bottom: 0; left: 0; right: 0;
    background: rgba(0,0,0,0.65); color: #ffffff !important; font-size: 9.5px;
    text-align: center; padding: 2px 0;
}}
.pdf-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 42px; padding: 0 12px; border-radius: 9px;
    background: #f8fafc; border: 1.5px dashed {th['primary']};
    color: {th['primary']} !important; font-weight: 700; font-size: 12px; text-decoration: none;
}}
.ext-link-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 42px; padding: 0 14px; border-radius: 9px;
    background: #eff6ff; border: 1.5px solid #2563eb;
    color: #1d4ed8 !important; font-weight: 700; font-size: 12px; text-decoration: none;
}}

.ev-box {{
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 14px; margin-bottom: 8px; border-right: 4px solid {th['primary']};
    width: 100%; box-sizing: border-box;
}}
.idea-card {{
    background: #ffffff; border: 1px solid #e2e8f0; padding: 9px 12px;
    border-radius: 10px; margin-bottom: 5px; font-size: 12.5px; color: #1e293b !important;
    display: flex; justify-content: space-between; align-items: center;
}}
.visitor-banner {{
    background: #fef3c7; color: #92400e !important; border: 1px solid #f59e0b;
    padding: 8px 14px; border-radius: 11px; margin-bottom: 8px;
    font-weight: 700; font-size: 13px; text-align: center;
}}

.ziyad-footer {{
    margin-top: 28px;
    padding: 16px 12px;
    background: #ffffff;
    border-top: 3px solid {th['primary']};
    border-radius: 14px 14px 8px 8px;
    text-align: center;
    border: 1px solid #e2e8f0;
    width: 100%;
    box-sizing: border-box;
}}
.footer-brand {{ font-size: 13.5px; font-weight: 700; color: {th['primary']} !important; margin-bottom: 3px; text-align: center; }}
.footer-rights {{ font-size: 11px; color: #64748b !important; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# التحقق التلقائي من رابط الزائر (?visitor=CODE)
query_params = st.query_params
if "visitor" in query_params and st.session_state.user is None:
    entered_code = str(query_params["visitor"]).strip()
    saved_code = str(user_info.get("visitor_code", "1448")).strip()
    if user_info.get("allow_visitor", True) and entered_code == saved_code:
        st.session_state.is_visitor = True

# ==========================================
# 8. دوال التاريخ والترحيب والفوتر وإدارة وتعديل ونقل الشاهد
# ==========================================
def get_greeting_and_dates():
    tz = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz)
    today = now.date()
    greeting = "صباح الخير والتميز" if now.hour < 12 else "مساء الخير والعطاء"
    
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    day_name = days_ar[today.weekday()]
    g_date = f"{today.day} {months_ar[today.month - 1]} {today.year}م"
    
    h_obj = Gregorian(today.year, today.month, today.day).to_hijri()
    h_months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    h_date = f"{h_obj.day} {h_months[h_obj.month - 1]} {h_obj.year}هـ"
    
    return greeting, f"{day_name} • {h_date} • {g_date}"

def render_attachments_html(files, signed_urls_map):
    if not files:
        return ""
    thumbs_html = '<div class="thumbs-container">'
    for i, f_rec in enumerate(files):
        f_url = f_rec.get('file_url', '')
        f_type = f_rec.get('file_type', '')
        if f_type == 'external/link' or f_url.startswith('http'):
            thumbs_html += f'<a href="{f_url}" target="_blank" class="ext-link-badge">🔗 فتح الرابط المرفق</a>'
        else:
            sec_url = signed_urls_map.get(f_url, '')
            if not sec_url:
                continue
            if f_type.startswith('image/'):
                thumbs_html += (
                    f'<a href="{sec_url}" target="_blank" class="thumb-link" title="اضغط للتكبير بالحجم الأصلي">'
                    f'<img src="{sec_url}" alt="شاهد"><div class="thumb-overlay">🔍 تكبير</div></a>'
                )
            else:
                thumbs_html += f'<a href="{sec_url}" target="_blank" class="pdf-badge">📄 ملف PDF ({i+1})</a>'
    thumbs_html += '</div>'
    return thumbs_html

def render_evidence_edit_and_delete(ev, signed_urls_map, stds, key_prefix=""):
    """
    مكون موحد لتعديل الشاهد، أو نقله إلى بند آخر، أو حذف أي صورة/مرفق فردي منه دون الحاجة لحذف الشاهد بالكامل
    """
    files = ev.get("evidence_files", [])
    exec_date = ev.get('execution_date') or ev['created_at'][:10]
    existing_links = [f['file_url'] for f in files if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http')]
    current_ext_link = existing_links[0] if existing_links else ""
    storage_files = [f for f in files if f.get('file_type') != 'external/link' and not f.get('file_url', '').startswith('http')]

    std_options_dict = {s['id']: f"البند {s['id']}: {s['title']}" for s in stds}
    std_ids_list = list(std_options_dict.keys())
    current_ev_std_id = ev.get('standard_id', 1)
    default_std_idx = std_ids_list.index(current_ev_std_id) if current_ev_std_id in std_ids_list else 0

    ed_col, del_col = st.columns(2)
    with ed_col:
        with st.expander("✏️ تعديل الشاهد / نقل البند / إدارة الصور"):
            # 1. قسم إدارة وحذف الصور أو ملفات الـ PDF الحالية بشكل فردي ومستقل
            if storage_files:
                st.markdown("**🖼️ المرفقات الحالية (اضغط على حذف تحت أي صورة لإزالتها بمفردها):**")
                att_cols = st.columns(min(len(storage_files), 3))
                for idx_f, f_obj in enumerate(storage_files):
                    with att_cols[idx_f % 3]:
                        f_u = signed_urls_map.get(f_obj['file_url'], '')
                        if f_obj.get('file_type', '').startswith('image/') and f_u:
                            st.markdown(
                                f'<div style="border:1px solid #cbd5e1; border-radius:10px; padding:4px; background:#f8fafc; text-align:center; margin-bottom:4px;">'
                                f'<img src="{f_u}" style="width:100%; height:85px; object-fit:cover; border-radius:7px;">'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div style="border:1px dashed #64748b; border-radius:10px; height:85px; display:flex; align-items:center; justify-content:center; background:#f8fafc; margin-bottom:4px; font-weight:700; font-size:12px;">'
                                f'📄 ملف PDF ({idx_f+1})'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        if st.button(f"🗑️ حذف المرفق ({idx_f+1})", key=f"{key_prefix}del_att_{ev['id']}_{f_obj['id']}", use_container_width=True):
                            try:
                                supabase.storage.from_("private-achievements").remove([f_obj['file_url']])
                            except Exception:
                                pass
                            supabase.table("evidence_files").delete().eq("id", f_obj['id']).execute()
                            clear_app_cache()
                            st.success("تم حذف المرفق المحدد بنجاح مع بقاء الشاهد وبقية بياناته!")
                            time.sleep(0.3)
                            st.rerun()
                st.write("---")

            # 2. نموذج تعديل البيانات ونقل الشاهد إلى بند آخر وإضافة مرفقات جديدة
            with st.form(f"{key_prefix}edit_form_{ev['id']}"):
                new_std_id = st.selectbox(
                    "⇄ البند (المعيار) التابع له الشاهد (اختر بنداً آخر لنقله):",
                    options=std_ids_list,
                    format_func=lambda x: std_options_dict[x],
                    index=default_std_idx,
                    key=f"{key_prefix}move_std_{ev['id']}"
                )
                new_t = st.text_input("عنوان الشاهد:", value=ev['title'])
                try:
                    default_d = datetime.date.fromisoformat(str(exec_date)[:10])
                except Exception:
                    default_d = datetime.date.today()
                new_exec_date = st.date_input("📅 تاريخ التنفيذ:", value=default_d)
                new_d = st.text_area("وصف الشاهد:", value=ev.get('description', ''), height=110)
                
                new_files = st.file_uploader(
                    "📎 رفع صور أو ملفات PDF جديدة (اختياري):",
                    type=["pdf", "jpg", "jpeg", "png"],
                    accept_multiple_files=True,
                    key=f"{key_prefix}up_{ev['id']}"
                )
                upload_mode = st.selectbox(
                    "طريقة التعامل مع المرفقات الجديدة عند رفعها:",
                    [
                        "➕ إضافة الملفات الجديدة إلى المرفقات الحالية",
                        "🔄 استبدال وحذف جميع المرفقات السابقة بالملفات الجديدة"
                    ],
                    key=f"{key_prefix}mode_{ev['id']}"
                )
                new_ext_link = st.text_input("🔗 أو رابط خارجي (امسحه لحذفه أو عدله):", value=current_ext_link, placeholder="https://")
                
                if st.form_submit_button("حفظ التعديلات 💾", type="primary", use_container_width=True):
                    update_payload = {
                        "standard_id": new_std_id,
                        "title": new_t,
                        "description": new_d,
                        "execution_date": str(new_exec_date)
                    }
                    try:
                        supabase.table("evidences").update(update_payload).eq("id", ev['id']).execute()
                    except Exception:
                        update_payload.pop("execution_date", None)
                        supabase.table("evidences").update(update_payload).eq("id", ev['id']).execute()
                        
                    if new_files:
                        if upload_mode.startswith("🔄"):
                            old_storage_paths = [f['file_url'] for f in storage_files]
                            if old_storage_paths:
                                try:
                                    supabase.storage.from_("private-achievements").remove(old_storage_paths)
                                except Exception:
                                    pass
                            for f in storage_files:
                                supabase.table("evidence_files").delete().eq("id", f['id']).execute()
                                
                        for nf in new_files:
                            ext = nf.name.split('.')[-1]
                            path = f"{ev['id']}/{uuid.uuid4()}.{ext}"
                            supabase.storage.from_("private-achievements").upload(path=path, file=nf.getvalue(), file_options={"content-type": nf.type})
                            supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": path, "file_type": nf.type}).execute()

                    if new_ext_link.strip() != current_ext_link:
                        for f in files:
                            if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http'):
                                supabase.table("evidence_files").delete().eq("id", f['id']).execute()
                        if new_ext_link.strip():
                            supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": new_ext_link.strip(), "file_type": "external/link"}).execute()

                    clear_app_cache()
                    if new_std_id != current_ev_std_id:
                        st.success(f"تم حفظ التعديلات ونقل الشاهد إلى ({std_options_dict[new_std_id]}) بنجاح!")
                    else:
                        st.success("تم حفظ التعديلات بنجاح!")
                    time.sleep(0.4)
                    st.rerun()

    with del_col:
        with st.expander("🗑️ حذف الشاهد بالكامل"):
            st.caption("سيتم حذف هذا الشاهد مع كافة مرفقاته نهائياً.")
            if st.button("تأكيد حذف الشاهد نهائياً", key=f"{key_prefix}confirm_del_{ev['id']}", type="primary", use_container_width=True):
                old_storage_paths = [f['file_url'] for f in storage_files]
                if old_storage_paths:
                    try:
                        supabase.storage.from_("private-achievements").remove(old_storage_paths)
                    except Exception:
                        pass
                supabase.table("evidences").delete().eq("id", ev['id']).execute()
                clear_app_cache()
                st.success("تم حذف الشاهد!")
                time.sleep(0.3)
                st.rerun()

def render_footer():
    year_now = datetime.date.today().year
    footer_html = (
        f'<div class="ziyad-footer">'
        f'<div class="footer-brand">🎓 منصة زياد الذكية | نظام ملف الإنجاز المهني الإلكتروني</div>'
        f'<div class="footer-rights">جميع الحقوق محفوظة © {year_now}م - تصميم وتطوير: أ. {user_info["full_name"]}</div>'
        f'</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)

# ==========================================
# 9. صفحة تسجيل الدخول (معلم + زائر)
# ==========================================
def login_page():
    login_hero = (
        f'<div class="hero-wrapper" style="text-align:center;">'
        f'<div style="display:flex; justify-content:center; margin-bottom:8px;">{ZIYAD_LOGO_SVG}</div>'
        f'<div style="font-size:15px; color:#fbbf24 !important; font-weight:700; text-align:center;">منصة زياد الذكية</div>'
        f'<div style="font-size:22px; font-weight:800; margin:5px 0; color:white !important; text-align:center;">ملف الإنجاز المهني الإلكتروني</div>'
        f'<div style="font-size:12.5px; opacity:0.95; color:white !important; text-align:center;">أ. {user_info["full_name"]} • {user_info["school_name"]}</div>'
        f'</div>'
    )
    st.markdown(login_hero, unsafe_allow_html=True)
    
    tab_teacher, tab_visitor = st.tabs(["🔒 دخول المعلم (تحكم كامل)", "👁️ دخول زائر (مشاهدة فقط)"])
    
    with tab_teacher:
        with st.form("login_form"):
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("تسجيل الدخول للنظام", type="primary", use_container_width=True)
            if submit:
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = response.user
                        st.session_state.is_visitor = False
                        st.success("تم تسجيل الدخول بنجاح!")
                        time.sleep(0.3)
                        st.rerun()
                    except Exception:
                        st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                else:
                    st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")

    with tab_visitor:
        st.info("بوابة مخصصة لمدير المدرسة والمشرف التربوي للاطلاع على ملف الإنجاز بواسطة رمز المشاهدة الممنوح من المعلم.")
        with st.form("visitor_form"):
            v_code = st.text_input("أدخل رمز المشاهدة للزائر:", type="password")
            v_submit = st.form_submit_button("👁️ استعراض ملف الإنجاز", type="primary", use_container_width=True)
            if v_submit:
                saved_code = str(user_info.get("visitor_code", "1448")).strip()
                if not user_info.get("allow_visitor", True):
                    st.error("المعلم قام بإيقاف خاصية دخول الزوار حالياً.")
                elif v_code.strip() == saved_code:
                    st.session_state.is_visitor = True
                    st.rerun()
                else:
                    st.error("رمز المشاهدة غير صحيح.")

    render_footer()

# ==========================================
# 10. التطبيق الرئيسي
# ==========================================
def main_app():
    is_visitor = st.session_state.is_visitor

    all_years = fetch_all_years()
    active_years = [y for y in all_years if y.get("is_active")]
    active_year = active_years[0] if active_years else (all_years[0] if all_years else {"id": None, "year_name": "1448"})

    stds, all_subs = fetch_standards_and_subs()
    evidences = fetch_year_evidences(active_year.get('id'))

    all_file_paths = tuple(
        f['file_url'] for ev in evidences for f in ev.get('evidence_files', []) if f.get('file_url')
    )
    signed_urls_map = get_signed_urls_batch(all_file_paths)

    # الهيدر والبنر الاحترافي
    greeting, today_str = get_greeting_and_dates()
    hero_html = (
        f'<div class="hero-wrapper">'
        f'<div class="hero-top">'
        f'<div class="brand-box">{ZIYAD_LOGO_SVG}'
        f'<div><div class="brand-title">منصة زياد الذكية</div>'
        f'<div class="brand-sub">نظام إدارة وتوثيق شواهد الأداء الوظيفي</div></div></div>'
        f'<div class="date-pill">🗓️ {today_str}</div>'
        f'</div>'
        f'<div class="hero-body">'
        f'<div>'
        f'<div class="welcome-line">✨ {greeting}</div>'
        f'<div class="teacher-name">أ. {user_info["full_name"]}</div>'
        f'<div class="meta-badges">'
        f'<span class="meta-pill">🏫 {user_info["school_name"]}</span>'
        f'<span class="meta-pill">📚 {user_info["specialization"]}</span>'
        f'<span class="meta-pill">👔 مدير المدرسة: {user_info["principal_name"]}</span>'
        f'</div>'
        f'</div>'
        f'<div class="year-badge">📁 ملف إنجاز عام {active_year["year_name"]}هـ</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    if is_visitor:
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            st.markdown('<div class="visitor-banner">👁️ تتصفح الملف بوضع الزائر (مشاهدة فقط)</div>', unsafe_allow_html=True)
        with col_v2:
            if st.button("🚪 خروج", use_container_width=True):
                st.session_state.is_visitor = False
                st.query_params.clear()
                st.rerun()

    # شريط التنقل الرئيسي (4 تبويبات متوازنة)
    if is_visitor:
        nav_map = {
            'home': "🏠 الرئيسية",
            'standard_view': "📋 البنود",
            'reports': "📄 التقرير"
        }
    else:
        nav_map = {
            'home': "🏠 الرئيسية",
            'standard_view': "📋 البنود",
            'reports': "📄 التقرير",
            'settings': "⚙️ حسابي"
        }

    nav_keys = list(nav_map.keys())
    curr_page = st.session_state.current_page if st.session_state.current_page in nav_keys else 'home'
    selected_nav = st.radio(
        "nav_bar",
        options=nav_keys,
        format_func=lambda k: nav_map[k],
        index=nav_keys.index(curr_page),
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_nav != st.session_state.current_page:
        st.session_state.current_page = selected_nav
        st.rerun()

    # حساب إحصائيات البنود
    total_stds = len(stds)
    total_ev_count = len(evidences)
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

    less_than_3 = sum(1 for s in stds if ev_by_std[s['id']] < s.get('target_evidences', 3))
    pct = int((stds_with_ev / total_stds) * 100) if total_stds else 0

    # ----------------------------------------
    # 🏠 1. الصفحة الرئيسية
    # ----------------------------------------
    if st.session_state.current_page == 'home':
        kpi_html = (
            f'<div class="kpi-grid">'
            f'<div class="kpi-card"><div class="kpi-val">{total_ev_count}</div><div class="kpi-lbl">إجمالي الشواهد</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_with_ev}/{total_stds}</div><div class="kpi-lbl">البنود المغطاة</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_reached_target}</div><div class="kpi-lbl">حققت المستهدف</div></div>'
            f'<div class="kpi-card"><div class="kpi-val" style="color:#dc2626 !important;">{empty_stds}</div><div class="kpi-lbl">بنود فارغة</div></div>'
            f'</div>'
            f'<div class="progress-card">'
            f'<div style="display:flex; justify-content:space-between; font-weight:700; font-size:13px; color:#1e293b;">'
            f'<span style="color:#1e293b !important;">نسبة تغطية معايير الأداء الوظيفي ({active_year["year_name"]}هـ)</span>'
            f'<span style="color:{th["primary"]} !important;">{pct}%</span>'
            f'</div>'
            f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;"></div></div>'
            f'</div>'
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

        filter_map = {
            'all': f"الكل • {total_stds}",
            'empty': f"فارغة • {empty_stds}",
            'less3': f"أقل من 3 • {less_than_3}"
        }
        f_keys = list(filter_map.keys())
        sel_filter = st.radio(
            "filter_bar",
            options=f_keys,
            format_func=lambda x: filter_map[x],
            index=f_keys.index(st.session_state.filter_mode),
            horizontal=True,
            label_visibility="collapsed"
        )
        if sel_filter != st.session_state.filter_mode:
            st.session_state.filter_mode = sel_filter
            st.rerun()

        for std in stds:
            s_id = std['id']
            count = ev_by_std[s_id]
            target = std.get('target_evidences', 3)

            if st.session_state.filter_mode == 'empty' and count > 0:
                continue
            if st.session_state.filter_mode == 'less3' and count >= target:
                continue

            dots_html = "".join([
                f'<div class="dot {"dot-on" if i < count else "dot-off"}"></div>'
                for i in range(target)
            ])
            
            if count == 0:
                status_txt = '<span style="color:#dc2626 !important; font-size:11.5px; font-weight:600;">لا شواهد بعد</span>'
                num_cls = "std-num std-num-empty"
            elif count >= target:
                status_txt = f'<span style="color:{th["primary"]} !important; font-size:11.5px; font-weight:700;">مكتمل ({count} شواهد)</span>'
                num_cls = "std-num"
            else:
                status_txt = f'<span style="color:{th["accent"]} !important; font-size:11.5px; font-weight:600;">{count} شاهد • بقي {target - count}</span>'
                num_cls = "std-num"

            card_html = (
                f'<div class="std-card">'
                f'<div style="display:flex; align-items:center;">'
                f'<div class="{num_cls}">{s_id}</div>'
                f'<div><div class="std-title">{s_id}. {std["title"]}</div>'
                f'<span class="weight-badge">الوزن النسبي: {std["weight"]}%</span></div>'
                f'</div>'
                f'<div style="text-align:left;"><div class="dots-row">{dots_html}</div>{status_txt}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            btn_label = f"➕ إضافة أو استعراض شواهد البند {s_id}" if not is_visitor else f"👁️ استعراض شواهد البند {s_id}"
            if st.button(btn_label, key=f"open_std_{s_id}", type="primary", use_container_width=True):
                navigate_to('standard_view', s_id)

    # ----------------------------------------
    # 📋 2. صفحة البنود والشواهد (مع التعديل وحذف الصور الفردية ونقل الشاهد لبند آخر)
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        st.markdown("#### 📋 استعراض وإدارة بنود الأداء والشواهد")
        
        options_map = {0: "🔍 عرض ملخص جميع البنود والشواهد المرفوعة"}
        for s in stds:
            options_map[s['id']] = f"البند {s['id']}: {s['title']} ({ev_by_std[s['id']]} شواهد)"
            
        current_std_id = st.session_state.view_standard_id
        if current_std_id not in options_map:
            current_std_id = 0
            
        selected_option = st.selectbox(
            "اختر البند للتنقل السريع أو إضافة شاهد:",
            options=list(options_map.keys()),
            format_func=lambda x: options_map[x],
            index=list(options_map.keys()).index(current_std_id)
        )
        
        if selected_option != st.session_state.view_standard_id:
            st.session_state.view_standard_id = selected_option
            st.rerun()

        if selected_option == 0:
            for s in stds:
                s_evs = [e for e in evidences if e['standard_id'] == s['id']]
                with st.expander(f"{'✅' if len(s_evs)>0 else '⚪'} البند {s['id']}: {s['title']} — ({len(s_evs)} شواهد)", expanded=(len(s_evs) > 0)):
                    if not s_evs:
                        st.caption("لا توجد شواهد مرفوعة في هذا البند حتى الآن.")
                    else:
                        for ev in s_evs:
                            files = ev.get("evidence_files", [])
                            exec_date = ev.get('execution_date') or ev['created_at'][:10]
                            thumbs_html = render_attachments_html(files, signed_urls_map)
                            ev_card = (
                                f'<div class="ev-box">'
                                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">'
                                f'<span style="font-weight:700; color:{th["primary"]} !important;">📄 {ev["title"]}</span>'
                                f'<span style="font-size:12px; color:#64748b !important;">📅 {exec_date}</span>'
                                f'</div>'
                                f'<div style="font-size:13.5px; color:#334155 !important; white-space:pre-line;">{ev.get("description") or ""}</div>'
                                f'{thumbs_html}</div>'
                            )
                            st.markdown(ev_card, unsafe_allow_html=True)
                            if not is_visitor:
                                render_evidence_edit_and_delete(ev, signed_urls_map, stds, key_prefix="all_")
                    if st.button(f"➕ إضافة شاهد جديد للبند {s['id']}", key=f"jump_std_{s['id']}", type="primary", use_container_width=True):
                        navigate_to('standard_view', s['id'])

        else:
            std_id = selected_option
            std_data = [s for s in stds if s['id'] == std_id][0]
            std_evidences = [e for e in evidences if e['standard_id'] == std_id]

            st.markdown(f"##### 📂 الشواهد المرفوعة في البند {std_id}: {std_data['title']} ({len(std_evidences)})")
            if not std_evidences:
                st.info("لا توجد شواهد مرفوعة في هذا البند حتى الآن. يمكنك إضافة شاهد جديد من النموذج بالأسفل.")
            else:
                for ev in std_evidences:
                    files = ev.get("evidence_files", [])
                    exec_date = ev.get('execution_date') or ev['created_at'][:10]
                    thumbs_html = render_attachments_html(files, signed_urls_map)

                    ev_detail_html = (
                        f'<div class="ev-box">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">'
                        f'<span style="font-weight:700; font-size:15.5px; color:{th["primary"]} !important;">📄 {ev["title"]}</span>'
                        f'<span style="background:{th["tint"]}; color:{th["primary_dark"]} !important; padding:4px 12px; border-radius:10px; font-size:12px; font-weight:700;">'
                        f'📅 تاريخ التنفيذ: {exec_date}</span></div>'
                        f'<div style="font-size:13.5px; color:#334155 !important; line-height:1.6; margin-bottom:6px; white-space:pre-line;">{ev.get("description") or ""}</div>'
                        f'{thumbs_html}</div>'
                    )
                    st.markdown(ev_detail_html, unsafe_allow_html=True)

                    if not is_visitor:
                        render_evidence_edit_and_delete(ev, signed_urls_map, stds, key_prefix="single_")

            db_subs = [item['title'] for item in all_subs if item.get('standard_id') == std_id]
            sub_options = db_subs if db_subs else DEFAULT_SUB_ITEMS.get(std_id, [])

            with st.expander("💡 استعراض أمثلة الشواهد المستهدفة لهذا البند", expanded=False):
                for idea in sub_options:
                    st.markdown(f'<div class="idea-card"><span>💡 {idea}</span><span style="color:{th["primary"]} !important; font-weight:bold;">✔</span></div>', unsafe_allow_html=True)

            if not is_visitor:
                st.markdown("##### ➕ إضافة شاهد جديد لهذا البند")
                
                desc_key = f"draft_desc_{std_id}"
                goal_key = f"draft_goal_{std_id}"
                target_key = f"draft_target_{std_id}"
                impl_key = f"draft_impl_{std_id}"
                impact_key = f"draft_impact_{std_id}"
                clear_flag_key = f"clear_draft_flag_{std_id}"

                if st.session_state.get(clear_flag_key, False):
                    for k in [desc_key, goal_key, target_key, impl_key, impact_key]:
                        st.session_state[k] = ""
                    st.session_state[clear_flag_key] = False

                for k in [desc_key, goal_key, target_key, impl_key, impact_key]:
                    if k not in st.session_state:
                        st.session_state[k] = ""

                chosen_idea = st.selectbox(
                    "اختر البند الفرعي المقترح:",
                    sub_options + ["أخرى (كتابة عنوان مخصص)"],
                    key=f"idea_sel_{std_id}"
                )
                default_title_val = "" if chosen_idea == "أخرى (كتابة عنوان مخصص)" else chosen_idea
                final_title = st.text_input("عنوان الشاهد", value=default_title_val, key=f"title_in_{std_id}")

                st.text_area(
                    "وصف مختصر (اختياري)",
                    key=desc_key,
                    placeholder="ماذا نفذت؟ وما الأثر؟ (اكتب نقاطاً سريعة مثل: التعلم النشط، أو اتركه فارغاً ودع الصياغة لنا)",
                    height=110
                )

                st.button(
                    "✨ صياغة الوصف بالذكاء الاصطناعي",
                    key=f"ai_btn_{std_id}",
                    on_click=run_ai_draft_callback,
                    args=(std_id, std_data['title'], sub_options)
                )

                with st.expander("📄 تفاصيل تقرير الشاهد (اختياري: الهدف، المستهدفون، التنفيذ، الأثر)", expanded=False):
                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        st.text_input("الهدف من الشاهد:", key=goal_key, placeholder="مثال: تعزيز الانضباط المدرسي...")
                        st.text_input("المستهدفون:", key=target_key, placeholder="مثال: طلاب الصف الخامس...")
                    with c_d2:
                        st.text_input("آلية التنفيذ:", key=impl_key, placeholder="مثال: برنامج إذاعي ومتابعة يومية...")
                        st.text_input("الأثر المتحقق:", key=impact_key, placeholder="مثال: ارتفاع نسبة التفاعل...")

                exec_date_input = st.date_input("📅 تاريخ التنفيذ (حسب توزيع المنهج):", value=datetime.date.today(), key=f"date_in_{std_id}")
                uploaded_files = st.file_uploader("📎 المرفقات (صور أو ملف PDF):", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key=f"files_in_{std_id}")
                ext_link_input = st.text_input("🔗 أو رابط (يوتيوب، مدرستي، درايف... - اختياري):", placeholder="https://", key=f"link_in_{std_id}")

                if st.button("حفظ الشاهد ورفع المرفقات 💾", type="primary", use_container_width=True, key=f"save_ev_btn_{std_id}"):
                    has_attachment = bool(uploaded_files) or bool(ext_link_input.strip())
                    if final_title.strip() and has_attachment and active_year.get('id'):
                        full_desc_parts = []
                        if st.session_state[desc_key].strip():
                            full_desc_parts.append(st.session_state[desc_key].strip())
                        extra_details = []
                        if st.session_state[goal_key].strip():
                            extra_details.append(f"• الهدف: {st.session_state[goal_key].strip()}")
                        if st.session_state[target_key].strip():
                            extra_details.append(f"• المستهدفون: {st.session_state[target_key].strip()}")
                        if st.session_state[impl_key].strip():
                            extra_details.append(f"• التنفيذ: {st.session_state[impl_key].strip()}")
                        if st.session_state[impact_key].strip():
                            extra_details.append(f"• الأثر: {st.session_state[impact_key].strip()}")
                        if extra_details:
                            full_desc_parts.append("\n".join(extra_details))
                        combined_description = "\n\n".join(full_desc_parts)

                        with st.spinner("جاري حفظ الشاهد والمرفقات..."):
                            insert_payload = {
                                "standard_id": std_id,
                                "year_id": active_year['id'],
                                "title": final_title.strip(),
                                "description": combined_description,
                                "execution_date": str(exec_date_input)
                            }
                            try:
                                ev_data = supabase.table("evidences").insert(insert_payload).execute()
                            except Exception:
                                insert_payload.pop("execution_date", None)
                                ev_data = supabase.table("evidences").insert(insert_payload).execute()
                                
                            new_id = ev_data.data[0]['id']
                            if uploaded_files:
                                for up_file in uploaded_files:
                                    ext = up_file.name.split('.')[-1]
                                    path = f"{new_id}/{uuid.uuid4()}.{ext}"
                                    supabase.storage.from_("private-achievements").upload(
                                        path=path, file=up_file.getvalue(), file_options={"content-type": up_file.type}
                                    )
                                    supabase.table("evidence_files").insert({
                                        "evidence_id": new_id, "file_url": path, "file_type": up_file.type
                                    }).execute()
                            if ext_link_input.strip():
                                supabase.table("evidence_files").insert({
                                    "evidence_id": new_id,
                                    "file_url": ext_link_input.strip(),
                                    "file_type": "external/link"
                                }).execute()
                                
                            st.session_state[clear_flag_key] = True
                            clear_app_cache()
                            st.success("تم حفظ الشاهد بنجاح!")
                            time.sleep(0.4)
                            st.rerun()
                    else:
                        st.warning("يرجى التأكد من كتابة عنوان الشاهد وإرفاق ملف واحد على الأقل أو وضع رابط خارجي.")

    # ----------------------------------------
    # 📄 3. صفحة التقارير والطباعة (شبكة 2×2 بحد أقصى 4 صور في الصفحة + صفحات إضافية تلقائية)
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.markdown("#### 📄 تصدير وطباعة ملف الإنجاز")
        
        report_style = st.selectbox(
            "🎨 اختر تصميم التقرير قبل التصدير:",
            [
                "1. التصميم الرسمي الوزاري (إطار كلاسيكي وجداول رسمية)",
                "2. التصميم العصري الحديث (بطاقات ناعمة وألوان المظهر الحالي)",
                "3. التصميم التنفيذي المختصر (تخطيط مكثف بحدود هندسية أنيقة)"
            ]
        )

        stds_map = {s['id']: s for s in stds}
        all_evidences = sorted(evidences, key=lambda x: x.get('standard_id', 0))
        total_evidences = len(all_evidences)
        active_stds = [s for s in stds if len([e for e in all_evidences if e['standard_id'] == s['id']]) > 0]
        covered_stds = len(active_stds)

        if report_style.startswith("1."):
            rep_color = "#146c59"
            rep_sub = "#0f5243"
            cover_border = "6px double #146c59"
            box_radius = "8px"
        elif report_style.startswith("2."):
            rep_color = th['primary']
            rep_sub = th['primary_dark']
            cover_border = f"3px solid {th['primary']}"
            box_radius = "12px"
        else:
            rep_color = "#1e293b"
            rep_sub = "#334155"
            cover_border = "2px solid #1e293b"
            box_radius = "4px"

        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>ملف الإنجاز المهني - {user_info['full_name']}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Readex+Pro:wght@400;500;600;700&display=swap');
                * {{ box-sizing: border-box; }}
                body {{ font-family: 'Readex Pro', sans-serif; background-color: #cbd5e1; margin: 0; padding: 20px; }}
                
                .page {{
                    background-color: white;
                    width: 210mm;
                    height: 296mm;
                    padding: 10mm 14mm;
                    margin: 0 auto 20mm auto;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
                    page-break-after: always;
                    page-break-inside: avoid;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }}
                
                .cover-page {{ border: {cover_border}; border-radius: {box_radius}; padding: 35px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; }}
                .cover-title {{ color: {rep_color}; font-size: 36px; font-weight: 700; margin-bottom: 10px; }}
                .cover-subtitle {{ font-size: 19px; margin-bottom: 35px; font-weight: 600; color: #475569; }}
                .info-table {{ width: 88%; border-collapse: collapse; margin: 0 auto; font-size: 16px; }}
                .info-table th, .info-table td {{ border: 1px solid #cbd5e1; padding: 12px; text-align: center; }}
                .info-table th {{ background-color: #f8fafc; width: 32%; font-weight: 700; color: {rep_color}; }}
                
                .header-container {{ display: flex; justify-content: space-between; border-bottom: 2px solid {rep_color}; padding-bottom: 6px; margin-bottom: 10px; font-size: 12px; font-weight: 700; flex-shrink: 0; }}
                .header-right {{ color: {rep_color}; }}
                .header-left {{ text-align: left; }}
                
                .index-title {{ color: {rep_color}; font-size: 22px; font-weight: 700; margin-bottom: 16px; }}
                .index-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
                .index-table th {{ background-color: #f1f5f9; color: {rep_color}; padding: 10px; text-align: center; border-bottom: 2px solid {rep_color}; }}
                .index-table td {{ padding: 10px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
                
                .content-wrapper {{ flex: 1 1 auto; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }}
                
                .top-ev-banner {{
                    background-color: {rep_color};
                    color: white;
                    padding: 10px 16px;
                    border-radius: {box_radius};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    flex-shrink: 0;
                }}
                .top-ev-title {{ font-size: 16px; font-weight: 700; }}
                .top-std-sub {{ font-size: 12.5px; opacity: 0.92; }}
                
                .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; flex-shrink: 0; }}
                .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 7px 12px; text-align: center; border-radius: {box_radius}; }}
                .meta-title {{ font-size: 11px; color: #64748b; font-weight: 600; }}
                .meta-value {{ font-size: 13px; font-weight: 700; color: #0f172a; }}
                
                .desc-header {{
                    border-right: 4px solid {rep_color};
                    padding-right: 8px;
                    font-size: 13.5px;
                    font-weight: 700;
                    color: {rep_color};
                    margin-bottom: 4px;
                    flex-shrink: 0;
                }}
                .desc-section {{
                    margin-bottom: 10px;
                    line-height: 1.55;
                    font-size: 12.5px;
                    color: #1e293b;
                    padding: 8px 10px;
                    background: #fafafa;
                    border: 1px solid #f1f5f9;
                    border-radius: {box_radius};
                    flex-shrink: 0;
                    white-space: pre-line;
                    max-height: 44mm;
                    overflow: hidden;
                }}
                
                .shawahed-bar {{
                    background-color: #e6f2ef;
                    color: {rep_color};
                    text-align: center;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 5px;
                    border-radius: 6px;
                    margin-bottom: 8px;
                    flex-shrink: 0;
                }}

                .images-grid {{
                    flex: 1 1 auto;
                    display: grid;
                    gap: 10px;
                    width: 100%;
                    min-height: 0;
                    overflow: hidden;
                    margin-bottom: 6px;
                }}
                .images-grid.count-1 {{
                    grid-template-columns: 1fr;
                    grid-template-rows: minmax(0, 1fr);
                }}
                .images-grid.count-2 {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    grid-template-rows: minmax(0, 1fr);
                }}
                .images-grid.count-3, .images-grid.count-4 {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    grid-template-rows: repeat(2, minmax(0, 1fr));
                }}
                .img-frame {{
                    background-color: #f8f9fa;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 100%;
                    min-width: 0;
                    min-height: 0;
                    overflow: hidden;
                }}
                .img-frame img {{
                    width: 100%;
                    height: 100%;
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain !important;
                    display: block;
                    border-radius: 6px;
                }}

                .pdf-notice {{ background: #f1f5f9; padding: 6px; text-align: center; border-radius: 6px; font-size: 11.5px; color: #334155; margin-bottom: 6px; border: 1px dashed #94a3b8; flex-shrink: 0; }}
                .signatures {{ display: flex; justify-content: space-between; margin-top: auto; border-top: 1.5px solid #e2e8f0; padding-top: 8px; text-align: center; flex-shrink: 0; }}
                .sig-box {{ width: 42%; font-size: 12.5px; }}
                .print-footer {{ text-align: center; font-size: 9.5px; color: #64748b; margin-top: 6px; padding-top: 4px; border-top: 1px dashed #e2e8f0; flex-shrink: 0; }}
                
                @media print {{
                    body {{ background-color: white; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                    .page {{ width: 210mm; height: 296mm; margin: 0; padding: 10mm 14mm; box-shadow: none; border: none; }}
                    @page {{ size: A4 portrait; margin: 0; }}
                }}
            </style>
        </head>
        <body>
        """
        
        html_content += f"""
        <div class="page">
            <div class="cover-page">
                <div style="font-size:15px; font-weight:700; color:{rep_color}; margin-bottom:8px;">المملكة العربية السعودية • وزارة التعليم</div>
                <div style="font-size:13px; color:#b45309; font-weight:700; margin-bottom:12px;">🎓 منصة زياد الذكية لتوثيق الأداء المهني</div>
                <div class="cover-title">ملف الإنجاز المهني</div>
                <div class="cover-subtitle">توثيق شواهد الأداء الوظيفي</div>
                <table class="info-table">
                    <tr><th>اسم المعلم</th><td>{user_info['full_name']}</td></tr>
                    <tr><th>التخصص</th><td>{user_info['specialization']}</td></tr>
                    <tr><th>المدرسة</th><td>{user_info['school_name']}</td></tr>
                    <tr><th>المرحلة الدراسية</th><td>{user_info['education_stage']}</td></tr>
                    <tr><th>المدينة</th><td>{user_info['city']}</td></tr>
                    <tr><th>مدير المدرسة</th><td>{user_info['principal_name']}</td></tr>
                    <tr><th>العام الدراسي</th><td>{active_year['year_name']}هـ</td></tr>
                    <tr><th>إجمالي الشواهد الموثقة</th><td>{total_evidences} شاهد ({covered_stds} من {len(stds)} معايير)</td></tr>
                </table>
                <div style="margin-top:35px; font-size:11px; color:#64748b;">صدر إلكترونياً عبر منصة زياد الذكية — جميع الحقوق محفوظة © أ. {user_info['full_name']}</div>
            </div>
        </div>
        """
        
        shared_header = f"""
        <div class="header-container">
            <div class="header-right">
                منصة زياد الذكية | أ. {user_info['full_name']}<br>
                <span style="font-size:10.5px; font-weight:normal; color:#666;">شواهد الأداء الوظيفي - العام الدراسي {active_year['year_name']}هـ</span>
            </div>
            <div class="header-left">
                المملكة العربية السعودية<br>
                <span style="font-size:10.5px; font-weight:normal; color:#666;">وزارة التعليم - {user_info['school_name']}</span>
            </div>
        </div>
        """
        
        html_content += f"""
        <div class="page">
            {shared_header}
            <div class="index-title">فهرس معايير الأداء المنجزة</div>
            <table class="index-table">
                <tr><th>م</th><th>المعيار</th><th>الوزن النسبي</th><th>الشواهد الموثقة</th><th>المستهدف</th></tr>
        """
        for std in stds:
            count = ev_by_std[std['id']]
            if count == 0:
                continue
            target = std.get('target_evidences', 3)
            html_content += f"<tr><td>{std['id']}</td><td style='text-align:right; font-weight:bold;'>{std['title']}</td><td>{std['weight']}%</td><td style='color:{rep_color}; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
        html_content += f"""
            </table>
            <div class="print-footer" style="margin-top:auto;">منصة زياد الذكية | جميع الحقوق محفوظة © أ. {user_info['full_name']}</div>
        </div>
        """
        
        for ev in all_evidences:
            std = stds_map.get(ev['standard_id'], {"title": "", "weight": 10})
            exec_date = ev.get('execution_date') or ev['created_at'][:10]
            files = ev.get('evidence_files', [])
            
            img_urls = []
            pdf_count = 0
            ext_links = []
            for f in files:
                f_url = f.get('file_url', '')
                f_type = f.get('file_type', '')
                if f_type == 'external/link' or f_url.startswith('http'):
                    ext_links.append(f_url)
                elif f_type.startswith('image/'):
                    sec_u = signed_urls_map.get(f_url, '')
                    if sec_u:
                        img_urls.append(sec_u)
                elif f_type == 'application/pdf':
                    pdf_count += 1

            img_chunks = [img_urls[i:i + 4] for i in range(0, len(img_urls), 4)]
            if not img_chunks:
                img_chunks = [[]]

            total_chunks = len(img_chunks)
            pdf_notice = f"<div class='pdf-notice'>📌 مرفق مستند PDF رسمي عدد ({pdf_count}) محفوظ في النظام الإلكتروني.</div>" if pdf_count > 0 else ""
            link_notice = f"<div class='pdf-notice'>🔗 رابط إلكتروني مرفق: {ext_links[0]}</div>" if ext_links else ""

            for chunk_idx, chunk in enumerate(img_chunks):
                c_len = len(chunk)
                grid_cls = f"count-{c_len}" if c_len in [1, 2, 3, 4] else "count-4"
                frames_html = "".join([f"<div class='img-frame'><img src='{u}'></div>" for u in chunk])
                images_section = f"<div class='shawahed-bar'>الشواهد{f' (صفحة {chunk_idx+1} من {total_chunks})' if total_chunks > 1 else ''}</div><div class='images-grid {grid_cls}'>{frames_html}</div>" if c_len > 0 else ""

                if chunk_idx == 0:
                    html_content += f"""
                    <div class="page">
                        {shared_header}
                        <div class="content-wrapper">
                            <div class="top-ev-banner">
                                <span class="top-ev-title">{ev['title']}</span>
                                <span class="top-std-sub">البند {ev['standard_id']}: {std['title']} ({std['weight']}%)</span>
                            </div>
                            <div class="meta-grid">
                                <div class="meta-box"><div class="meta-title">تاريخ التنفيذ</div><div class="meta-value">{exec_date}</div></div>
                                <div class="meta-box"><div class="meta-title">نوع الشاهد</div><div class="meta-value">شاهد ميداني موثق</div></div>
                            </div>
                            <div class="desc-header">الوصف</div>
                            <div class="desc-section">{ev.get('description') or 'تم تنفيذ الشاهد وتوثيقه وفق خطة توزيع المنهج.'}</div>
                            {pdf_notice}
                            {link_notice}
                            {images_section}
                        </div>
                        <div class="signatures">
                            <div class="sig-box">
                                <div style="color:#666; font-size:11.5px; margin-bottom:10px;">المعلم:</div>
                                <div style="font-weight:bold;">{user_info['full_name']}</div>
                            </div>
                            <div class="sig-box">
                                <div style="color:#666; font-size:11.5px; margin-bottom:10px;">مدير المدرسة:</div>
                                <div style="font-weight:bold;">{user_info['principal_name']}</div>
                            </div>
                        </div>
                        <div class="print-footer">منصة زياد الذكية | ملف الإنجاز المهني — أ. {user_info['full_name']}</div>
                    </div>
                    """
                else:
                    html_content += f"""
                    <div class="page">
                        {shared_header}
                        <div class="content-wrapper">
                            <div class="top-ev-banner">
                                <span class="top-ev-title">تابع: {ev['title']}</span>
                                <span class="top-std-sub">البند {ev['standard_id']}: {std['title']} (صفحة {chunk_idx+1} من {total_chunks})</span>
                            </div>
                            {images_section}
                        </div>
                        <div class="signatures">
                            <div class="sig-box">
                                <div style="color:#666; font-size:11.5px; margin-bottom:10px;">المعلم:</div>
                                <div style="font-weight:bold;">{user_info['full_name']}</div>
                            </div>
                            <div class="sig-box">
                                <div style="color:#666; font-size:11.5px; margin-bottom:10px;">مدير المدرسة:</div>
                                <div style="font-weight:bold;">{user_info['principal_name']}</div>
                            </div>
                        </div>
                        <div class="print-footer">منصة زياد الذكية | ملف الإنجاز المهني — أ. {user_info['full_name']}</div>
                    </div>
                    """
        
        html_content += "</body></html>"
        safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        
        components.html(f"""
            <div style="text-align: center; margin: 4px 0;">
                <button onclick="openPrintWindow()" style="width: 100%; height: 52px; background-color: #146c59; color: white; border: none; border-radius: 14px; font-size: 16px; font-weight: bold; cursor: pointer; font-family: 'Readex Pro', 'Cairo', sans-serif; box-shadow: 0 4px 10px rgba(20,108,89,0.2);">
                    تصدير ملف الإنجاز PDF
                </button>
            </div>
            <script>
                function openPrintWindow() {{
                    var win = window.open('', '_blank');
                    win.document.write(`{safe_html}`);
                    win.document.close();
                    var imgs = Array.from(win.document.images);
                    if (imgs.length === 0) {{
                        setTimeout(function() {{ win.print(); }}, 600);
                    }} else {{
                        var loaded = 0;
                        var printed = false;
                        function checkDone() {{
                            if (!printed && loaded >= imgs.length) {{
                                printed = true;
                                setTimeout(function() {{ win.print(); }}, 400);
                            }}
                        }}
                        imgs.forEach(function(img) {{
                            if (img.complete) {{
                                loaded++;
                                checkDone();
                            }} else {{
                                img.onload = function() {{ loaded++; checkDone(); }};
                                img.onerror = function() {{ loaded++; checkDone(); }};
                            }}
                        }});
                        setTimeout(function() {{
                            if (!printed) {{
                                printed = true;
                                win.print();
                            }}
                        }}, 3500);
                    }}
                }}
            </script>
        """, height=62)

        docx_bytes = generate_editable_docx(user_info, active_year, stds, evidences)
        st.download_button(
            label="📄 تصدير Word قابل للتعديل",
            data=docx_bytes,
            file_name=f"ملف_إنجاز_{user_info['full_name'].replace(' ', '_')}_{active_year['year_name']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    # ----------------------------------------
    # ⚙️ 4. صفحة حسابي
    # ----------------------------------------
    elif st.session_state.current_page == 'settings' and not is_visitor:
        st.markdown("#### ⚙️ إعدادات الحساب والمظهر والأرشيف والنسخ الاحتياطي")
        t1, t2, t3, t4 = st.tabs(["👤 البيانات والمظهر", "📅 الأرشيف والنسخ", "🔗 مشاركة للزوار", "🚪 الخروج"])
        
        with t1:
            with st.form("profile_form"):
                st.markdown("##### 🎨 مظهر التطبيق")
                theme_keys = list(THEMES.keys())
                theme_labels = [THEMES[k]["name"] for k in theme_keys]
                current_idx = theme_keys.index(active_theme_key) if active_theme_key in theme_keys else 0
                selected_theme_label = st.selectbox("اختر المظهر اللوني للتطبيق:", theme_labels, index=current_idx)
                chosen_theme_key = theme_keys[theme_labels.index(selected_theme_label)]

                st.markdown("##### 📝 البيانات الأساسية")
                c1, c2 = st.columns(2)
                with c1:
                    n_name = st.text_input("اسم المعلم:", value=user_info['full_name'])
                    n_spec = st.text_input("التخصص:", value=user_info['specialization'])
                    n_city = st.text_input("المدينة:", value=user_info['city'])
                with c2:
                    n_school = st.text_input("اسم المدرسة:", value=user_info['school_name'])
                    n_stage = st.text_input("المرحلة الدراسية:", value=user_info['education_stage'])
                    n_prin = st.text_input("اسم مدير المدرسة:", value=user_info['principal_name'])

                st.markdown("##### ✨ إعداد الذكاء الاصطناعي (اختياري)")
                g_key_in = st.text_input(
                    "مفتاح Gemini API (اختياري - في حال تركه فارغاً يعمل محرك القوالب التربوية الذكي المدمج مجاناً):",
                    value=st.session_state.custom_gemini_key,
                    type="password"
                )
                
                if st.form_submit_button("حفظ البيانات والمظهر 💾", type="primary", use_container_width=True):
                    st.session_state.custom_gemini_key = g_key_in.strip()
                    payload = {
                        "id": 1,
                        "full_name": n_name,
                        "specialization": n_spec,
                        "school_name": n_school,
                        "education_stage": n_stage,
                        "city": n_city,
                        "principal_name": n_prin,
                        "theme": chosen_theme_key
                    }
                    try:
                        supabase.table("user_profile").upsert(payload).execute()
                    except Exception:
                        payload.pop("theme", None)
                        supabase.table("user_profile").upsert(payload).execute()
                    clear_app_cache()
                    st.success("تم تحديث البيانات والمظهر بنجاح!")
                    time.sleep(0.3)
                    st.rerun()

        with t2:
            sub_section = st.radio(
                "archive_backup_split",
                options=["archive_sec", "backup_sec"],
                format_func=lambda k: "📅 أرشفة الأعوام الدراسية" if k == "archive_sec" else "💾 التصدير والنسخ الاحتياطي",
                horizontal=True,
                label_visibility="collapsed"
            )

            if sub_section == "archive_sec":
                st.markdown("##### 📅 أرشفة ملفات الإنجاز وإدارة الأعوام الدراسية")
                st.caption("في نهاية العام الدراسي، يمكنك أرشفة الملف الحالي وفتح ملف إنجاز جديد للعام القادم مع بقاء جميع شواهدك السابقة محفوظة.")
                
                with st.form("archive_and_new_year_form", clear_on_submit=True):
                    new_year_name = st.text_input("🆕 اسم العام الدراسي الجديد (مثال: 1449 أو 1449-1450):")
                    submit_new_year = st.form_submit_button("📦 أرشفة العام الحالي وبدء ملف الإنجاز الجديد", type="primary", use_container_width=True)
                    if submit_new_year:
                        if new_year_name.strip():
                            for y in all_years:
                                supabase.table("academic_years").update({"is_active": False}).eq("id", y['id']).execute()
                            supabase.table("academic_years").insert({
                                "year_name": new_year_name.strip(),
                                "is_active": True
                            }).execute()
                            clear_app_cache()
                            st.success(f"تمت أرشفة العام السابق، وفتح ملف إنجاز جديد لعام ({new_year_name.strip()})!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.warning("يرجى كتابة اسم العام الدراسي الجديد.")

                st.markdown("##### 🗂️ سجل ملفات الإنجاز المحفوظة")
                for y in all_years:
                    y_ev_res = supabase.table("evidences").select("id", count="exact").eq("year_id", y['id']).execute()
                    y_count = y_ev_res.count if y_ev_res.count is not None else len(y_ev_res.data)
                    is_act = y.get("is_active", False)
                    
                    badge_html = '<span style="background:#10b981; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">🟢 الملف النشط</span>' if is_act else '<span style="background:#64748b; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">📦 مؤرشف</span>'
                    
                    arch_card = (
                        f'<div class="std-card">'
                        f'<div><div class="std-title">📁 ملف إنجاز العام الدراسي: {y["year_name"]}هـ</div>'
                        f'<div style="font-size:12.5px; color:#64748b !important;">عدد الشواهد الموثقة: <strong>{y_count} شاهد</strong></div></div>'
                        f'<div>{badge_html}</div>'
                        f'</div>'
                    )
                    st.markdown(arch_card, unsafe_allow_html=True)
                    
                    if not is_act:
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            if st.button(f"🔄 تفعيل واستعراض ملف عام {y['year_name']}هـ", key=f"act_{y['id']}", type="primary", use_container_width=True):
                                for item_y in all_years:
                                    supabase.table("academic_years").update({"is_active": False}).eq("id", item_y['id']).execute()
                                supabase.table("academic_years").update({"is_active": True}).eq("id", y['id']).execute()
                                clear_app_cache()
                                st.rerun()
                        with col_b:
                            if y_count == 0:
                                if st.button("🗑️ حذف", key=f"del_y_{y['id']}", use_container_width=True):
                                    supabase.table("academic_years").delete().eq("id", y['id']).execute()
                                    clear_app_cache()
                                    st.rerun()

            else:
                st.markdown("##### 📤 تصدير ملف الإنجاز والنسخ الاحتياطي (متعدد الصيغ)")
                st.caption("اختر الصيغة المناسبة لتحميل نسخة كاملة من ملف إنجازك أو قاعدة بياناتك:")

                docx_backup_bytes = generate_editable_docx(user_info, active_year, stds, evidences)
                st.download_button(
                    label="📄 تصدير ملف الإنجاز Word قابل للتعديل (.docx)",
                    data=docx_backup_bytes,
                    file_name=f"ملف_إنجاز_{user_info['full_name'].replace(' ', '_')}_{active_year['year_name']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

                csv_data = generate_excel_csv(stds, evidences)
                st.download_button(
                    label="📊 تصدير سجل الشواهد لبرنامج Excel (.csv)",
                    data=csv_data.encode("utf-8"),
                    file_name=f"سجل_الشواهد_{active_year['year_name']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                full_backup = {
                    "user_profile": user_info,
                    "academic_years": all_years,
                    "standards": stds,
                    "sub_items": all_subs,
                    "evidences": evidences
                }
                st.download_button(
                    label="📦 تحميل النسخة الاحتياطية الشاملة للنظام (.json)",
                    data=json.dumps(full_backup, ensure_ascii=False, indent=4),
                    file_name=f"ziyad_full_backup_{datetime.date.today()}.json",
                    mime="application/json",
                    type="primary",
                    use_container_width=True
                )

                st.write("---")
                st.markdown("##### 📥 استعادة نسخة احتياطية سابقة (Restore)")
                uploaded_backup = st.file_uploader("ارفع ملف النسخة الاحتياطية (.json) لاستعادة الشواهد والبيانات:", type=["json"])
                if uploaded_backup is not None:
                    if st.button("🔄 بدء استعادة البيانات الآن", type="primary", use_container_width=True):
                        try:
                            b_data = json.loads(uploaded_backup.getvalue().decode("utf-8"))
                            restored_count = 0
                            existing_ids = {e['id'] for e in evidences}
                            for ev_item in b_data.get("evidences", []):
                                if ev_item.get("id") not in existing_ids and active_year.get("id"):
                                    ins_ev = {
                                        "standard_id": ev_item.get("standard_id", 1),
                                        "year_id": active_year["id"],
                                        "title": ev_item.get("title", "شاهد مستعاد"),
                                        "description": ev_item.get("description", ""),
                                        "execution_date": ev_item.get("execution_date") or ev_item.get("created_at", "")[:10]
                                    }
                                    try:
                                        supabase.table("evidences").insert(ins_ev).execute()
                                    except Exception:
                                        ins_ev.pop("execution_date", None)
                                        supabase.table("evidences").insert(ins_ev).execute()
                                    restored_count += 1
                            clear_app_cache()
                            st.success(f"تمت استعادة ({restored_count}) شاهد جديد بنجاح إلى العام الحالي!")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"تعذر قراءة ملف النسخة الاحتياطية: {e}")

        with t3:
            st.markdown("##### 🔗 التحكم في وصول الزوار (قراءة ومشاهدة فقط)")
            with st.form("visitor_settings_form"):
                allow_v = st.checkbox("تفعيل السماح بدخول الزوار عبر الرمز السري", value=user_info.get("allow_visitor", True))
                v_code_input = st.text_input("الرمز السري للزائر:", value=str(user_info.get("visitor_code", "1448")))
                if st.form_submit_button("حفظ إعدادات الزائر 🔒", type="primary", use_container_width=True):
                    try:
                        supabase.table("user_profile").update({
                            "allow_visitor": allow_v,
                            "visitor_code": v_code_input.strip()
                        }).eq("id", 1).execute()
                        clear_app_cache()
                        st.success("تم تحديث إعدادات الزائر بنجاح!")
                        time.sleep(0.3)
                        st.rerun()
                    except Exception as e:
                        st.error(f"يرجى التأكد من تحديث جدول user_profile: {e}")

            curr_code = user_info.get("visitor_code", "1448")
            st.info(f"💡 **رابط المشاركة السريعة للزائر:** أضف `?visitor={curr_code}` لنهاية رابط موقعك، أو أعطِ الرمز `{curr_code}` للزائر ليدخله في تبويب (دخول زائر).")

        with t4:
            if st.button("🚪 تسجيل الخروج من الحساب", type="primary", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.is_visitor = False
                st.rerun()

    render_footer()

# ==========================================
# 11. نقطة تشغيل التطبيق
# ==========================================
if st.session_state.user is None and not st.session_state.is_visitor:
    login_page()
else:
    main_app()
