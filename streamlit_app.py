import streamlit as st
from supabase import create_client
import time
import uuid
import json
import re
import html
import base64
import datetime
import zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image
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
        "name": "🔵 أزرق منصة زياد الذكية",
        "primary": "#1e3a8a",
        "primary_light": "#2563eb",
        "primary_dark": "#0f172a",
        "bg": "#f4f7fb",
        "accent": "#f59e0b",
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
        "accent": "#f59e0b",
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
# 5. الاتصال الآمن بقاعدة البيانات، ضغط الصور، وحساب المساحة السحابية السريع
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_tokens' not in st.session_state:
    st.session_state.auth_tokens = None
if 'is_visitor' not in st.session_state:
    st.session_state.is_visitor = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'view_standard_id' not in st.session_state:
    st.session_state.view_standard_id = 0
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'
if 'login_mode' not in st.session_state:
    st.session_state.login_mode = 'teacher'
if 'ai_variant' not in st.session_state:
    st.session_state.ai_variant = 0
if 'custom_gemini_key' not in st.session_state:
    st.session_state.custom_gemini_key = ""
if 'ready_docx_bytes' not in st.session_state:
    st.session_state.ready_docx_bytes = None
if 'ready_zip_bytes' not in st.session_state:
    st.session_state.ready_zip_bytes = None
if 'ready_pdf_b64' not in st.session_state:
    st.session_state.ready_pdf_b64 = None
if 'auto_open_pdf' not in st.session_state:
    st.session_state.auto_open_pdf = False

if st.session_state.user is not None and st.session_state.auth_tokens:
    try:
        curr_sess = supabase.auth.get_session()
        if curr_sess is None:
            supabase.auth.set_session(
                st.session_state.auth_tokens["access_token"],
                st.session_state.auth_tokens["refresh_token"]
            )
    except Exception:
        pass

def clear_app_cache():
    st.cache_data.clear()
    st.session_state.ready_docx_bytes = None
    st.session_state.ready_zip_bytes = None
    st.session_state.ready_pdf_b64 = None
    st.session_state.auto_open_pdf = False

def navigate_to(page_name, std_id=None):
    st.session_state.current_page = page_name
    if std_id is not None:
        st.session_state.view_standard_id = std_id
    st.rerun()

def optimize_uploaded_image(up_file):
    raw_bytes = up_file.getvalue()
    mime_type = up_file.type or ""
    ext = up_file.name.split('.')[-1].lower() if '.' in up_file.name else "bin"

    if not mime_type.startswith("image/"):
        return raw_bytes, mime_type, ext

    if len(raw_bytes) < 350 * 1024 and ext in ("jpg", "jpeg", "png"):
        return raw_bytes, mime_type, ext

    try:
        img = Image.open(BytesIO(raw_bytes))
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        out_buf = BytesIO()
        img.save(out_buf, format="JPEG", quality=85, optimize=True)
        return out_buf.getvalue(), "image/jpeg", "jpg"
    except Exception:
        return raw_bytes, mime_type, ext

@st.cache_data(ttl=600, show_spinner=False)
def fetch_storage_usage_stats():
    total_bytes = 0
    img_count = 0
    pdf_count = 0
    link_count = 0

    try:
        all_files_res = supabase.table("evidence_files").select("file_url, file_type").execute()
        all_files = all_files_res.data if all_files_res.data else []
    except Exception:
        all_files = []

    folders = set()
    for f in all_files:
        f_url = f.get("file_url", "")
        f_type = f.get("file_type", "")
        if f_type == "external/link" or f_url.startswith("http"):
            link_count += 1
        elif f_type.startswith("image/"):
            img_count += 1
            if "/" in f_url:
                folders.add(f_url.split("/")[0])
        elif f_type == "application/pdf":
            pdf_count += 1
            if "/" in f_url:
                folders.add(f_url.split("/")[0])

    rpc_succeeded = False
    try:
        rpc_res = supabase.rpc("get_storage_usage").execute()
        if isinstance(rpc_res.data, (int, float)) and rpc_res.data >= 0:
            total_bytes = int(rpc_res.data)
            rpc_succeeded = True
    except Exception:
        pass

    if not rpc_succeeded and (img_count + pdf_count) > 0:
        def _get_folder_size(folder_name):
            f_bytes = 0
            try:
                items = supabase.storage.from_("private-achievements").list(folder_name)
                if items:
                    for item in items:
                        meta = item.get("metadata") or {}
                        sz = meta.get("size", 0)
                        if isinstance(sz, (int, float)):
                            f_bytes += int(sz)
            except Exception:
                pass
            return f_bytes

        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                sizes = list(executor.map(_get_folder_size, folders))
                total_bytes = sum(sizes)
        except Exception:
            pass

        if total_bytes == 0:
            total_bytes = (img_count * 240 * 1024) + (pdf_count * 550 * 1024)

    used_mb = total_bytes / (1024 * 1024)
    limit_mb = 1024.0
    remaining_mb = max(0.0, limit_mb - used_mb)
    usage_pct = min(100.0, (used_mb / limit_mb) * 100.0)
    est_more_images = int((remaining_mb * 1024) / 240)

    return {
        "total_bytes": total_bytes,
        "used_mb": used_mb,
        "limit_mb": limit_mb,
        "remaining_mb": remaining_mb,
        "usage_pct": usage_pct,
        "img_count": img_count,
        "pdf_count": pdf_count,
        "link_count": link_count,
        "est_more_images": est_more_images
    }

def render_storage_meter_card(storage_stats):
    pct = storage_stats["usage_pct"]
    used_mb = storage_stats["used_mb"]
    rem_mb = storage_stats["remaining_mb"]
    imgs = storage_stats["img_count"]
    pdfs = storage_stats["pdf_count"]
    more_imgs = storage_stats["est_more_images"]

    if used_mb < 1.0 and storage_stats["total_bytes"] > 0:
        used_str = f"{storage_stats['total_bytes'] / 1024:.1f} KB"
    else:
        used_str = f"{used_mb:.2f} MB"

    if pct < 70:
        bar_color = "#10b981"
        badge_bg = "#dcfce7"
        badge_txt = "#166534"
        status_label = "🟢 المساحة آمنة ووفيرة"
        alert_msg = f"💡 المساحة المتبقية ({rem_mb:.1f} MB) تكفي لرفع قرابة ({more_imgs:,}) صورة إضافية بفضل نظام الضغط الذكي."
    elif pct < 85:
        bar_color = "#f59e0b"
        badge_bg = "#fef3c7"
        badge_txt = "#92400e"
        status_label = "🟠 تنبيه: تجاوزت 70% من المساحة"
        alert_msg = f"⚠️ تبقى لديك ({rem_mb:.1f} MB). يُنصح بمراجعة المرفقات وحذف الصور المكررة أو غير الضرورية."
    else:
        bar_color = "#ef4444"
        badge_bg = "#fee2e2"
        badge_txt = "#991b1b"
        status_label = "🔴 تحذير حرج: المساحة قاربت على الامتلاء!"
        alert_msg = f"🚨 تبقى ({rem_mb:.1f} MB) فقط من أصل 1024 MB! يرجى تصدير ملفاتك وحذف المرفقات القديمة لتفادي توقف الرفع."

    vis_pct = max(pct, 1.5) if storage_stats["total_bytes"] > 0 else 0.0

    meter_html = (
        f'<div class="progress-card" dir="rtl" style="border:1.5px solid {bar_color}; margin-bottom:14px;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">'
        f'<span style="font-weight:800; font-size:14.5px; color:#0f172a !important;">☁️ عداد مساحة التخزين السحابية (Supabase 1GB)</span>'
        f'<span style="background:{badge_bg}; color:{badge_txt} !important; padding:4px 10px; border-radius:99px; font-size:11.5px; font-weight:700;">{status_label}</span>'
        f'</div>'
        f'<div style="display:flex; justify-content:space-between; font-size:12.5px; font-weight:700; color:#334155; margin-bottom:4px;">'
        f'<span>المستهلك: {used_str} من 1024 MB</span>'
        f'<span style="color:{bar_color} !important;">{pct:.1f}%</span>'
        f'</div>'
        f'<div class="progress-bar-bg" style="height:11px; background:#e2e8f0;">'
        f'<div style="width:{vis_pct}%; height:100%; background:{bar_color}; border-radius:6px; transition:width 0.3s ease;"></div>'
        f'</div>'
        f'<div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-top:10px; font-size:12px; color:#475569;">'
        f'<span>🖼️ الصور المحفوظة: <strong>{imgs}</strong></span>'
        f'<span>📄 ملفات PDF: <strong>{pdfs}</strong></span>'
        f'<span>📦 المتبقي: <strong>{rem_mb:.1f} MB</strong></span>'
        f'</div>'
        f'<div style="margin-top:8px; padding:7px 10px; background:#f8fafc; border-radius:9px; font-size:11.5px; color:#334155;">{alert_msg}</div>'
        f'</div>'
    )
    st.markdown(meter_html, unsafe_allow_html=True)

def sort_evidences_chronologically(ev_list):
    def _sort_key(ev):
        std_id = ev.get('standard_id', 0)
        exec_d = str(ev.get('execution_date') or ev.get('created_at', '')[:10] or '9999-12-31')
        created_at = str(ev.get('created_at', '') or '')
        ev_id = ev.get('id', 0)
        return (std_id, exec_d, created_at, ev_id)
    return sorted(ev_list, key=_sort_key)

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

@st.cache_data(ttl=300, show_spinner=False)
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

@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_years():
    try:
        res = supabase.table("academic_years").select("*").order("created_at", desc=True).execute()
        if res.data:
            return res.data
        ins = supabase.table("academic_years").insert({"year_name": "1448", "is_active": True}).execute()
        return ins.data if ins.data else []
    except Exception:
        return []

@st.cache_data(ttl=600, show_spinner=False)
def fetch_standards_and_subs():
    try:
        stds = supabase.table("standards").select("*").order("id").execute().data
    except Exception:
        stds = []
    try:
        subs = supabase.table("sub_items").select("*").execute().data
    except Exception:
        subs = []
    return stds, subs

@st.cache_data(ttl=180, show_spinner=False)
def fetch_year_evidences(year_id):
    if not year_id:
        return []
    try:
        res = supabase.table("evidences").select("*, evidence_files(*)").eq("year_id", year_id).execute()
        raw_data = res.data if res.data else []
        return sort_evidences_chronologically(raw_data)
    except Exception:
        return []

