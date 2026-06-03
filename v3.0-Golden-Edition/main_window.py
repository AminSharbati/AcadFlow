# main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from auth import AuthManager
from config import APP_NAME, VERSION, COMPANY, WINDOW_WIDTH, WINDOW_HEIGHT
from database import get_session

class MainWindow:
    def __init__(self, user_data):
        self.user = user_data
        
        self.window = tk.Tk()
        self.window.title(f"{APP_NAME} | {self.user['full_name']} | {AuthManager.get_user_role_name(self.user['role'])}")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.minsize(1050, 680)
        self.window.configure(bg='#e8ecf1')
        
        try:
            self.font_small = ('B Nazanin', 10); self.font_normal = ('B Nazanin', 11)
            self.font_bold = ('B Nazanin', 11, 'bold'); self.font_title = ('B Nazanin', 14, 'bold')
            self.font_header = ('B Nazanin', 18, 'bold')
        except:
            self.font_small = ('Tahoma', 9); self.font_normal = ('Tahoma', 10)
            self.font_bold = ('Tahoma', 10, 'bold'); self.font_title = ('Tahoma', 13, 'bold')
            self.font_header = ('Tahoma', 16, 'bold')
        
        self._setup_styles()
        self._create_menu()
        self._create_header()
        self._create_notebook()
        self._create_statusbar()
        self.window.protocol("WM_DELETE_WINDOW", self._exit)
    
    def _setup_styles(self):
        style = ttk.Style(); style.theme_use('clam')
        style.configure('.', font=self.font_normal)
        style.configure('TLabel', font=self.font_normal, padding=2)
        style.configure('TButton', font=self.font_bold, padding=8)
        style.configure('TEntry', font=self.font_normal, padding=4)
        style.configure('TCombobox', font=self.font_normal, padding=4)
        style.configure('Treeview', font=self.font_normal, rowheight=28)
        style.configure('Treeview.Heading', font=self.font_bold, padding=6)
        style.configure('TLabelframe.Label', font=self.font_title)
        style.configure('TNotebook.Tab', font=self.font_bold, padding=[15, 6])
    
    def _create_menu(self):
        menubar = Menu(self.window, font=self.font_normal); self.window.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0, font=self.font_normal)
        menubar.add_cascade(label="📁 فایل", menu=file_menu)
        file_menu.add_command(label="🔄 بروزرسانی همه", command=self._refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 خروج", command=self._exit)
        
        if self.user['role'] in ['admin', 'manager']:
            tools_menu = Menu(menubar, tearoff=0, font=self.font_normal)
            menubar.add_cascade(label="🔧 ابزارها", menu=tools_menu)
            tools_menu.add_command(label="👥 مدیریت کاربران", command=self._show_user_management)
            tools_menu.add_command(label="📋 تاریخچه فعالیت‌ها", command=self._show_logs)
        
        help_menu = Menu(menubar, tearoff=0, font=self.font_normal)
        menubar.add_cascade(label="❓ راهنما", menu=help_menu)
        help_menu.add_command(label="📖 راهنمای استفاده", command=self._show_help)
        help_menu.add_command(label="ℹ️ درباره", command=self._show_about)
    
    def _create_header(self):
        header = tk.Frame(self.window, bg='#1a1a2e', height=55)
        header.pack(fill='x'); header.pack_propagate(False)
        tk.Label(header, text=f"  {APP_NAME}", font=self.font_header, fg='#e94560', bg='#1a1a2e').pack(side='left', padx=15)
        tk.Label(header, text=f"نسخه {VERSION} | {self.user['full_name']} | {AuthManager.get_user_role_name(self.user['role'])}  ",
                font=self.font_small, fg='#8b949e', bg='#1a1a2e').pack(side='right', padx=15)
    
    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.window, padding=(5, 5, 5, 0))
        self.notebook.pack(fill='both', expand=True, padx=8, pady=(0, 5))
        
        from tabs.dashboard_tab import DashboardTab
        from tabs.student_tab import StudentTab
        from tabs.master_tab import MasterTab
        from tabs.lesson_tab import LessonTab
        from tabs.presentation_tab import PresentationTab
        from tabs.selection_tab import SelectionTab
        from tabs.report_tab import ReportTab
        
        self.tabs = []
        role = self.user['role']
        
        if role in ['admin', 'manager']:
            self.tabs.append(DashboardTab(self.notebook, self.user, self))
            self.tabs.append(StudentTab(self.notebook, self.user, self))
            self.tabs.append(MasterTab(self.notebook, self.user, self))
            self.tabs.append(LessonTab(self.notebook, self.user, self))
            self.tabs.append(PresentationTab(self.notebook, self.user, self))
        
        self.tabs.append(SelectionTab(self.notebook, self.user, self))
        self.tabs.append(ReportTab(self.notebook, self.user, self))
    
    def _create_statusbar(self):
        bar = tk.Frame(self.window, bg='#1a1a2e', height=28)
        bar.pack(side='bottom', fill='x'); bar.pack_propagate(False)
        self.status_label = tk.Label(bar, text="  ✓ آماده", fg='#8b949e', bg='#1a1a2e', font=self.font_small, anchor='w')
        self.status_label.pack(side='left', fill='both', expand=True)
        tk.Label(bar, text=f"ارائه شده توسط {COMPANY}  ", fg='#e94560', bg='#1a1a2e', font=self.font_small).pack(side='right', padx=10)
    
    def _update_status(self, msg): self.status_label.config(text=f"  ✓ {msg}")
    
    def _show_user_management(self):
        win = tk.Toplevel(self.window)
        win.title("مدیریت کاربران")
        win.geometry("950x850")
        win.configure(bg='#e8ecf1')
        
        selected_user_id = tk.IntVar(value=0)
        
        form = ttk.LabelFrame(win, text="افزودن / ویرایش کاربر", padding="10")
        form.pack(fill='x', padx=10, pady=10)
        
        entries = {}
        labels = [
            ("نام کاربری", "username", 0, 0), ("نام کامل", "full_name", 0, 2), ("نقش", "role", 0, 4),
            ("رمز عبور", "password", 1, 0), ("ایمیل", "email", 1, 2), ("سوال امنیتی", "question", 1, 4),
        ]
        
        for label, key, row, col in labels:
            ttk.Label(form, text=f"{label}:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
            if key == "role":
                widget = ttk.Combobox(form, values=['admin', 'manager', 'professor', 'student'], width=18, state='readonly')
            else:
                widget = ttk.Entry(form, width=20)
            widget.grid(row=row, column=col+1, padx=5, pady=5)
            entries[key] = widget
        
        def clear_form():
            for w in entries.values():
                if isinstance(w, ttk.Combobox): w.set('')
                else: w.delete(0, tk.END)
            selected_user_id.set(0)
        
        def add_user():
            try:
                from models import User
                session = get_session()
                username = entries['username'].get().strip()
                full_name = entries['full_name'].get().strip()
                role = entries['role'].get().strip()
                password = entries['password'].get().strip()
                email = entries['email'].get().strip()
                question = entries['question'].get().strip()
                
                if not all([username, full_name, role, password]):
                    messagebox.showwarning("هشدار", "فیلدهای اجباری را پر کنید", parent=win)
                    session.close(); return
                
                if session.query(User).filter(User.username == username).first():
                    messagebox.showwarning("هشدار", "نام کاربری تکراری است", parent=win)
                    session.close(); return
                
                new_user = User(username=username, full_name=full_name, role=role,
                               email=email if email else None,
                               security_question=question if question else None)
                new_user.password_hash = AuthManager.hash_password(password)
                if question:
                    new_user.security_answer_hash = AuthManager.hash_password(password)
                
                session.add(new_user); session.commit(); session.close()
                load_users(); clear_form()
                messagebox.showinfo("موفق", "کاربر با موفقیت افزوده شد", parent=win)
            except Exception as e:
                messagebox.showerror("خطا", str(e), parent=win)
        
        def update_user():
            uid = selected_user_id.get()
            
            if not uid:
                messagebox.showwarning("هشدار", "ابتدا یک کاربر از لیست انتخاب کنید", parent=win)
                return
            
            full_name = entries['full_name'].get().strip()
            role = entries['role'].get().strip()
            email = entries['email'].get().strip()
            password = entries['password'].get().strip()
            
            success, msg = AuthManager.update_user(
                user_id=uid,
                full_name=full_name,
                email=email if email else None,
                role=role,
                password=password if password else None
            )
            
            if success:
                load_users()
                clear_form()
                messagebox.showinfo("موفق", "کاربر با موفقیت بروزرسانی شد", parent=win)
            else:
                messagebox.showerror("خطا", msg, parent=win)
        
        ttk.Button(form, text="✔افزودن", command=add_user, width=15).grid(row=2, column=0, pady=15, padx=3)
        ttk.Button(form, text="✏ویرایش", command=update_user, width=15).grid(row=2, column=1, pady=15, padx=3)
        ttk.Button(form, text="🔄تازه سازی", command=clear_form, width=15).grid(row=2, column=2, pady=15, padx=3)
        
        table_frame = ttk.LabelFrame(win, text="لیست کاربران", padding="10")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        cols = ("شناسه", "نام کاربری", "نام کامل", "نقش", "وضعیت", "آخرین ورود")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        widths = [60, 120, 150, 100, 80, 140]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c, anchor='center'); tree.column(c, anchor='center', width=w)
        tree.pack(fill='both', expand=True)
        
        def load_users():
            for item in tree.get_children(): tree.delete(item)
            for u in AuthManager.get_all_users():
                status = "✅ فعال" if u.is_active else "❌ غیرفعال"
                last = u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else "-"
                tree.insert("", "end", values=(u.id, u.username, u.full_name,
                           AuthManager.get_user_role_name(u.role), status, last))
        
        def on_select(event):
            sel = tree.focus()
            if not sel: return
            vals = tree.item(sel)['values']
            selected_user_id.set(vals[0])
            
            for w in entries.values():
                if isinstance(w, ttk.Combobox): w.set('')
                else: w.delete(0, tk.END)
            
            entries['username'].insert(0, vals[1])
            entries['full_name'].insert(0, vals[2])
            role_map = {'ادمین کل': 'admin', 'مدیر آموزش': 'manager', 'استاد': 'professor', 'دانشجو': 'student'}
            entries['role'].set(role_map.get(vals[3], 'student'))
        
        tree.bind('<<TreeviewSelect>>', on_select)
        load_users()
        
        btn_frame = ttk.Frame(table_frame); btn_frame.pack(fill='x', pady=8)
        
        def toggle():
            sel = tree.focus()
            if sel:
                uid = tree.item(sel)['values'][0]
                success, msg = AuthManager.toggle_user_status(uid)
                load_users()
                messagebox.showinfo("نتیجه", msg, parent=win)
        
        def delete():
            sel = tree.focus()
            if sel:
                uid = tree.item(sel)['values'][0]; uname = tree.item(sel)['values'][1]
                if uname == 'admin':
                    messagebox.showwarning("هشدار", "ادمین اصلی قابل حذف نیست", parent=win); return
                if messagebox.askyesno("تأیید حذف", f"آیا از حذف کاربر '{uname}' اطمینان دارید؟", parent=win):
                    success, msg = AuthManager.delete_user(uid)
                    load_users()
                    messagebox.showinfo("نتیجه", msg, parent=win)
        
        ttk.Button(btn_frame, text="فعال/غیرفعال", command=toggle, width=16).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌حذف کاربر", command=delete, width=16).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔁تازه‌سازی", command=load_users, width=16).pack(side='left', padx=5)
    
    def _show_logs(self):
        win = tk.Toplevel(self.window)
        win.title("تاریخچه فعالیت‌ها")
        win.geometry("800x500")
        
        from models import AuditLog
        tree = ttk.Treeview(win, columns=("کاربر", "فعالیت", "زمان"), show="headings", height=20)
        for c, w in [("کاربر", 150), ("فعالیت", 450), ("زمان", 160)]:
            tree.heading(c, text=c, anchor='center'); tree.column(c, width=w, anchor='center')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        session = get_session()
        try:
            for log in session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all():
                name = log.user.full_name if log.user else "نامشخص"
                time_str = log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else ""
                tree.insert("", "end", values=(name, log.action, time_str))
        finally: session.close()
    
    def _show_help(self): messagebox.showinfo("راهنما", "AcadFlow نسخه ۳.۰\n\nسیستم جامع مدیریت آموزشی")
    def _show_about(self): messagebox.showinfo("درباره", f"AcadFlow نسخه {VERSION}\n\nارائه شده توسط {COMPANY}")
    
    def _refresh_all(self):
        for tab in self.tabs:
            if hasattr(tab, 'refresh_data'): tab.refresh_data()
        self._update_status("همه بخش‌ها بروزرسانی شدند")
    
    def _exit(self):
        if messagebox.askyesno("خروج", "آیا مطمئن هستید؟"): self.window.destroy()
    
    def run(self): self.window.mainloop()