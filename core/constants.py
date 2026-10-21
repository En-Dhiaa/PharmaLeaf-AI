"""
PharmaLeaf AI - Application Constants and Configuration Values
"""
import os
import sys

APP_NAME = "PharmaLeaf AI"
APP_TITLE = "PharmaLeaf AI — نظام استخراج وتحليل النشرات الدوائية"
APP_VERSION = "1.0.0"
APP_AUTHOR = "En-Dhiaa"

SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]
SUPPORTED_DOCUMENT_EXTENSIONS = [".pdf"]
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_DOCUMENT_EXTENSIONS

# Standard AppData directories for user preferences & tessdata
USER_APPDATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "PharmaLeaf")
DEFAULT_TESSDATA_DIR = os.path.join(USER_APPDATA_DIR, "tessdata")
PROJECTS_DIR = os.path.join(USER_APPDATA_DIR, "projects")
DATABASE_PATH = os.path.join(USER_APPDATA_DIR, "pharmaleaf.db")

# Fallback system Tesseract path on Windows
SYSTEM_TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Recognized pharmaceutical leaflet headings (Arabic & English)
PHARMA_SECTIONS = [
    {
        "id": "brand_name",
        "ar": "الاسم التجاري والدواء",
        "en": "Trade / Brand Name",
        "keywords_ar": ["الاسم التجاري", "اسم المستحضر", "الدواء", "الاسم العلمي"],
        "keywords_en": ["trade name", "brand name", "product name", "proprietary name"]
    },
    {
        "id": "composition",
        "ar": "التركيب والمواد الفعالة",
        "en": "Composition / Active Ingredients",
        "keywords_ar": ["التركيب", "المواد الفعالة", "المادة الفعالة", "المكونات", "يحتوي كل قرص", "يحتوي كل مل"],
        "keywords_en": ["composition", "active ingredient", "active substances", "contains", "each tablet contains"]
    },
    {
        "id": "indications",
        "ar": "دواعي الاستعمال",
        "en": "Indications / Therapeutic Uses",
        "keywords_ar": ["دواعي الاستعمال", "دواعي الاستخدام", "يستخدم لعلاج", "الاستطبابات", "الحالات التي يستخدم فيها"],
        "keywords_en": ["indications", "therapeutic indications", "uses", "intended use", "what is this medicine used for"]
    },
    {
        "id": "dosage",
        "ar": "الجرعة وطريقة الاستعمال",
        "en": "Dosage & Administration",
        "keywords_ar": ["الجرعة وطريقة الاستعمال", "طريقة الاستخدام", "كيفية تناول الدواء", "الجرعة المعتادة", "الجرعة اليومية", "ارشادات الاستعمال"],
        "keywords_en": ["dosage and administration", "posology", "how to take", "method of administration", "recommended dose"]
    },
    {
        "id": "contraindications",
        "ar": "موانع الاستعمال",
        "en": "Contraindications",
        "keywords_ar": ["موانع الاستعمال", "لا تستخدم هذا الدواء", "لا تتناول", "يحظر استخدام"],
        "keywords_en": ["contraindications", "do not take", "when not to use", "contra-indications"]
    },
    {
        "id": "warnings",
        "ar": "تحذيرات واحتياطات خاصة",
        "en": "Warnings & Precautions",
        "keywords_ar": ["تحذيرات واحتياطات", "تحذيرات هامة", "احتياطات خاصة", "تنبيهات", "انتبه قبل الاستخدام"],
        "keywords_en": ["warnings and precautions", "special warnings", "precautions for use", "take special care"]
    },
    {
        "id": "side_effects",
        "ar": "الآثار الجانبية وغير المرغوبة",
        "en": "Adverse Reactions / Side Effects",
        "keywords_ar": ["الآثار الجانبية", "الأعراض الجانبية", "التأثيرات غير المرغوبة", "ردود الفعل التحسسية"],
        "keywords_en": ["undesirable effects", "adverse reactions", "side effects", "possible side effects"]
    },
    {
        "id": "interactions",
        "ar": "التفاعلات والتداخلات الدوائية",
        "en": "Drug Interactions",
        "keywords_ar": ["التفاعلات الدوائية", "التداخلات مع أدوية أخرى", "تناول أدوية أخرى"],
        "keywords_en": ["interactions", "drug interactions", "other medicines and", "taking other medicines"]
    },
    {
        "id": "pregnancy",
        "ar": "الحمل والرضاعة",
        "en": "Pregnancy & Lactation",
        "keywords_ar": ["الحمل والرضاعة", "الحمل", "الرضاعة الطبيعية", "الخصوبة"],
        "keywords_en": ["pregnancy and lactation", "pregnancy and breast-feeding", "fertility"]
    },
    {
        "id": "overdose",
        "ar": "الجرعة الزائدة",
        "en": "Overdose",
        "keywords_ar": ["الجرعة الزائدة", "في حال تناول جرعة مفرطة", "التسمم"],
        "keywords_en": ["overdose", "if you take more than you should"]
    },
    {
        "id": "storage",
        "ar": "الحفظ والتخزين ومدة الصلاحية",
        "en": "Storage & Shelf Life",
        "keywords_ar": ["الحفظ والتخزين", "شروط التخزين", "يحفظ بعيداً عن متناول الأطفال", "يحفظ في درجة حرارة", "تاريخ الصلاحية"],
        "keywords_en": ["storage", "how to store", "keep out of the reach of children", "shelf life", "storage conditions"]
    },
    {
        "id": "manufacturer",
        "ar": "الشركة المصنعة والمالك",
        "en": "Manufacturer / Marketing Authorization Holder",
        "keywords_ar": ["الشركة المصنعة", "صُنع بواسطة", "إنتاج شركة", "الوكيل"],
        "keywords_en": ["manufacturer", "manufactured by", "marketing authorization holder", "produced by"]
    }
]

# Regex pattern for dosage, strengths, and measurements in leaflets
DOSAGE_PATTERN = r"(?i)\b\d+(?:[\.,]\d+)?\s*(?:mg|mcg|µg|g|kg|ml|l|iu|ui|mmol|mEq|%|ملغ|ملجم|جرام|غرام|كغ|مل|لتر|ميكروغرام|وحدة دولية)\b"

# Confidence threshold below which OCR tokens are flagged for manual review
LOW_CONFIDENCE_THRESHOLD = 65.0