@st.cache_data(ttl=1800, show_spinner=False)
def get_signed_urls_batch(paths_tuple):
    if not paths_tuple:
        return {}
    url_map = {}
    unique_paths = list(dict.fromkeys(paths_tuple))
    storage_paths = [p for p in unique_paths if not p.startswith("http")]
    for p in unique_paths:
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

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_and_prepare_word_image(file_path, signed_url=""):
    raw_bytes = None
    try:
        raw_bytes = supabase.storage.from_("private-achievements").download(file_path)
    except Exception:
        if signed_url:
            try:
                req = urllib.request.Request(signed_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw_bytes = resp.read()
            except Exception:
                pass
    if not raw_bytes:
        return None

    try:
        img = Image.open(BytesIO(raw_bytes))
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        w_px, h_px = img.size
        out_buf = BytesIO()
        img.save(out_buf, format="JPEG", quality=85)
        jpeg_bytes = out_buf.getvalue()

        max_w_emu = 2650000
        max_h_emu = 2250000
        ratio = min(max_w_emu / max(w_px, 1), max_h_emu / max(h_px, 1))
        cx = int(w_px * ratio)
        cy = int(h_px * ratio)
        return {"bytes": jpeg_bytes, "cx": cx, "cy": cy}
    except Exception:
        return None

# ==========================================
# 6. محركات التصدير (Word للتقرير + حقيبة مرفقات ZIP وCSV وJSON للنسخ الاحتياطي)
# ==========================================
def clean_xml_text(val):
    if val is None:
        return ""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(val))
    return cleaned

def sanitize_filename_part(name_str):
    cleaned = re.sub(r'[\\/*?:"<>|\r\n\t]+', '_', str(name_str or '').strip())
    return cleaned[:55].strip('_') or "ملف"

