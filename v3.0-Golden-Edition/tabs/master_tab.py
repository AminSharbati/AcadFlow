# tabs/master_tab.py
from tabs.base_tab import BaseTab
from models import Master

class MasterTab(BaseTab):
    def __init__(self, parent, user, main_window):
        super().__init__(parent, user, main_window, "👨‍🏫 اساتید", Master, permission='manage')
        fields = [("نام استاد", "name"), ("کد ملی", "national_code"), ("مدرک تحصیلی", "degree"),
                  ("گروه", "department"), ("موبایل", "mobile"), ("ایمیل", "email", "optional")]
        self.setup_ui(fields); self.refresh_data()
    
    def add_record(self):
        from auth import AuthManager; from database import get_session; from tkinter import messagebox
        if not self._has_permission('manage'): messagebox.showwarning("عدم دسترسی", "شما اجازه افزودن ندارید"); return
        try:
            data = self._get_form_data()
            if data.get('email') and data.get('national_code'):
                AuthManager.create_user_from_person(data['name'], data['email'], data['national_code'], 'professor')
            session = get_session()
            try: record = self.model(**data); session.add(record); session.commit(); self._clear_form(); self.refresh_data(); messagebox.showinfo("موفق", "استاد افزوده شد")
            except: session.rollback(); raise
            finally: session.close()
        except Exception as e: messagebox.showerror("خطا", str(e))