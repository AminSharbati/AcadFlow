# tabs/presentation_tab.py
from tabs.base_tab import BaseTab
from models import Presentation, Master, Lesson
from config import WEEK_DAYS

class PresentationTab(BaseTab):
    def __init__(self, parent, user, main_window):
        super().__init__(parent, user, main_window, "📅 ارائه دروس", Presentation, permission='manage')
        fields = [("استاد", "master_id", "combo_fk", Master, "name"), ("درس", "lesson_id", "combo_fk", Lesson, "name"),
                  ("روز برگزاری", "day_hold", "combo", WEEK_DAYS), ("ساعت شروع", "start_time", "int_optional"),
                  ("ساعت پایان", "finish_time", "int_optional"), ("ظرفیت", "capacity", "int_optional")]
        self.setup_ui(fields); self.refresh_data()
    
    def _format_value(self, record, attr, value):
        if attr == 'master_id': return record.master.name if record.master else 'نامشخص'
        if attr == 'lesson_id': return record.lesson.name if record.lesson else 'نامشخص'
        return value