def generate_editable_docx(user_info, active_year, stds, evidences, signed_urls_map):
    stds_map = {s['id']: s for s in stds}
    sorted_evs = sort_evidences_chronologically(evidences)
    total_ev = len(sorted_evs)
    covered_stds = len(set(e['standard_id'] for e in sorted_evs))

    image_tasks = []
    for ev in sorted_evs:
        for f in ev.get('evidence_files', []):
            f_url = f.get('file_url', '')
            f_type = f.get('file_type', '')
            if f_type.startswith('image/') and not f_url.startswith('http'):
                image_tasks.append((f_url, signed_urls_map.get(f_url, '')))

    prepared_images_map = {}
    if image_tasks:
        def _prep_task(task_pair):
            return task_pair[0], fetch_and_prepare_word_image(task_pair[0], task_pair[1])
        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                for p_path, p_info in executor.map(_prep_task, image_tasks):
                    if p_info:
                        prepared_images_map[p_path] = p_info
        except Exception:
            for t_path, t_su in image_tasks:
                p_info = fetch_and_prepare_word_image(t_path, t_su)
                if p_info:
                    prepared_images_map[t_path] = p_info

    media_files = {}
    rels_entries = []
    img_counter = 1

    def w_para(text, bold=False, size_pt=12, color="1E293B", align="right", space_after=120):
        sz = int(size_pt * 2)
        b_tag = "<w:b/><w:bCs/>" if bold else ""
        safe_txt = clean_xml_text(text)
        lines = safe_txt.split('\n')
        runs_xml = ""
        for l_idx, line_str in enumerate(lines):
            br_tag = "<w:br/>" if l_idx > 0 else ""
            runs_xml += f"""
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Cairo" w:hAnsi="Cairo" w:cs="Cairo"/>
                    {b_tag}
                    <w:color w:val="{color}"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:rtl/>
                </w:rPr>
                {br_tag}
                <w:t xml:space="preserve">{xml_escape(line_str)}</w:t>
            </w:r>
            """
        return f"""
        <w:p>
            <w:pPr>
                <w:bidi/>
                <w:jc w:val="{align}"/>
                <w:spacing w:after="{space_after}"/>
            </w:pPr>
            {runs_xml}
        </w:p>
        """

    def w_image_para(rel_id, img_id, cx, cy):
        return f"""
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
                <w:spacing w:before="60" w:after="60"/>
            </w:pPr>
            <w:r>
                <w:drawing>
                    <wp:inline distT="0" distB="0" distL="0" distR="0">
                        <wp:extent cx="{cx}" cy="{cy}"/>
                        <wp:docPr id="{img_id}" name="Picture {img_id}"/>
                        <wp:cNvGraphicFramePr>
                            <a:graphicFrameLocks noChangeAspect="1"/>
                        </wp:cNvGraphicFramePr>
                        <a:graphic>
                            <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                                <pic:pic>
                                    <pic:nvPicPr>
                                        <pic:cNvPr id="{img_id}" name="image_{img_id}.jpg"/>
                                        <pic:cNvPicPr/>
                                    </pic:nvPicPr>
                                    <pic:blipFill>
                                        <a:blip r:embed="{rel_id}"/>
                                        <a:stretch>
                                            <a:fillRect/>
                                        </a:stretch>
                                    </pic:blipFill>
                                    <pic:spPr>
                                        <a:xfrm>
                                            <a:off x="0" y="0"/>
                                            <a:ext cx="{cx}" cy="{cy}"/>
                                        </a:xfrm>
                                        <a:prstGeom prst="rect">
                                            <a:avLst/>
                                        </a:prstGeom>
                                    </pic:spPr>
                                </pic:pic>
                            </a:graphicData>
                        </a:graphic>
                    </wp:inline>
                </w:drawing>
            </w:r>
        </w:p>
        """

    def w_images_grid_table(img_drawings_list):
        tbl_xml = """
        <w:tbl>
            <w:tblPr>
                <w:bidiVisual/>
                <w:tblW w:w="5000" w:type="pct"/>
                <w:tblBorders>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                </w:tblBorders>
            </w:tblPr>
        """
        for i in range(0, len(img_drawings_list), 2):
            pair = img_drawings_list[i:i + 2]
            tbl_xml += "<w:tr>"
            for cell_xml in pair:
                tbl_xml += f"""
                <w:tc>
                    <w:tcPr>
                        <w:tcW w:w="2500" w:type="pct"/>
                        <w:shd w:val="clear" w:color="auto" w:fill="F8FAFC"/>
                        <w:tcMar>
                            <w:top w:w="100" w:type="dxa"/>
                            <w:bottom w:w="100" w:type="dxa"/>
                            <w:left w:w="100" w:type="dxa"/>
                            <w:right w:w="100" w:type="dxa"/>
                        </w:tcMar>
                    </w:tcPr>
                    {cell_xml}
                </w:tc>
                """
            if len(pair) == 1:
                tbl_xml += """
                <w:tc>
                    <w:tcPr>
                        <w:tcW w:w="2500" w:type="pct"/>
                        <w:shd w:val="clear" w:color="auto" w:fill="F8FAFC"/>
                    </w:tcPr>
                    <w:p/>
                </w:tc>
                """
            tbl_xml += "</w:tr>"
        tbl_xml += "</w:tbl>"
        return tbl_xml

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
                align_val = "center" if is_header else "right"
                tbl_xml += f"""
                <w:tc>
                    <w:tcPr>
                        <w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>
                        <w:tcMar>
                            <w:top w:w="100" w:type="dxa"/>
                            <w:bottom w:w="100" w:type="dxa"/>
                            <w:left w:w="140" w:type="dxa"/>
                            <w:right w:w="140" w:type="dxa"/>
                        </w:tcMar>
                    </w:tcPr>
                    {w_para(c_text, bold=is_header, size_pt=11, color=txt_color, align=align_val, space_after=0)}
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
    if len(index_rows) == 1:
        index_rows.append([("-", False), ("لا توجد شواهد مرفوعة بعد", False), ("-", False), ("0", False), ("-", False)])
    body_parts.append(w_table(index_rows))
    if sorted_evs:
        body_parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    for idx, ev in enumerate(sorted_evs):
        std = stds_map.get(ev['standard_id'], {"title": "", "weight": 10})
        exec_date = ev.get('execution_date') or ev['created_at'][:10]
        files = ev.get('evidence_files', [])
        links_list = [f['file_url'] for f in files if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http')]
        pdf_cnt = sum(1 for f in files if f.get('file_type') == 'application/pdf')

        att_notes = [f"إجمالي المرفقات: {len(files)}"]
        if pdf_cnt:
            att_notes.append(f"ملفات PDF: {pdf_cnt}")
        if links_list:
            att_notes.append(f"الرابط: {links_list[0]}")
        att_summary = " | ".join(att_notes)

        body_parts.append(w_para(f"المعيار {ev['standard_id']}: {std['title']} (الوزن {std['weight']}%)", bold=True, size_pt=15, color="0F5243", align="right", space_after=100))
        ev_rows = [
            [("عنوان الشاهد", True), (ev.get("title", ""), False)],
            [("تاريخ التنفيذ الفعلي", True), (str(exec_date), False)],
            [("وصف الشاهد والأثر", True), (ev.get("description") or "تم تنفيذ الشاهد وتوثيقه وفق خطة توزيع المنهج.", False)],
            [("المرفقات والروابط", True), (att_summary, False)],
            [("المعلم", True), (user_info.get("full_name", ""), False)],
            [("مدير المدرسة", True), (user_info.get("principal_name", ""), False)]
        ]
        body_parts.append(w_table(ev_rows))

        ev_img_drawings = []
        for f in files:
            f_url = f.get('file_url', '')
            f_type = f.get('file_type', '')
            if f_type.startswith('image/') and not f_url.startswith('http'):
                img_info = prepared_images_map.get(f_url)
                if img_info:
                    rel_id = f"rIdImg{img_counter}"
                    media_name = f"image_{img_counter}.jpg"
                    media_files[f"word/media/{media_name}"] = img_info["bytes"]
                    rels_entries.append(
                        f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>'
                    )
                    ev_img_drawings.append(w_image_para(rel_id, img_counter, img_info["cx"], img_info["cy"]))
                    img_counter += 1

        if ev_img_drawings:
            body_parts.append(w_para("صور الشواهد المرفقة:", bold=True, size_pt=12, color="0F5243", align="right", space_after=80))
            body_parts.append(w_images_grid_table(ev_img_drawings))

        body_parts.append(w_para("ملاحظات إضافية / تعديل:", bold=True, size_pt=10, color="64748B", align="right", space_after=100))
        if idx < len(sorted_evs) - 1:
            body_parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
        <w:body>
            {''.join(body_parts)}
            <w:sectPr>
                <w:bidi/>
                <w:pgSz w:w="11906" w:h="16838"/>
                <w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900"/>
            </w:sectPr>
        </w:body>
    </w:document>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
        <Default Extension="xml" ContentType="application/xml"/>
        <Default Extension="jpg" ContentType="image/jpeg"/>
        <Default Extension="jpeg" ContentType="image/jpeg"/>
        <Default Extension="png" ContentType="image/png"/>
        <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    </Types>"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    </Relationships>"""

    doc_rels_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        {''.join(rels_entries)}
    </Relationships>"""

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as docx_zip:
        docx_zip.writestr("[Content_Types].xml", content_types_xml.strip())
        docx_zip.writestr("_rels/.rels", rels_xml.strip())
        docx_zip.writestr("word/_rels/document.xml.rels", doc_rels_xml.strip())
        docx_zip.writestr("word/document.xml", document_xml.strip())
        for m_path, m_bytes in media_files.items():
            docx_zip.writestr(m_path, m_bytes)
    return buf.getvalue()

def generate_excel_csv(stds, evidences):
    stds_map = {s['id']: s['title'] for s in stds}
    lines = ["رقم المعيار,اسم المعيار,عنوان الشاهد,تاريخ التنفيذ,الوصف,عدد المرفقات"]
    for ev in sort_evidences_chronologically(evidences):
        s_id = ev.get('standard_id', '')
        s_title = str(stds_map.get(s_id, '')).replace(',', ' - ')
        title = str(ev.get('title', '')).replace(',', ' - ').replace('\n', ' ')
        exec_d = ev.get('execution_date') or ev.get('created_at', '')[:10]
        desc = str(ev.get('description', '') or '').replace(',', ' - ').replace('\n', ' ')
        f_cnt = len(ev.get('evidence_files', []))
        lines.append(f"{s_id},{s_title},{title},{exec_d},{desc},{f_cnt}")
    return "\ufeff" + "\n".join(lines)

def generate_attachments_zip(user_info, active_year, all_years, stds, all_subs, evidences, signed_urls_map):
    stds_map = {s['id']: s['title'] for s in stds}
    sorted_evs = sort_evidences_chronologically(evidences)

    download_tasks = []
    for ev in sorted_evs:
        for f_rec in ev.get("evidence_files", []):
            f_url = f_rec.get("file_url", "")
            f_type = f_rec.get("file_type", "")
            if f_type != "external/link" and not f_url.startswith("http"):
                download_tasks.append((f_url, signed_urls_map.get(f_url, "")))

    downloaded_map = {}
    if download_tasks:
        def _dl_file(pair):
            f_p, s_u = pair
            raw_b = None
            try:
                raw_b = supabase.storage.from_("private-achievements").download(f_p)
            except Exception:
                if s_u:
                    try:
                        req = urllib.request.Request(s_u, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            raw_b = resp.read()
                    except Exception:
                        pass
            return f_p, raw_b

        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                for k_path, k_bytes in executor.map(_dl_file, download_tasks):
                    if k_bytes:
                        downloaded_map[k_path] = k_bytes
        except Exception:
            pass

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        csv_str = generate_excel_csv(stds, sorted_evs)
        zf.writestr("سجل_الشواهد.csv", csv_str.encode("utf-8"))

        full_backup = {
            "user_profile": user_info,
            "academic_years": all_years,
            "standards": stds,
            "sub_items": all_subs,
            "evidences": sorted_evs
        }
        zf.writestr("نسخة_النظام_الاحتياطية.json", json.dumps(full_backup, ensure_ascii=False, indent=4).encode("utf-8"))

        for idx, ev in enumerate(sorted_evs, 1):
            s_id = ev.get("standard_id", 1)
            s_title = sanitize_filename_part(stds_map.get(s_id, f"معيار_{s_id}"))
            ev_title = sanitize_filename_part(ev.get("title", f"شاهد_{idx}"))
            exec_d = sanitize_filename_part(ev.get("execution_date") or ev.get("created_at", "")[:10])
            folder_path = f"البند_{s_id}_{s_title}/{idx}_{ev_title}_{exec_d}"

            info_txt = (
                f"عنوان الشاهد: {ev.get('title', '')}\n"
                f"المعيار: {s_id} - {stds_map.get(s_id, '')}\n"
                f"تاريخ التنفيذ: {ev.get('execution_date') or ev.get('created_at', '')[:10]}\n"
                f"الوصف:\n{ev.get('description') or ''}\n"
            )
            zf.writestr(f"{folder_path}/بيانات_الشاهد.txt", info_txt.encode("utf-8"))

            for f_idx, f_rec in enumerate(ev.get("evidence_files", []), 1):
                f_url = f_rec.get("file_url", "")
                f_type = f_rec.get("file_type", "")
                if f_type == "external/link" or f_url.startswith("http"):
                    zf.writestr(f"{folder_path}/رابط_خارجي_{f_idx}.txt", f_url.encode("utf-8"))
                    continue

                ext = f_url.split(".")[-1].lower() if "." in f_url else ("pdf" if f_type == "application/pdf" else "jpg")
                raw_file_bytes = downloaded_map.get(f_url)
                if raw_file_bytes:
                    zf.writestr(f"{folder_path}/مرفق_{f_idx}.{ext}", raw_file_bytes)

    return buf.getvalue()

user_info = get_user_profile()
active_theme_key = user_info.get("theme", "emerald")
if active_theme_key not in THEMES:
    active_theme_key = "emerald"
th = THEMES[active_theme_key]

ZIYAD_LOGO_SVG = '<svg width="52" height="52" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="18" fill="white" fill-opacity="0.16"/><rect x="1.5" y="1.5" width="61" height="61" rx="16.5" stroke="white" stroke-opacity="0.38" stroke-width="2"/><path d="M32 14L12 24L32 34L52 24L32 14Z" fill="#FBBF24"/><path d="M20 29V41C20 44.5 25.5 48 32 48C38.5 48 44 44.5 44 41V29L32 35L20 29Z" fill="white"/><path d="M48 26V40" stroke="#FBBF24" stroke-width="3" stroke-linecap="round"/></svg>'

# ==========================================
# 7. التصميم الشامل وتوحيد خط Cairo وإخفاء دوائر الراديو وعلامات الروابط
# ==========================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

*::-webkit-scrollbar,
html::-webkit-scrollbar,
body::-webkit-scrollbar,
.stApp::-webkit-scrollbar,
[data-testid="stAppViewContainer"]::-webkit-scrollbar,
[data-testid="stMain"]::-webkit-scrollbar,
.main::-webkit-scrollbar,
.block-container::-webkit-scrollbar {{
    display: none !important;
    width: 0px !important;
    height: 0px !important;
    background: transparent !important;
}}

*, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {{
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}}

:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
    --text-color: #0f172a !important;
    --background-color: {th['bg']} !important;
    --secondary-background-color: #ffffff !important;
    --primary-color: {th['primary']} !important;
    --font: 'Cairo', sans-serif !important;
    color-scheme: light only !important;
    direction: rtl !important; 
    text-align: right !important; 
    font-family: 'Cairo', sans-serif !important;
    background-color: {th['bg']} !important;
    color: #0f172a !important;
    overflow-x: clip !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overscroll-behavior-x: none !important;
    touch-action: pan-y !important;
}}

*:not([data-testid="stIconMaterial"]):not(.material-icons):not([class*="material-symbols"]):not(svg):not(path) {{
    font-family: 'Cairo', sans-serif !important;
}}

header {{visibility: hidden; height: 0 !important;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
.stSidebar {{display: none !important;}}

/* إخفاء أيقونات الروابط (Anchor Links) التي تظهر بجانب العناوين تماماً */
[data-testid="stHeaderActionElements"],
.stMarkdown h1 a,
.stMarkdown h2 a,
.stMarkdown h3 a,
.stMarkdown h4 a,
.stMarkdown h5 a,
.stMarkdown h6 a,
h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a,
a.anchor-link {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}}

.block-container {{
    padding: 0.7rem 0.75rem 2rem 0.75rem !important;
    max-width: 760px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    direction: rtl !important;
    text-align: right !important;
}}
[data-testid="stVerticalBlock"] {{
    gap: 0.5rem !important;
    max-width: 100% !important;
    overflow: visible !important;
    direction: rtl !important;
}}
div.element-container, [data-testid="stMarkdownContainer"] {{
    max-width: 100% !important;
    overflow: visible !important;
    direction: rtl !important;
    text-align: right !important;
}}

h1, h2, h3, h4, h5, h6, p, label, .stMarkdown,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {{
    font-family: 'Cairo', sans-serif !important;
    color: #0f172a;
    direction: rtl !important;
    word-wrap: break-word !important;
    letter-spacing: 0px !important;
}}

h1, h2, h3, h4, h5 {{
    font-weight: 800 !important;
    letter-spacing: 0px !important;
}}

.section-heading {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    color: #0f172a !important;
    margin: 8px 0 10px 0 !important;
    direction: rtl !important;
    text-align: right !important;
}}
.sub-heading {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 15.5px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin: 10px 0 8px 0 !important;
    direction: rtl !important;
    text-align: right !important;
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
    background-color: #f8fafc !important;
    background: #f8fafc !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: {th['primary']} !important;
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 600 !important;
}}

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {{
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.02) !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] svg {{
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    fill: #0f172a !important;
    background-color: transparent !important;
    direction: rtl !important;
    text-align: right !important;
    white-space: normal !important;
    line-height: 1.4 !important;
    font-weight: 700 !important;
}}

input::placeholder, textarea::placeholder {{
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    opacity: 1 !important;
    direction: rtl !important;
    text-align: right !important;
}}

div[data-testid="stAlert"], div[data-testid="stAlert"] > div, div[role="alert"] {{
    background-color: {th['tint']} !important;
    background: {th['tint']} !important;
    color: {th['primary_dark']} !important;
    border: 1px solid {th['primary']} !important;
    border-radius: 14px !important;
    direction: rtl !important;
    text-align: right !important;
}}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div[role="alert"] p {{
    color: {th['primary_dark']} !important;
    -webkit-text-fill-color: {th['primary_dark']} !important;
    font-weight: 700 !important;
    direction: rtl !important;
    text-align: right !important;
}}

div[data-testid="stFileUploader"] section {{
    background-color: #ffffff !important;
    border: 1.5px dashed #94a3b8 !important;
    border-radius: 14px !important;
    color: #0f172a !important;
    padding: 12px !important;
    direction: rtl !important;
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
    border-radius: 20px !important;
    padding: 22px 20px !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04) !important;
    width: 100% !important;
    box-sizing: border-box !important;
    direction: rtl !important;
    text-align: right !important;
}}

[data-testid="stExpander"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    width: 100% !important;
    direction: rtl !important;
    text-align: right !important;
}}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpanderDetails"] {{
    background-color: #ffffff !important;
    color: {th['primary']} !important;
    font-weight: 800 !important;
    direction: rtl !important;
    text-align: right !important;
}}

button[data-baseweb="tab"] {{
    background-color: transparent !important;
    color: #475569 !important;
    font-weight: 800 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {th['primary']} !important;
    border-bottom-color: {th['primary']} !important;
}}

div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {{
    background-color: #e6f4f1 !important;
    color: {th['primary']} !important;
    border: 1px solid #b7e0d6 !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 44px !important;
    padding: 0.4rem 0.85rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    white-space: normal !important;
    direction: rtl !important;
}}
div[data-testid="stButton"] button p, div[data-testid="stDownloadButton"] button p {{
    color: {th['primary']} !important;
    -webkit-text-fill-color: {th['primary']} !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    white-space: normal !important;
    line-height: 1.3 !important;
    text-align: center !important;
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
    background: linear-gradient(135deg, {th['primary_dark']}, {th['primary']}, {th['primary_light']}) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 13px !important;
    min-height: 50px !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.15) !important;
}}
div[data-testid="stButton"] button[kind="primary"] p, div[data-testid="stFormSubmitButton"] button p, div[data-testid="stDownloadButton"] button[kind="primary"] p {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    text-align: center !important;
}}

/* ========================================================= */
/* شريط التبويبات الكبسولات (Pills) - إخفاء دائرة الراديو الحمراء/الرمادية نهائياً */
/* ========================================================= */
div[data-testid="stRadio"] {{
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 6px !important;
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
    gap: 8px !important;
    background: #ffffff !important;
    padding: 6px !important;
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.03) !important;
    justify-content: stretch !important;
    align-items: stretch !important;
    direction: rtl !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] > label,
div[data-testid="stRadio"] label[data-baseweb="radio"] {{
    flex: 1 1 0% !important;
    min-width: 0 !important;
    min-height: 42px !important;
    margin: 0 !important;
    padding: 8px 10px !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    transition: all 0.18s ease !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover,
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
    background: {th['tint']} !important;
    border-color: {th['primary']} !important;
}}
div[data-testid="stRadio"] label > div:not(:has([data-testid="stMarkdownContainer"])),
div[data-testid="stRadio"] input[type="radio"] {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
}}
div[data-testid="stRadio"] label > div:has([data-testid="stMarkdownContainer"]),
div[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: auto !important;
    opacity: 1 !important;
    visibility: visible !important;
    position: static !important;
    margin: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
    white-space: nowrap !important;
    text-align: center !important;
}}
div[data-testid="stRadio"] label:has(input:checked),
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {{
    background: linear-gradient(135deg, {th['primary_dark']}, {th['primary']}, {th['primary_light']}) !important;
    border: 2px solid #f59e0b !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}}
div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label:has(input:checked) span {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
}}

/* ========================================================= */
/* البنر الزجاجي ثلاثي الأبعاد المطابق لفيديو منصة زياد الذكية */
/* ========================================================= */
.hero-wrapper {{
    background: linear-gradient(135deg, {th['primary_dark']} 0%, {th['primary']} 52%, {th['primary_light']} 100%) !important;
    color: #ffffff !important;
    padding: 20px 24px;
    border-radius: 24px;
    margin-bottom: 10px;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.35), 0 12px 26px rgba(15, 23, 42, 0.16) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    box-sizing: border-box;
    width: 100%;
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Cairo', sans-serif !important;
}}

/* تصميم بنر صفحة الدخول */
.login-banner-flex {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    padding: 10px 6px;
    direction: rtl !important;
}}
.login-Main-title {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 30px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    margin: 0 !important;
    line-height: 1.3 !important;
    letter-spacing: 0px !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}
.login-portal-pill {{
    font-family: 'Cairo', sans-serif !important;
    background: rgba(15, 23, 42, 0.32) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    padding: 7px 18px;
    border-radius: 99px;
    font-size: 14px !important;
    font-weight: 800 !important;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: inset 0 1px 2px rgba(255,255,255,0.2);
}}
.login-card-heading {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    text-align: right !important;
    margin: 0 0 12px 0 !important;
    padding-bottom: 10px;
    border-bottom: 1px solid #f1f5f9;
}}

/* أزرار التواصل والمنصات المباشرة (بدون إظهار الأرقام أو الإيميل أو الروابط) */
.contact-grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin-top: 12px;
    direction: rtl !important;
}}
.contact-grid-2 {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-top: 10px;
    direction: rtl !important;
}}
@media (max-width: 520px) {{
    .contact-grid-3 {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 6px;
    }}
    .contact-grid-2 {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 6px;
    }}
}}
.contact-pill-card {{
    font-family: 'Cairo', sans-serif !important;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 11px 10px;
    text-align: center !important;
    text-decoration: none !important;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    transition: all 0.18s ease;
    cursor: pointer;
}}
.contact-pill-card:hover {{
    border-color: {th['primary']} !important;
    background: {th['tint']} !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
}}
.contact-pill-title {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    color: #334155 !important;
    text-align: center !important;
    white-space: nowrap;
}}
.contact-pill-card:hover .contact-pill-title {{
    color: {th['primary']} !important;
}}

/* بنر الصفحة الرئيسية بعد الدخول */
.hero-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.16);
    padding-bottom: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
    direction: rtl !important;
}}
.brand-box {{ display: flex; align-items: center; gap: 12px; direction: rtl !important; }}
.brand-title {{ font-family: 'Cairo', sans-serif !important; font-size: 21px !important; font-weight: 900 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 0; text-align: right !important; letter-spacing: 0px !important; }}
.brand-sub {{ font-family: 'Cairo', sans-serif !important; font-size: 12px !important; font-weight: 700 !important; color: #fde68a !important; -webkit-text-fill-color: #fde68a !important; margin: 2px 0 0 0; text-align: right !important; }}
.date-pill {{
    font-family: 'Cairo', sans-serif !important;
    background: rgba(15, 23, 42, 0.35);
    padding: 5px 12px;
    border-radius: 99px;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.22);
    direction: rtl !important;
}}
.hero-body {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 10px;
    direction: rtl !important;
}}
.welcome-line {{ font-family: 'Cairo', sans-serif !important; font-size: 13px !important; color: #fde68a !important; -webkit-text-fill-color: #fde68a !important; font-weight: 700 !important; margin-bottom: 2px; text-align: right !important; }}
.teacher-name {{ font-family: 'Cairo', sans-serif !important; font-size: 22px !important; font-weight: 900 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 0 0 8px 0; text-align: right !important; letter-spacing: 0px !important; }}
.meta-badges {{ display: flex; flex-wrap: wrap; gap: 6px; direction: rtl !important; }}
.meta-pill {{
    font-family: 'Cairo', sans-serif !important;
    background: rgba(0,0,0,0.25);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    padding: 4px 10px;
    border-radius: 9px;
    font-size: 11.5px !important;
    font-weight: 700 !important;
}}
.year-badge {{
    font-family: 'Cairo', sans-serif !important;
    background: #fbbf24 !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    padding: 6px 14px;
    border-radius: 12px;
    font-size: 13px !important;
    font-weight: 800 !important;
}}

.kpi-grid {{
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-bottom: 8px; width: 100%; box-sizing: border-box; direction: rtl !important;
}}
.kpi-card {{
    background: #ffffff; border-radius: 16px; padding: 12px 6px; text-align: center !important;
    border: 1px solid #e2e8f0; box-shadow: 0 3px 8px rgba(0,0,0,0.03);
}}
.kpi-val {{ font-family: 'Cairo', sans-serif !important; font-size: 21px; font-weight: 900; color: {th['primary']} !important; text-align: center !important; }}
.kpi-lbl {{ font-family: 'Cairo', sans-serif !important; font-size: 11.5px; color: #475569 !important; margin-top: 2px; font-weight: 700; text-align: center !important; }}

.progress-card {{
    background: #ffffff; padding: 12px 16px; border-radius: 15px; 
    margin-bottom: 6px; border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box; direction: rtl !important;
}}
.progress-bar-bg {{
    background: #e2e8f0; height: 9px; border-radius: 5px; width: 100%; overflow: hidden; margin-top: 6px; direction: rtl !important;
}}
.progress-bar-fill {{
    background: linear-gradient(90deg, {th['primary']}, {th['primary_light']});
    height: 100%; border-radius: 5px;
}}

.std-card {{
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 13px 15px; margin-bottom: 2px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02); width: 100%; box-sizing: border-box;
    direction: rtl !important; text-align: right !important;
}}
.std-num {{
    font-family: 'Cairo', sans-serif !important;
    width: 40px; height: 40px; border-radius: 12px;
    background: {th['tint']}; color: {th['primary']} !important;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 17px; margin-left: 12px; flex-shrink: 0;
}}
.std-num-empty {{ background: #fee2e2; color: #dc2626 !important; }}
.std-title {{ font-family: 'Cairo', sans-serif !important; font-size: 15.5px; font-weight: 800; color: #0f172a !important; margin-bottom: 3px; text-align: right !important; direction: rtl !important; letter-spacing: 0px !important; }}
.weight-badge {{
    font-family: 'Cairo', sans-serif !important;
    background: #f1f5f9; color: #475569 !important; font-size: 11.5px; padding: 2px 9px;
    border-radius: 8px; display: inline-block; font-weight: 700;
}}
.dots-row {{ display: flex; gap: 4px; margin-bottom: 4px; justify-content: flex-end; }}
.dot {{ width: 12px; height: 5px; border-radius: 3px; }}
.dot-on {{ background: {th['primary']}; }}
.dot-off {{ background: #e2e8f0; }}

.ev-box {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px 14px 4px 4px;
    padding: 14px 16px;
    margin-bottom: 2px;
    border-right: 4px solid {th['primary']};
    width: 100%;
    box-sizing: border-box;
    direction: rtl !important;
    text-align: right !important;
}}
.ev-box * {{
    direction: rtl !important;
    font-family: 'Cairo', sans-serif !important;
}}
.ev-header-row {{
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    margin-bottom: 8px !important;
    direction: rtl !important;
    text-align: right !important;
}}
.ev-title-right {{
    font-family: 'Cairo', sans-serif !important;
    font-weight: 800 !important;
    font-size: 15.5px !important;
    color: {th['primary']} !important;
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: isolate !important;
}}
.ev-desc-rtl {{
    font-family: 'Cairo', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #334155 !important;
    line-height: 1.75 !important;
    margin-bottom: 8px !important;
    white-space: pre-line !important;
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: plaintext !important;
}}
.thumbs-container {{
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    margin: 8px 0 4px 0 !important;
    align-items: center !important;
    direction: rtl !important;
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
    font-weight: 700; text-align: center !important; padding: 2px 0;
}}
.pdf-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 42px; padding: 0 12px; border-radius: 9px;
    background: #f8fafc; border: 1.5px dashed {th['primary']};
    color: {th['primary']} !important; font-weight: 800; font-size: 12px; text-decoration: none;
}}
.ext-link-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    height: 42px; padding: 0 14px; border-radius: 9px;
    background: #eff6ff; border: 1.5px solid #2563eb;
    color: #1d4ed8 !important; font-weight: 800; font-size: 12px; text-decoration: none;
}}

.idea-card {{
    font-family: 'Cairo', sans-serif !important;
    background: #ffffff; border: 1px solid #e2e8f0; padding: 9px 12px;
    border-radius: 10px; margin-bottom: 5px; font-size: 13px; font-weight: 700; color: #1e293b !important;
    display: flex; justify-content: space-between; align-items: center;
    direction: rtl !important; text-align: right !important;
}}
.visitor-banner {{
    font-family: 'Cairo', sans-serif !important;
    background: #fef3c7; color: #92400e !important; border: 1px solid #f59e0b;
    padding: 8px 14px; border-radius: 11px; margin-bottom: 8px;
    font-weight: 800; font-size: 13px; text-align: center !important;
}}

.ziyad-footer {{
    margin-top: 26px;
    padding: 16px 12px;
    background: #ffffff;
    border-top: 3px solid {th['primary']};
    border-radius: 16px;
    text-align: center !important;
    border: 1px solid #e2e8f0;
    width: 100%;
    box-sizing: border-box;
}}
.footer-brand {{ font-family: 'Cairo', sans-serif !important; font-size: 13.5px; font-weight: 800; color: #334155 !important; margin-bottom: 4px; text-align: center !important; }}
.footer-rights {{ font-family: 'Cairo', sans-serif !important; font-size: 11.5px; font-weight: 600; color: #64748b !important; text-align: center !important; }}
</style>
""", unsafe_allow_html=True)

