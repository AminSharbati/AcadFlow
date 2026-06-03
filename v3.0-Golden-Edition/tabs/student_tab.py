# tabs/student_tab.py
from tabs.base_tab import BaseTab
from models import Student
from config import MAJORS

class StudentTab(BaseTab):
    def __init__(self, parent, user, main_window):
        super().__init__(parent, user, main_window, "👨‍🎓 دانشجویان", Student, permission='manage')
        fields = [("نام دانشجو", "name"), ("کد دانشجویی", "student_code"), ("کد ملی", "national_code"),
                  ("ترم ورود", "entrance_term", "optional"), ("مقطع", "graduation"), ("موبایل", "mobile"),
                  ("ایمیل", "email", "optional"), ("رشته تحصیلی", "major", "combo", MAJORS)]
        self.setup_ui(fields); self.refresh_data()
    
    def add_record(self):
        from auth import AuthManager; from database import get_session; from tkinter import messagebox
        if not self._has_permission('manage'): messagebox.showwarning("عدم دسترسی", "شما اجازه افزودن ندارید"); return
        try:
            data = self._get_form_data()
            if data.get('mobile') and data.get('national_code'):
                AuthManager.create_user_from_person(data['name'], data['email'], data['national_code'], 'student')
            session = get_session()
            try: record = self.model(**data); session.add(record); session.commit(); self._clear_form(); self.refresh_data(); messagebox.showinfo("موفق", "دانشجو افزوده شد")
            except: session.rollback(); raise
            finally: session.close()
        except Exception as e: messagebox.showerror("خطا", str(e))