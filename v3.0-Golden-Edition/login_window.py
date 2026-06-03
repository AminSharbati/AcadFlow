# login_window.py
import tkinter as tk
from tkinter import messagebox
from auth import AuthManager
from config import COMPANY, VERSION

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AcadFlow - ورود به سیستم")
        self.window.geometry("550x650")
        self.window.resizable(False, False)
        self.window.configure(bg="#b1b1b1")
        self.user_data = None
        
        try:
            self.font_title = ('B Nazanin', 30, 'bold')
            self.font_normal = ('B Nazanin', 15)
            self.font_small = ('B Nazanin', 10)
            self.font_btn = ('B Nazanin', 15, 'bold')
            self.font_login = ('B Nazanin', 15, 'bold')
        except:
            self.font_title = ('Arial', 25, 'bold')
            self.font_normal = ('Arial', 12)
            self.font_small = ('Arial', 8)
            self.font_btn = ('Arial', 12, 'bold')
            self.font_login = ('Arial', 12, 'bold')
        
        self._build_ui()
        self.window.bind('<Return>', lambda e: self._login())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.entry_user.focus()
    
    def _build_ui(self):
        header = tk.Frame(self.window, bg='#b1b1b1', height=110)
        header.pack(fill='x'); header.pack_propagate(False)
        tk.Label(header, text="AcadFlow", font=self.font_title, fg="#000000", bg='#b1b1b1').pack(pady=(25, 0))
        tk.Label(header, text="سیستم جامع مدیریت آموزشی جریان | نسخه طلایی", font=self.font_small, fg="#000000", bg='#b1b1b1').pack()
        
        card = tk.Frame(self.window, bg='#161b22', padx=25, pady=20)
        card.pack(padx=20, pady=15, fill='both')
        
        tk.Label(card, text="ورود به حساب کاربری", font=self.font_login, fg='#e6edf3', bg='#161b22').pack(pady=(10, 15))
        
        tk.Label(card, text="نام کاربری", font=self.font_small, fg='#8b949e', bg='#161b22').pack(anchor='w')
        self.entry_user = tk.Entry(card, font=self.font_normal, bg='#0d1117', fg='#e6edf3', insertbackground='white',
                                   relief='flat', bd=0, highlightbackground='#30363d', highlightcolor='#58a6ff', highlightthickness=1)
        self.entry_user.pack(fill='x', ipady=6, pady=(3, 10))
        
        tk.Label(card, text="رمز عبور", font=self.font_small, fg='#8b949e', bg='#161b22').pack(anchor='w')
        self.entry_pass = tk.Entry(card, font=self.font_normal, bg='#0d1117', fg='#e6edf3', insertbackground='white',
                                   relief='flat', bd=0, show='●', highlightbackground='#30363d', highlightcolor='#58a6ff', highlightthickness=1)
        self.entry_pass.pack(fill='x', ipady=6, pady=(3, 5))
        
        self.show_var = tk.BooleanVar()
        tk.Checkbutton(card, text="نمایش رمز عبور", variable=self.show_var,
                      command=lambda: self.entry_pass.config(show='' if self.show_var.get() else '●'),
                      fg='#8b949e', bg='#161b22', selectcolor='#161b22', activebackground='#161b22', font=self.font_small).pack(anchor='w', pady=(0, 12))
        
        tk.Button(card, text="ورود به سیستم", font=self.font_btn, bg='#238636', fg='white', activebackground='#2ea043',
                 relief='flat', bd=0, cursor='hand2', command=self._login, height=1).pack(fill='x', pady=(0, 5))
        
        tk.Label(card, text=f"ارائه شده توسط {COMPANY}", font=self.font_small, fg='#484f58', bg='#161b22').pack(pady=(5, 2))
        
        tk.Button(card, text="رمز عبور را فراموش کرده‌ام", font=self.font_small, fg='#58a6ff', bg='#161b22', bd=0,
                 cursor='hand2', activebackground='#161b22', activeforeground='#79c0ff', command=self._recover_password).pack(pady=(2, 3))
        
        self.lbl_error = tk.Label(card, text="", font=self.font_small, fg='#f85149', bg='#161b22')
        self.lbl_error.pack(pady=(3, 5))
        
        tk.Label(self.window, text=f"نسخه {VERSION}", font=self.font_small, fg="#000000", bg='#b1b1b1').pack(side='bottom', pady=10)
    
    def _login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not username or not password: self.lbl_error.config(text="لطفاً همه فیلدها را پر کنید"); return
        self.lbl_error.config(text="در حال بررسی...", fg='#d2991d'); self.window.update()
        result, message = AuthManager.login(username, password)
        if result: self.user_data = result; self.window.destroy()
        else: self.lbl_error.config(text=message, fg='#f85149'); self.entry_pass.delete(0, tk.END)
    
    def _recover_password(self):
        username = self.entry_user.get().strip()
        if not username: self.lbl_error.config(text="ابتدا نام کاربری را وارد کنید"); return
        from database import get_session
        from models import User
        session = get_session()
        user = session.query(User).filter(User.username == username).first()
        if not user: self.lbl_error.config(text="کاربر یافت نشد"); session.close(); return
        if not user.security_question: self.lbl_error.config(text="سوال امنیتی ثبت نشده"); session.close(); return
        
        recover = tk.Toplevel(self.window)
        recover.title("بازیابی رمز عبور"); recover.geometry("400x300")
        recover.configure(bg='#b1b1b1'); recover.resizable(False, False)
        
        tk.Label(recover, text="بازیابی رمز عبور", font=self.font_login, fg="#000000", bg='#b1b1b1').pack(pady=20)
        tk.Label(recover, text=f"سوال: کدملی شما؟", font=self.font_normal, fg="#000000", bg='#b1b1b1').pack(pady=10)
        answer_entry = tk.Entry(recover, font=self.font_normal, bg="#000000", fg='#e6edf3', relief='flat')
        answer_entry.pack(fill='x', padx=30, ipady=5, pady=10); answer_entry.focus()
        result_label = tk.Label(recover, text="", font=self.font_small, fg='#f85149', bg='#b1b1b1'); result_label.pack()
        
        def check():
            ans = answer_entry.get().strip()
            if not ans: result_label.config(text="پاسخ را وارد کنید"); return
            new_pass, msg = AuthManager.recover_password(username, ans)
            if new_pass:
                result_label.config(text=f"رمز جدید: {new_pass}", fg='#3fb950')
                self.entry_pass.delete(0, tk.END); self.entry_pass.insert(0, new_pass)
                recover.after(2000, recover.destroy)
            else: result_label.config(text=msg, fg='#f85149')
        
        tk.Button(recover, text="بررسی", font=self.font_btn, bg='#238636', fg='white', relief='flat', command=check).pack(pady=15)
        session.close()
    
    def run(self): self.window.mainloop(); return self.user_data