# حقن خط Cairo في الصفحة الأم + إزالة دوائر الراديو وعلامات الروابط نهائياً عبر الـ DOM + فرض RTL للقوائم المنسدلة
components.html(f"""
<script>
(function() {{
    try {{
        var pDoc = window.parent.document;
        pDoc.documentElement.setAttribute('dir', 'rtl');
        pDoc.body.setAttribute('dir', 'rtl');

        var fontId = 'ziyad-google-fonts';
        if (!pDoc.getElementById(fontId)) {{
            var link = pDoc.createElement('link');
            link.id = fontId;
            link.rel = 'stylesheet';
            link.href = 'https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap';
            pDoc.head.appendChild(link);
        }}

        var styleId = 'ziyad-global-portal-rtl';
        var existingStyle = pDoc.getElementById(styleId);
        if (!existingStyle) {{
            existingStyle = pDoc.createElement('style');
            existingStyle.id = styleId;
            pDoc.head.appendChild(existingStyle);
        }}
        existingStyle.innerHTML = `
            *::-webkit-scrollbar {{
                display: none !important;
                width: 0px !important;
                height: 0px !important;
            }}
            *, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container {{
                scrollbar-width: none !important;
                -ms-overflow-style: none !important;
            }}
            *:not([data-testid="stIconMaterial"]):not(.material-icons):not([class*="material-symbols"]):not(svg):not(path) {{
                font-family: 'Cairo', sans-serif !important;
            }}
            [data-testid="stHeaderActionElements"],
            h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, a.anchor-link {{
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
                height: 0 !important;
                opacity: 0 !important;
            }}
            .block-container {{
                overflow: visible !important;
            }}
            div[data-testid="stRadio"] label > div:not(:has([data-testid="stMarkdownContainer"])),
            div[data-testid="stRadio"] input[type="radio"] {{
                display: none !important;
                width: 0px !important;
                height: 0px !important;
                opacity: 0 !important;
                position: absolute !important;
            }}
            div[data-testid="stRadio"] label > div:has([data-testid="stMarkdownContainer"]),
            div[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                height: auto !important;
                opacity: 1 !important;
                visibility: visible !important;
                position: static !important;
            }}
            div[data-baseweb="popover"],
            div[data-baseweb="popover"] *,
            div[data-baseweb="menu"],
            div[data-baseweb="menu"] *,
            ul[data-testid="stSelectboxVirtualDropdown"],
            ul[data-testid="stSelectboxVirtualDropdown"] *,
            ul[role="listbox"],
            ul[role="listbox"] *,
            li[role="option"],
            li[role="option"] * {{
                direction: rtl !important;
                text-align: right !important;
                font-family: 'Cairo', sans-serif !important;
            }}
            li[role="option"] {{
                display: flex !important;
                flex-direction: row !important;
                justify-content: flex-start !important;
                align-items: center !important;
                padding: 10px 14px !important;
                background-color: #ffffff !important;
                color: #0f172a !important;
                font-weight: 700 !important;
            }}
            li[role="option"]:hover,
            li[role="option"][aria-selected="true"] {{
                background-color: {th['tint']} !important;
                color: {th['primary']} !important;
                font-weight: 800 !important;
            }}
        `;

        function enforcePortalRTL() {{
            var nodes = pDoc.querySelectorAll('[data-baseweb="popover"], [data-baseweb="menu"], [data-testid="stSelectboxVirtualDropdown"], ul[role="listbox"], li[role="option"]');
            nodes.forEach(function(el) {{
                el.setAttribute('dir', 'rtl');
                el.style.setProperty('direction', 'rtl', 'important');
                el.style.setProperty('text-align', 'right', 'important');
                var children = el.querySelectorAll('div, span');
                children.forEach(function(ch) {{
                    ch.setAttribute('dir', 'rtl');
                    ch.style.setProperty('direction', 'rtl', 'important');
                    ch.style.setProperty('text-align', 'right', 'important');
                }});
            }});

            var anchors = pDoc.querySelectorAll('[data-testid="stHeaderActionElements"], h1 a, h2 a, h3 a, h4 a, h5 a, h6 a');
            anchors.forEach(function(a) {{
                a.style.setProperty('display', 'none', 'important');
            }});

            var radioLabels = pDoc.querySelectorAll('div[data-testid="stRadio"] label');
            radioLabels.forEach(function(lbl) {{
                Array.from(lbl.children).forEach(function(child) {{
                    if (child.tagName === 'INPUT') {{
                        child.style.setProperty('display', 'none', 'important');
                    }} else if (child.tagName === 'DIV') {{
                        if (child.querySelector('[data-testid="stMarkdownContainer"]') || (child.textContent && child.textContent.trim().length > 0)) {{
                            child.style.setProperty('display', 'flex', 'important');
                            child.style.setProperty('visibility', 'visible', 'important');
                            child.style.setProperty('opacity', '1', 'important');
                            child.style.setProperty('width', '100%', 'important');
                            child.style.setProperty('justify-content', 'center', 'important');
                        }} else {{
                            child.style.setProperty('display', 'none', 'important');
                            child.style.setProperty('width', '0px', 'important');
                            child.style.setProperty('height', '0px', 'important');
                        }}
                    }}
                }});
            }});
        }}

        enforcePortalRTL();
        if (!window.parent.__ziyadRtlObserverAttached) {{
            var obs = new MutationObserver(function() {{
                enforcePortalRTL();
            }});
            obs.observe(pDoc.body, {{ childList: true, subtree: true }});
            window.parent.__ziyadRtlObserverAttached = true;
        }}
    }} catch (e) {{}}
}})();
</script>
""", height=0)

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
    thumbs_html = '<div class="thumbs-container" dir="rtl">'
    for i, f_rec in enumerate(files):
        f_url = f_rec.get('file_url', '')
        f_type = f_rec.get('file_type', '')
        if f_type == 'external/link' or f_url.startswith('http'):
            safe_ext_u = html.escape(f_url, quote=True)
            thumbs_html += f'<a href="{safe_ext_u}" target="_blank" class="ext-link-badge" dir="rtl">🔗 فتح الرابط المرفق</a>'
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
                thumbs_html += f'<a href="{sec_url}" target="_blank" class="pdf-badge" dir="rtl">📄 ملف PDF ({i+1})</a>'
    thumbs_html += '</div>'
    return thumbs_html

