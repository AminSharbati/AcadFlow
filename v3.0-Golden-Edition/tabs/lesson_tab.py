# tabs/lesson_tab.py
from tabs.base_tab import BaseTab
from models import Lesson
from config import MAJORS

class LessonTab(BaseTab):
    def __init__(self, parent, user, main_window):
        super().__init__(parent, user, main_window, "📚 دروس", Lesson, permission='manage')
        fields = [("نام درس", "name"), ("تعداد واحد", "unit", "int"), ("رشته تحصیلی", "major", "combo", MAJORS),
                  ("ظرفیت", "max_capacity", "int_optional"), ("توضیحات", "description", "optional")]
        self.setup_ui(fields); self.refresh_data()