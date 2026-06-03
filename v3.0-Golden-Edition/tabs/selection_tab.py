# tabs/selection_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from tabs.base_tab import BaseTab
from models import Selection, Student, Presentation, Lesson
from database import get_session
from config import MAJORS
from auth import AuthManager

class SelectionTab(BaseTab):
    def __init__(self, parent, user, main_window):
        super().__init__(parent, user, main_window, "📝 انتخاب واحد", Selection, permission='grade')
        fields = [
            ("فیلتر رشته", "major_filter", "combo_major", MAJORS),
            ("دانشجو", "student_id", "combo_fk_filtered", Student, "name"),
            ("درس ارائه شده", "presentation_id", "combo_fk_filtered", Presentation, "name"),
            ("سال تحصیلی", "year_education", "int_optional"),
            ("نمره", "score", "optional"),
        ]
        self.setup_ui(fields)
        self.refresh_data()
    
    def _format_value(self, record, attr, value):
        if attr == 'student_id':
            return record.student.name if record.student else 'نامشخص'
        if attr == 'presentation_id':
            return record.presentation.get_summary() if record.presentation else 'نامشخص'
        if attr == 'status':
            return record.get_status_text()
        if attr == 'score' and value is not None:
            return f"{value:.1f}"
        return value
    
    def _on_major_filter(self, event=None):
        major = self.entries.get('major_filter')
        if not major:
            return
        selected_major = major.get()
        
        # فیلتر دانشجوها
        student_combo = self.entries.get('student_id')
        if student_combo:
            student_combo.set('')
            session = get_session()
            try:
                if selected_major:
                    students = session.query(Student).filter(Student.major == selected_major).all()
                else:
                    students = session.query(Student).all()
                student_combo['values'] = sorted([s.name for s in students])
            finally:
                session.close()
        
        # فیلتر درس‌های ارائه شده
        pres_combo = self.entries.get('presentation_id')
        if pres_combo:
            pres_combo.set('')
            session = get_session()
            try:
                if selected_major:
                    presentations = session.query(Presentation).join(Lesson).filter(
                        Lesson.major == selected_major
                    ).all()
                else:
                    presentations = session.query(Presentation).all()
                pres_combo['values'] = sorted([p.get_display_name() for p in presentations])
            finally:
                session.close()
    
    def load_foreign_keys(self):
        """بارگذاری combo_fk ها - فقط برای حالت بدون فیلتر"""
        # این تب combo_fk_filtered داره که با فیلتر پر میشن
        # combo_fk معمولی نداره
        pass
    
    def refresh_data(self):
        self.load_data()
        # پاک کردن فیلترها
        for key in ['major_filter', 'student_id', 'presentation_id']:
            widget = self.entries.get(key)
            if widget and isinstance(widget, ttk.Combobox):
                widget.set('')
                if key != 'major_filter':
                    widget['values'] = []
    
    def add_record(self):
        if not self._has_permission('grade'):
            messagebox.showwarning("عدم دسترسی", "شما اجازه ثبت ندارید")
            return
        super().add_record()
    
    def update_record(self):
        if self.user['role'] == 'student':
            messagebox.showwarning("عدم دسترسی", "دانشجو نمی‌تواند ویرایش کند")
            return
        super().update_record()