def render_evidence_edit_and_delete(ev, signed_urls_map, stds, key_prefix=""):
    files = ev.get("evidence_files", [])
    exec_date = ev.get('execution_date') or ev['created_at'][:10]
    existing_links = [f['file_url'] for f in files if f.get('file_type') == 'external/link' or f.get('file_url', '').startswith('http')]
    current_ext_link = existing_links[0] if existing_links else ""
    storage_files = [f for f in files if f.get('file_type') != 'external/link' and not f.get('file_url', '').startswith('http')]

    std_options_dict = {s['id']: f"البند {s['id']}: {s['title']}" for s in stds}
    std_ids_list = list(std_options_dict.keys())
    current_ev_std_id = ev.get('standard_id', 1)
    default_std_idx = std_ids_list.index(current_ev_std_id) if current_ev_std_id in std_ids_list else 0

    with st.expander("⚙️ إدارة وتعديل الشاهد / نقل البند / التحكم بالصور والمرفقات"):
        tab_edit, tab_del = st.tabs(["✏️ تعديل البيانات وإدارة الصور", "🗑️ حذف الشاهد بالكامل"])

        with tab_edit:
            if storage_files:
                st.markdown('<div class="sub-heading">🖼️ الصور والمرفقات الحالية (يمكنك حذف أي مرفق بمفرده):</div>', unsafe_allow_html=True)
                cols_count = min(len(storage_files), 3)
                att_cols = st.columns(cols_count)
                for idx_f, f_obj in enumerate(storage_files):
                    with att_cols[idx_f % cols_count]:
                        f_u = signed_urls_map.get(f_obj['file_url'], '')
                        if f_obj.get('file_type', '').startswith('image/') and f_u:
                            st.markdown(
                                f'<div dir="rtl" style="border:1px solid #cbd5e1; border-radius:12px; padding:6px; background:#f8fafc; text-align:center; margin-bottom:6px;">'
                                f'<img src="{f_u}" style="width:100%; height:110px; object-fit:contain; border-radius:8px; background:white;">'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div dir="rtl" style="border:1px dashed #64748b; border-radius:12px; height:110px; display:flex; align-items:center; justify-content:center; background:#f8fafc; margin-bottom:6px; font-weight:700; font-size:13px;">'
                                f'📄 ملف PDF رقم ({idx_f+1})'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        if st.button(f"🗑️ حذف صورة ({idx_f+1})", key=f"{key_prefix}del_att_{ev['id']}_{f_obj['id']}", use_container_width=True):
                            try:
                                supabase.storage.from_("private-achievements").remove([f_obj['file_url']])
                            except Exception:
                                pass
                            supabase.table("evidence_files").delete().eq("id", f_obj['id']).execute()
                            clear_app_cache()
                            st.success("تم حذف الصورة المحددة بنجاح!")
                            time.sleep(0.3)
                            st.rerun()
                st.write("---")

            with st.form(f"{key_prefix}edit_form_{ev['id']}"):
                new_std_id = st.selectbox(
                    "⇄ البند (المعيار) التابع له الشاهد (اختر بنداً آخر لنقله):",
                    options=std_ids_list,
                    format_func=lambda x: std_options_dict[x],
                    index=default_std_idx,
                    key=f"{key_prefix}move_std_{ev['id']}"
                )

                col_t, col_d = st.columns([2, 1])
                with col_t:
                    new_t = st.text_input("عنوان الشاهد:", value=ev['title'])
                with col_d:
                    try:
                        default_d = datetime.date.fromisoformat(str(exec_date)[:10])
                    except Exception:
                        default_d = datetime.date.today()
                    new_exec_date = st.date_input("📅 تاريخ التنفيذ:", value=default_d)

                new_d = st.text_area("وصف الشاهد:", value=ev.get('description', ''), height=115)

                col_up, col_mode = st.columns([3, 2])
                with col_up:
                    new_files = st.file_uploader(
                        "📎 إرفاق صور أو ملفات PDF جديدة (اختياري):",
                        type=["pdf", "jpg", "jpeg", "png"],
                        accept_multiple_files=True,
                        key=f"{key_prefix}up_{ev['id']}"
                    )
                with col_mode:
                    upload_mode = st.selectbox(
                        "عند رفع ملفات جديدة:",
                        [
                            "➕ إضافتها للصور الحالية",
                            "🔄 استبدال الصور السابقة"
                        ],
                        key=f"{key_prefix}mode_{ev['id']}"
                    )

                new_ext_link = st.text_input("🔗 أو رابط خارجي (امسحه لحذفه أو عدله):", value=current_ext_link, placeholder="https://")
                
                if st.form_submit_button("حفظ كافة التعديلات 💾", type="primary", use_container_width=True):
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
                            opt_bytes, opt_mime, opt_ext = optimize_uploaded_image(nf)
                            path = f"{ev['id']}/{uuid.uuid4()}.{opt_ext}"
                            supabase.storage.from_("private-achievements").upload(path=path, file=opt_bytes, file_options={"content-type": opt_mime})
                            supabase.table("evidence_files").insert({"evidence_id": ev['id'], "file_url": path, "file_type": opt_mime}).execute()

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
                        st.success("تم حفظ التعديلات وإعادة ترتيب الشواهد زمنياً بنجاح!")
                    time.sleep(0.4)
                    st.rerun()

        with tab_del:
            st.warning("⚠️ تنبيه: حذف الشاهد بالكامل سيؤدي إلى إزالته مع كافة الصور والمرفقات المرتبطة به نهائياً.")
            if st.button("🗑️ تأكيد حذف الشاهد بالكامل نهائياً", key=f"{key_prefix}confirm_del_{ev['id']}", type="primary", use_container_width=True):
                old_storage_paths = [f['file_url'] for f in storage_files]
                if old_storage_paths:
                    try:
                        supabase.storage.from_("private-achievements").remove(old_storage_paths)
                    except Exception:
                        pass
                supabase.table("evidences").delete().eq("id", ev['id']).execute()
                clear_app_cache()
                st.success("تم حذف الشاهد بالكامل!")
                time.sleep(0.3)
                st.rerun()

def build_pdf_report_html(user_info, active_year, stds, evidences, ev_by_std, signed_urls_map, report_style, th):
    stds_map = {s['id']: s for s in stds}
    all_evidences = sort_evidences_chronologically(evidences)
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

    safe_t_name = html.escape(str(user_info.get('full_name', '')))
    safe_spec = html.escape(str(user_info.get('specialization', '')))
    safe_school = html.escape(str(user_info.get('school_name', '')))
    safe_stage = html.escape(str(user_info.get('education_stage', '')))
    safe_city = html.escape(str(user_info.get('city', '')))
    safe_prin = html.escape(str(user_info.get('principal_name', '')))
    safe_y_name = html.escape(str(active_year.get('year_name', '')))

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>ملف الإنجاز المهني - {safe_t_name}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
            * {{ box-sizing: border-box; direction: rtl; font-family: 'Cairo', sans-serif !important; }}
            body {{ font-family: 'Cairo', sans-serif !important; background-color: #cbd5e1; margin: 0; padding: 20px; direction: rtl; text-align: right; }}
            
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
                direction: rtl;
                text-align: right;
            }}
            
            .cover-page {{ border: {cover_border}; border-radius: {box_radius}; padding: 35px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; }}
            .cover-title {{ color: {rep_color}; font-size: 36px; font-weight: 900; margin-bottom: 10px; }}
            .cover-subtitle {{ font-size: 19px; margin-bottom: 35px; font-weight: 700; color: #475569; }}
            .info-table {{ width: 88%; border-collapse: collapse; margin: 0 auto; font-size: 16px; }}
            .info-table th, .info-table td {{ border: 1px solid #cbd5e1; padding: 12px; text-align: center; }}
            .info-table th {{ background-color: #f8fafc; width: 32%; font-weight: 800; color: {rep_color}; }}
            
            .header-container {{ display: flex; justify-content: space-between; border-bottom: 2px solid {rep_color}; padding-bottom: 6px; margin-bottom: 10px; font-size: 12px; font-weight: 800; flex-shrink: 0; }}
            .header-right {{ color: {rep_color}; text-align: right; }}
            .header-left {{ text-align: left; }}
            
            .index-title {{ color: {rep_color}; font-size: 22px; font-weight: 800; margin-bottom: 16px; text-align: right; }}
            .index-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            .index-table th {{ background-color: #f1f5f9; color: {rep_color}; padding: 10px; text-align: center; border-bottom: 2px solid {rep_color}; font-weight: 800; }}
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
            .top-ev-title {{ font-size: 16px; font-weight: 800; text-align: right; }}
            .top-std-sub {{ font-size: 12.5px; opacity: 0.92; text-align: left; }}
            
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; flex-shrink: 0; }}
            .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 7px 12px; text-align: center; border-radius: {box_radius}; }}
            .meta-title {{ font-size: 11px; color: #64748b; font-weight: 700; }}
            .meta-value {{ font-size: 13px; font-weight: 800; color: #0f172a; }}
            
            .desc-header {{
                border-right: 4px solid {rep_color};
                padding-right: 8px;
                font-size: 13.5px;
                font-weight: 800;
                color: {rep_color};
                margin-bottom: 4px;
                flex-shrink: 0;
                text-align: right;
            }}
            .desc-section {{
                margin-bottom: 10px;
                line-height: 1.6;
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
                direction: rtl;
                text-align: right;
            }}
            
            .shawahed-bar {{
                background-color: #e6f2ef;
                color: {rep_color};
                text-align: center;
                font-weight: 800;
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
            <div style="font-size:15px; font-weight:800; color:{rep_color}; margin-bottom:8px;">المملكة العربية السعودية • وزارة التعليم</div>
            <div style="font-size:13px; color:#b45309; font-weight:800; margin-bottom:12px;">🎓 منصة زياد الذكية لتوثيق الأداء المهني</div>
            <div class="cover-title">ملف الإنجاز المهني</div>
            <div class="cover-subtitle">توثيق شواهد الأداء الوظيفي</div>
            <table class="info-table">
                <tr><th>اسم المعلم</th><td>{safe_t_name}</td></tr>
                <tr><th>التخصص</th><td>{safe_spec}</td></tr>
                <tr><th>المدرسة</th><td>{safe_school}</td></tr>
                <tr><th>المرحلة الدراسية</th><td>{safe_stage}</td></tr>
                <tr><th>المدينة</th><td>{safe_city}</td></tr>
                <tr><th>مدير المدرسة</th><td>{safe_prin}</td></tr>
                <tr><th>العام الدراسي</th><td>{safe_y_name}هـ</td></tr>
                <tr><th>إجمالي الشواهد الموثقة</th><td>{total_evidences} شاهد ({covered_stds} من {len(stds)} معايير)</td></tr>
            </table>
            <div style="margin-top:35px; font-size:11px; color:#64748b;">صدر إلكترونياً عبر منصة زياد الذكية — جميع الحقوق محفوظة © أ. {safe_t_name}</div>
        </div>
    </div>
    """
    
    shared_header = f"""
    <div class="header-container">
        <div class="header-right">
            منصة زياد الذكية | أ. {safe_t_name}<br>
            <span style="font-size:10.5px; font-weight:normal; color:#666;">شواهد الأداء الوظيفي - العام الدراسي {safe_y_name}هـ</span>
        </div>
        <div class="header-left">
            المملكة العربية السعودية<br>
            <span style="font-size:10.5px; font-weight:normal; color:#666;">وزارة التعليم - {safe_school}</span>
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
        safe_s_title = html.escape(str(std['title']))
        html_content += f"<tr><td>{std['id']}</td><td style='text-align:right; font-weight:bold;'>{safe_s_title}</td><td>{std['weight']}%</td><td style='color:{rep_color}; font-weight:bold;'>{count}</td><td>{target}</td></tr>"
    html_content += f"""
        </table>
        <div class="print-footer" style="margin-top:auto;">منصة زياد الذكية | جميع الحقوق محفوظة © أ. {safe_t_name}</div>
    </div>
    """
    
    for ev in all_evidences:
        std = stds_map.get(ev['standard_id'], {"title": "", "weight": 10})
        exec_date = html.escape(str(ev.get('execution_date') or ev['created_at'][:10]))
        safe_ev_title = html.escape(str(ev.get('title', '')))
        safe_std_title = html.escape(str(std.get('title', '')))
        safe_ev_desc = html.escape(str(ev.get('description') or 'تم تنفيذ الشاهد وتوثيقه وفق خطة توزيع المنهج.'))

        files = ev.get('evidence_files', [])
        img_urls = []
        pdf_count = 0
        ext_links = []
        for f in files:
            f_url = f.get('file_url', '')
            f_type = f.get('file_type', '')
            if f_type == 'external/link' or f_url.startswith('http'):
                ext_links.append(html.escape(f_url))
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
                            <span class="top-ev-title">{safe_ev_title}</span>
                            <span class="top-std-sub">البند {ev['standard_id']}: {safe_std_title} ({std['weight']}%)</span>
                        </div>
                        <div class="meta-grid">
                            <div class="meta-box"><div class="meta-title">تاريخ التنفيذ</div><div class="meta-value">{exec_date}</div></div>
                            <div class="meta-box"><div class="meta-title">نوع الشاهد</div><div class="meta-value">شاهد ميداني موثق</div></div>
                        </div>
                        <div class="desc-header">الوصف</div>
                        <div class="desc-section" dir="rtl">{safe_ev_desc}</div>
                        {pdf_notice}
                        {link_notice}
                        {images_section}
                    </div>
                    <div class="signatures">
                        <div class="sig-box">
                            <div style="color:#666; font-size:11.5px; margin-bottom:10px;">المعلم:</div>
                            <div style="font-weight:bold;">{safe_t_name}</div>
                        </div>
                        <div class="sig-box">
                            <div style="color:#666; font-size:11.5px; margin-bottom:10px;">مدير المدرسة:</div>
                            <div style="font-weight:bold;">{safe_prin}</div>
                        </div>
                    </div>
                    <div class="print-footer">منصة زياد الذكية | ملف الإنجاز المهني — أ. {safe_t_name}</div>
                </div>
                """
            else:
                html_content += f"""
                <div class="page">
                    {shared_header}
                    <div class="content-wrapper">
                        <div class="top-ev-banner">
                            <span class="top-ev-title">تابع: {safe_ev_title}</span>
                            <span class="top-std-sub">البند {ev['standard_id']}: {safe_std_title} (صفحة {chunk_idx+1} من {total_chunks})</span>
                        </div>
                        {images_section}
                    </div>
                    <div class="signatures">
                        <div class="sig-box">
                            <div style="color:#666; font-size:11.5px; margin-bottom:10px;">المعلم:</div>
                            <div style="font-weight:bold;">{safe_t_name}</div>
                        </div>
                        <div class="sig-box">
                            <div style="color:#666; font-size:11.5px; margin-bottom:10px;">مدير المدرسة:</div>
                            <div style="font-weight:bold;">{safe_prin}</div>
                        </div>
                    </div>
                    <div class="print-footer">منصة زياد الذكية | ملف الإنجاز المهني — أ. {safe_t_name}</div>
                </div>
                """
    
    html_content += "</body></html>"
    return html_content

def render_footer(is_login=False):
    year_now = datetime.date.today().year
    safe_name = html.escape(str(user_info.get("full_name", "")))
    contact_cards_html = (
        f'<div class="contact-grid-3">'
        f'<a href="mailto:ziyadalamri30@gmail.com" class="contact-pill-card">'
        f'<span class="contact-pill-title">✉️ البريد الإلكتروني</span>'
        f'</a>'
        f'<a href="https://wa.me/966534900049" target="_blank" class="contact-pill-card">'
        f'<span class="contact-pill-title">💬 الواتساب</span>'
        f'</a>'
        f'<a href="https://t.me/ZiyadAlmoamri" target="_blank" class="contact-pill-card">'
        f'<span class="contact-pill-title">✈️ التليجرام</span>'
        f'</a>'
        f'</div>'
        f'<div class="contact-grid-2">'
        f'<a href="https://zi-style.streamlit.app" target="_blank" class="contact-pill-card">'
        f'<span class="contact-pill-title">🧠 منصة أنماط التعلم</span>'
        f'</a>'
        f'<a href="https://zi-edu.streamlit.app" target="_blank" class="contact-pill-card">'
        f'<span class="contact-pill-title">🎓 منصة زياد الذكية</span>'
        f'</a>'
        f'</div>'
    )
    if is_login:
        footer_html = (
            f'<div style="margin-top:26px; text-align:center;" dir="rtl">'
            f'<div class="footer-brand">جميع الحقوق محفوظة لمنصة الأستاذ زياد الذكية © {year_now}</div>'
            f'{contact_cards_html}'
            f'</div>'
        )
    else:
        footer_html = (
            f'<div class="ziyad-footer" dir="rtl">'
            f'<div class="footer-brand">🎓 منصة زياد الذكية | بوابة التعليم الذكية {year_now}</div>'
            f'<div class="footer-rights" style="margin-bottom:10px;">جميع الحقوق محفوظة © {year_now}م - تصميم وتطوير: أ. {safe_name}</div>'
            f'{contact_cards_html}'
            f'</div>'
        )
    st.markdown(footer_html, unsafe_allow_html=True)

# ==========================================
# 9. صفحة تسجيل الدخول
# ==========================================
def login_page():
    login_hero = (
        f'<div class="hero-wrapper" dir="rtl">'
        f'<div class="login-banner-flex">'
        f'{ZIYAD_LOGO_SVG}'
        f'<div class="login-Main-title">منصة زياد الذكية</div>'
        f'<div class="login-portal-pill">ملف الإنجاز المهني الإلكتروني 2026</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(login_hero, unsafe_allow_html=True)

    login_modes = {
        'teacher': "🔒 دخول المعلم",
        'visitor': "👁️ دخول الزائر"
    }
    mode_keys = list(login_modes.keys())
    selected_mode = st.radio(
        "login_mode_bar",
        options=mode_keys,
        format_func=lambda k: login_modes[k],
        index=mode_keys.index(st.session_state.login_mode),
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_mode != st.session_state.login_mode:
        st.session_state.login_mode = selected_mode
        st.rerun()

    if st.session_state.login_mode == 'teacher':
        with st.form("login_form"):
            st.markdown('<div class="login-card-heading">تسجيل دخول المعلم</div>', unsafe_allow_html=True)
            email = st.text_input("البريد الإلكتروني", placeholder="أدخل البريد الإلكتروني هنا...")
            password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور...")
            submit = st.form_submit_button("🚀 تسجيل الدخول للنظام", type="primary", use_container_width=True)
            if submit:
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        st.session_state.user = response.user
                        if response.session:
                            st.session_state.auth_tokens = {
                                "access_token": response.session.access_token,
                                "refresh_token": response.session.refresh_token
                            }
                        st.session_state.is_visitor = False
                        st.success("تم تسجيل الدخول بنجاح!")
                        time.sleep(0.3)
                        st.rerun()
                    except Exception:
                        st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                else:
                    st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")
    else:
        with st.form("visitor_form"):
            st.markdown('<div class="login-card-heading">بوابة الزائر والمشرف التربوي</div>', unsafe_allow_html=True)
            st.caption("بوابة مخصصة لمدير المدرسة والمشرف التربوي للاطلاع على ملف الإنجاز بواسطة رمز المشاهدة الممنوح من المعلم.")
            v_code = st.text_input("رمز المشاهدة للزائر:", type="password", placeholder="أدخل رمز المشاهدة هنا...")
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

    render_footer(is_login=True)

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

    all_file_paths = tuple(sorted(set(
        f['file_url'] for ev in evidences for f in ev.get('evidence_files', []) if f.get('file_url')
    )))
    signed_urls_map = get_signed_urls_batch(all_file_paths)

    greeting, today_str = get_greeting_and_dates()
    safe_name = html.escape(str(user_info.get("full_name", "")))
    safe_school = html.escape(str(user_info.get("school_name", "")))
    safe_spec = html.escape(str(user_info.get("specialization", "")))
    safe_prin = html.escape(str(user_info.get("principal_name", "")))
    safe_year = html.escape(str(active_year.get("year_name", "1448")))

    hero_html = (
        f'<div class="hero-wrapper" dir="rtl">'
        f'<div class="hero-top" dir="rtl">'
        f'<div class="brand-box">{ZIYAD_LOGO_SVG}'
        f'<div><div class="brand-title">منصة زياد الذكية</div>'
        f'<div class="brand-sub">بوابة التعليم الذكية 2026 • ملف الإنجاز المهني</div></div></div>'
        f'<div class="date-pill">🗓️ {today_str}</div>'
        f'</div>'
        f'<div class="hero-body" dir="rtl">'
        f'<div>'
        f'<div class="welcome-line">✨ {greeting}</div>'
        f'<div class="teacher-name">أ. {safe_name}</div>'
        f'<div class="meta-badges">'
        f'<span class="meta-pill">🏫 {safe_school}</span>'
        f'<span class="meta-pill">📚 {safe_spec}</span>'
        f'<span class="meta-pill">👔 مدير المدرسة: {safe_prin}</span>'
        f'</div>'
        f'</div>'
        f'<div class="year-badge">📁 ملف إنجاز عام {safe_year}هـ</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    if is_visitor:
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            st.markdown('<div class="visitor-banner" dir="rtl">👁️ تتصفح الملف بوضع الزائر (مشاهدة فقط)</div>', unsafe_allow_html=True)
        with col_v2:
            if st.button("🚪 خروج", use_container_width=True):
                st.session_state.is_visitor = False
                st.query_params.clear()
                st.rerun()

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
            f'<div class="kpi-grid" dir="rtl">'
            f'<div class="kpi-card"><div class="kpi-val">{total_ev_count}</div><div class="kpi-lbl">إجمالي الشواهد</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_with_ev}/{total_stds}</div><div class="kpi-lbl">البنود المغطاة</div></div>'
            f'<div class="kpi-card"><div class="kpi-val">{stds_reached_target}</div><div class="kpi-lbl">حققت المستهدف</div></div>'
            f'<div class="kpi-card"><div class="kpi-val" style="color:#dc2626 !important;">{empty_stds}</div><div class="kpi-lbl">بنود فارغة</div></div>'
            f'</div>'
            f'<div class="progress-card" dir="rtl">'
            f'<div style="display:flex; justify-content:space-between; font-weight:800; font-size:13.5px; color:#1e293b;">'
            f'<span style="color:#1e293b !important;">نسبة تغطية معايير الأداء الوظيفي ({safe_year}هـ)</span>'
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
                status_txt = '<span style="color:#dc2626 !important; font-size:11.5px; font-weight:700;">لا شواهد بعد</span>'
                num_cls = "std-num std-num-empty"
            elif count >= target:
                status_txt = f'<span style="color:{th["primary"]} !important; font-size:11.5px; font-weight:800;">مكتمل ({count} شواهد)</span>'
                num_cls = "std-num"
            else:
                status_txt = f'<span style="color:{th["accent"]} !important; font-size:11.5px; font-weight:700;">{count} شاهد • بقي {target - count}</span>'
                num_cls = "std-num"

            safe_std_t = html.escape(str(std["title"]))
            card_html = (
                f'<div class="std-card" dir="rtl">'
                f'<div style="display:flex; align-items:center;">'
                f'<div class="{num_cls}">{s_id}</div>'
                f'<div><div class="std-title">{s_id}. {safe_std_t}</div>'
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
    # 📋 2. صفحة البنود والشواهد
    # ----------------------------------------
    elif st.session_state.current_page == 'standard_view':
        st.markdown('<div class="section-heading">📋 استعراض وإدارة بنود الأداء والشواهد</div>', unsafe_allow_html=True)
        
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
                s_evs = sort_evidences_chronologically([e for e in evidences if e['standard_id'] == s['id']])
                with st.expander(f"{'✅' if len(s_evs)>0 else '⚪'} البند {s['id']}: {s['title']} — ({len(s_evs)} شواهد)", expanded=(len(s_evs) > 0)):
                    if not s_evs:
                        st.caption("لا توجد شواهد مرفوعة في هذا البند حتى الآن.")
                    else:
                        for order_idx, ev in enumerate(s_evs, 1):
                            files = ev.get("evidence_files", [])
                            exec_date = html.escape(str(ev.get('execution_date') or ev['created_at'][:10]))
                            safe_ev_t = html.escape(str(ev.get("title", "")))
                            safe_ev_d = html.escape(str(ev.get("description") or ""))
                            thumbs_html = render_attachments_html(files, signed_urls_map)
                            ev_card = (
                                f'<div class="ev-box" dir="rtl">'
                                f'<div class="ev-header-row" dir="rtl">'
                                f'<span class="ev-title-right" dir="rtl">📄 {order_idx} - {safe_ev_t}</span>'
                                f'<span style="font-size:12px; color:#64748b !important;" dir="rtl">📅 {exec_date}</span>'
                                f'</div>'
                                f'<div class="ev-desc-rtl" dir="rtl">{safe_ev_d}</div>'
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
            std_evidences = sort_evidences_chronologically([e for e in evidences if e['standard_id'] == std_id])

            st.markdown(f'<div class="sub-heading">📂 الشواهد المرفوعة في البند {std_id}: {std_data["title"]} ({len(std_evidences)})</div>', unsafe_allow_html=True)
            if not std_evidences:
                st.info("لا توجد شواهد مرفوعة في هذا البند حتى الآن. يمكنك إضافة شاهد جديد من النموذج بالأسفل.")
            else:
                for order_idx, ev in enumerate(std_evidences, 1):
                    files = ev.get("evidence_files", [])
                    exec_date = html.escape(str(ev.get('execution_date') or ev['created_at'][:10]))
                    safe_ev_t = html.escape(str(ev.get("title", "")))
                    safe_ev_d = html.escape(str(ev.get("description") or ""))
                    thumbs_html = render_attachments_html(files, signed_urls_map)

                    ev_detail_html = (
                        f'<div class="ev-box" dir="rtl">'
                        f'<div class="ev-header-row" dir="rtl">'
                        f'<span class="ev-title-right" dir="rtl">📄 {order_idx} - {safe_ev_t}</span>'
                        f'<span style="background:{th["tint"]}; color:{th["primary_dark"]} !important; padding:4px 12px; border-radius:10px; font-size:12px; font-weight:800;" dir="rtl">'
                        f'📅 تاريخ التنفيذ: {exec_date}</span></div>'
                        f'<div class="ev-desc-rtl" dir="rtl">{safe_ev_d}</div>'
                        f'{thumbs_html}</div>'
                    )
                    st.markdown(ev_detail_html, unsafe_allow_html=True)

                    if not is_visitor:
                        render_evidence_edit_and_delete(ev, signed_urls_map, stds, key_prefix="single_")

            db_subs = [item['title'] for item in all_subs if item.get('standard_id') == std_id]
            sub_options = db_subs if db_subs else DEFAULT_SUB_ITEMS.get(std_id, [])

            with st.expander("💡 استعراض أمثلة الشواهد المستهدفة لهذا البند", expanded=False):
                for idea in sub_options:
                    safe_idea = html.escape(str(idea))
                    st.markdown(f'<div class="idea-card" dir="rtl"><span>💡 {safe_idea}</span><span style="color:{th["primary"]} !important; font-weight:bold;">✔</span></div>', unsafe_allow_html=True)

            if not is_visitor:
                st.markdown('<div class="sub-heading">➕ إضافة شاهد جديد لهذا البند</div>', unsafe_allow_html=True)
                
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

                        with st.spinner("جاري ضغط الصور وحفظ الشاهد والمرفقات..."):
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
                                    opt_bytes, opt_mime, opt_ext = optimize_uploaded_image(up_file)
                                    path = f"{new_id}/{uuid.uuid4()}.{opt_ext}"
                                    supabase.storage.from_("private-achievements").upload(
                                        path=path, file=opt_bytes, file_options={"content-type": opt_mime}
                                    )
                                    supabase.table("evidence_files").insert({
                                        "evidence_id": new_id, "file_url": path, "file_type": opt_mime
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
    # 📄 3. صفحة التقارير والطباعة
    # ----------------------------------------
    elif st.session_state.current_page == 'reports':
        st.markdown('<div class="section-heading">📄 تصدير وطباعة ملف الإنجاز</div>', unsafe_allow_html=True)
        st.info(f"📊 الملف جاهز للتصدير ويحتوي على ({total_ev_count}) شاهد موزعة على ({stds_with_ev}) من أصل ({total_stds}) معايير. اختر التصميم ثم اضغط على الزر المطلوب:")
        
        report_style = st.selectbox(
            "🎨 اختر تصميم التقرير قبل التصدير:",
            [
                "1. التصميم الرسمي الوزاري (إطار كلاسيكي وجداول رسمية)",
                "2. التصميم العصري الحديث (بطاقات ناعمة وألوان المظهر الحالي)",
                "3. التصميم التنفيذي المختصر (تخطيط مكثف بحدود هندسية أنيقة)"
            ]
        )

        if st.button("🖨️ تجهيز وطباعة ملف الإنجاز PDF", type="primary", use_container_width=True):
            with st.spinner("جاري تجهيز صفحات تقرير PDF..."):
                html_content = build_pdf_report_html(
                    user_info, active_year, stds, evidences, ev_by_std, signed_urls_map, report_style, th
                )
                st.session_state.ready_pdf_b64 = base64.b64encode(html_content.encode("utf-8")).decode("ascii")
                st.session_state.auto_open_pdf = True

        if st.session_state.ready_pdf_b64:
            auto_js_call = "openPrintWindow();" if st.session_state.auto_open_pdf else ""
            st.session_state.auto_open_pdf = False
            st.success("✅ تم تجهيز تقرير PDF! إذا لم تفتح نافذة الطباعة تلقائياً، اضغط على الزر الأخضر بالأسفل:")
            components.html(f"""
                <div style="text-align: center; margin: 4px 0;">
                    <button onclick="openPrintWindow()" style="width: 100%; height: 50px; background-color: #146c59; color: white; border: none; border-radius: 14px; font-size: 15.5px; font-weight: 800; cursor: pointer; font-family: 'Cairo', sans-serif; box-shadow: 0 4px 10px rgba(20,108,89,0.2);">
                        🖨️ فتح نافذة الطباعة وحفظ PDF الآن
                    </button>
                </div>
                <script>
                    var b64Report = "{st.session_state.ready_pdf_b64}";
                    function decodeUtf8Base64(b64) {{
                        var binStr = atob(b64);
                        var bytes = new Uint8Array(binStr.length);
                        for (var i = 0; i < binStr.length; i++) {{
                            bytes[i] = binStr.charCodeAt(i);
                        }}
                        return new TextDecoder('utf-8').decode(bytes);
                    }}
                    function openPrintWindow() {{
                        var win = window.open('', '_blank');
                        if (!win) return;
                        win.document.write(decodeUtf8Base64(b64Report));
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
                    {auto_js_call}
                </script>
            """, height=62)

        if not is_visitor:
            st.write("")
            if st.button("📄 تجهيز ملف Word قابل للتعديل (شامل الصور والمرفقات)", use_container_width=True):
                with st.spinner("جاري تجهيز ملف الـ Word وتضمين صور الشواهد بداخله..."):
                    all_evidences = sort_evidences_chronologically(evidences)
                    st.session_state.ready_docx_bytes = generate_editable_docx(
                        user_info, active_year, stds, all_evidences, signed_urls_map
                    )

            if st.session_state.ready_docx_bytes:
                st.download_button(
                    label="⬇️ اضغط هنا لتحميل ملف الـ Word الجاهز (.docx)",
                    data=st.session_state.ready_docx_bytes,
                    file_name=f"ملف_إنجاز_{user_info['full_name'].replace(' ', '_')}_{active_year['year_name']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )

    # ----------------------------------------
    # ⚙️ 4. صفحة حسابي
    # ----------------------------------------
    elif st.session_state.current_page == 'settings' and not is_visitor:
        st.markdown('<div class="section-heading">⚙️ إعدادات الحساب والمظهر والأرشيف والنسخ الاحتياطي</div>', unsafe_allow_html=True)

        storage_stats = fetch_storage_usage_stats()
        render_storage_meter_card(storage_stats)

        t1, t2, t3, t4 = st.tabs(["👤 البيانات والمظهر", "📅 الأرشيف والنسخ", "🔗 مشاركة للزوار", "🚪 الخروج"])
        
        with t1:
            with st.form("profile_form"):
                st.markdown('<div class="sub-heading">🎨 مظهر التطبيق</div>', unsafe_allow_html=True)
                theme_keys = list(THEMES.keys())
                theme_labels = [THEMES[k]["name"] for k in theme_keys]
                current_idx = theme_keys.index(active_theme_key) if active_theme_key in theme_keys else 0
                selected_theme_label = st.selectbox("اختر المظهر اللوني للتطبيق:", theme_labels, index=current_idx)
                chosen_theme_key = theme_keys[theme_labels.index(selected_theme_label)]

                st.markdown('<div class="sub-heading">📝 البيانات الأساسية</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    n_name = st.text_input("اسم المعلم:", value=user_info['full_name'])
                    n_spec = st.text_input("التخصص:", value=user_info['specialization'])
                    n_city = st.text_input("المدينة:", value=user_info['city'])
                with c2:
                    n_school = st.text_input("اسم المدرسة:", value=user_info['school_name'])
                    n_stage = st.text_input("المرحلة الدراسية:", value=user_info['education_stage'])
                    n_prin = st.text_input("اسم مدير المدرسة:", value=user_info['principal_name'])

                st.markdown('<div class="sub-heading">✨ إعداد الذكاء الاصطناعي (اختياري)</div>', unsafe_allow_html=True)
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
                st.markdown('<div class="sub-heading">📅 أرشفة ملفات الإنجاز وإدارة الأعوام الدراسية</div>', unsafe_allow_html=True)
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

                st.markdown('<div class="sub-heading">🗂️ سجل ملفات الإنجاز المحفوظة</div>', unsafe_allow_html=True)
                for y in all_years:
                    y_ev_res = supabase.table("evidences").select("id", count="exact").eq("year_id", y['id']).execute()
                    y_count = y_ev_res.count if y_ev_res.count is not None else len(y_ev_res.data)
                    is_act = y.get("is_active", False)
                    
                    badge_html = '<span style="background:#10b981; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">🟢 الملف النشط</span>' if is_act else '<span style="background:#64748b; color:white !important; padding:4px 12px; border-radius:8px; font-size:12px;">📦 مؤرشف</span>'
                    safe_yn = html.escape(str(y["year_name"]))
                    arch_card = (
                        f'<div class="std-card" dir="rtl">'
                        f'<div><div class="std-title">📁 ملف إنجاز العام الدراسي: {safe_yn}هـ</div>'
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
                st.markdown('<div class="sub-heading">📤 النسخ الاحتياطي للأصول والبيانات (للحفظ الخارجي والاستعادة)</div>', unsafe_allow_html=True)
                st.caption("لحفظ نسخة أمان كاملة على جهازك أو قرصك الخارجي (بينما طباعة PDF وتصدير Word متاحان في تبويب 📄 التقرير):")

                if st.button("🗂️ تجهيز حقيبة المرفقات والصور الأصلية مرتبة بالمجلدات (.zip)", use_container_width=True):
                    with st.spinner("جاري جمع الصور وملفات الـ PDF وترتيبها في مجلدات المعايير..."):
                        st.session_state.ready_zip_bytes = generate_attachments_zip(
                            user_info, active_year, all_years, stds, all_subs, evidences, signed_urls_map
                        )
                if st.session_state.ready_zip_bytes:
                    st.download_button(
                        label="⬇️ تحميل حقيبة المرفقات والصور الجاهزة (.zip)",
                        data=st.session_state.ready_zip_bytes,
                        file_name=f"حقيبة_شواهد_{user_info['full_name'].replace(' ', '_')}_{active_year['year_name']}.zip",
                        mime="application/zip",
                        type="primary",
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
                st.markdown('<div class="sub-heading">📥 استعادة نسخة احتياطية سابقة (Restore)</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="sub-heading">🔗 التحكم في وصول الزوار (قراءة ومشاهدة فقط)</div>', unsafe_allow_html=True)
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
            st.info(f"💡 **رابط المشاركة السريعة للزائر:** أضف `?visitor={curr_code}` لنهاية رابط موقعك، أو أعطِ الرمز `{curr_code}` للزائر ليدخله في تبويب (دخول الزائر).")

        with t4:
            if st.button("🚪 تسجيل الخروج من الحساب", type="primary", use_container_width=True):
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
                clear_app_cache()
                st.session_state.user = None
                st.session_state.auth_tokens = None
                st.session_state.is_visitor = False
                st.rerun()

    render_footer(is_login=False)

# ==========================================
# 11. نقطة تشغيل التطبيق (محمية ضد أي خطأ غير متوقع)
# ==========================================
if st.session_state.user is None and not st.session_state.is_visitor:
    login_page()
else:
    try:
        main_app()
    except Exception as err:
        if "JWT" in str(err) or "401" in str(err) or "expired" in str(err).lower():
            st.session_state.user = None
            st.session_state.auth_tokens = None
            st.warning("انتهت صلاحية جلسة الأمان، يرجى تسجيل الدخول مرة أخرى.")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"حدث خطأ غير متوقع: {err}")
