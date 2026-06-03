# config.py
APP_NAME = "AcadFlow"
VERSION = "3.0.0"
COMPANY = "داتین آریا"
DB_FILE = "acadflow.db"

MAJORS = ["کامپیوتر", "برق", "عمران", "مکانیک", "معماری", "سایر"]
WEEK_DAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه"]

ROLES = {"admin": "ادمین کل", "manager": "مدیر آموزش", "professor": "استاد", "student": "دانشجو"}

SECURITY_QUESTION = "کد ملی شما چیست؟"

MIN_SCORE = 0
MAX_SCORE = 20
MAX_LOGIN_ATTEMPTS = 5

WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 800