# tabs/dashboard_tab.py
import tkinter as tk
from tkinter import ttk
from database import get_session
from models import Student, Master, Lesson, Presentation, Selection
from auth import AuthManager
from sqlalchemy import func
import arabic_reshaper
from bidi.algorithm import get_display

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except:
    HAS_MPL = False


def fa(text):
    """تابع کمکی برای راست‌چین و درست کردن حروف فارسی - فقط برای matplotlib"""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)


class DashboardTab:
    def __init__(self, parent, user, main_window):
        self.parent = parent
        self.user = user
        self.main_window = main_window
        self.frame = ttk.Frame(self.parent)
        self.parent.add(self.frame, text="📊 داشبورد")
        try:
            self.font = ('B Nazanin', 11)
            self.font_bold = ('B Nazanin', 12, 'bold')
            self.font_title = ('B Nazanin', 14, 'bold')
            self.font_big = ('B Nazanin', 18, 'bold')
        except:
            self.font = ('Tahoma', 10)
            self.font_bold = ('Tahoma', 11, 'bold')
            self.font_title = ('Tahoma', 13, 'bold')
            self.font_big = ('Tahoma', 16, 'bold')
        
        if not AuthManager.can_user_view_all(self.user['role']):
            ttk.Label(self.frame, text="دسترسی محدود", font=self.font_big).pack(pady=50)
            return
        
        self._build()
    
    def _build(self):
        # ========== Canvas + Scrollbar + Mousewheel ==========
        canvas = tk.Canvas(self.frame, bg='#e8ecf1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        # تنظیم عرض canvas با عرض scroll_frame
        def _configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _configure_canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== MOUSEWHEEL SCROLL ==========
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ========== Title bar ==========
        title_frame = tk.Frame(scroll_frame, bg='#1a1a2e', height=50)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="  📊 داشبورد مدیریتی", font=self.font_big,
                fg='white', bg='#1a1a2e').pack(side='right', padx=20, pady=8)
        ttk.Button(title_frame, text="🔄 بروزرسانی", command=self.refresh_data, width=18).pack(side='left', padx=3, pady=3)
        
        # ========== Main container ==========
        main_container = tk.Frame(scroll_frame, bg='#e8ecf1')
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # ========== ۵ کارت آماری اصلی ==========
        session = get_session()
        try:
            avg = session.query(func.avg(Selection.score)).filter(Selection.score != None).scalar()
            stats = [
                ("👨‍🎓 دانشجویان", session.query(Student).count(), "#3498db"),
                ("👨‍🏫 اساتید", session.query(Master).count(), "#2ecc71"),
                ("📚 دروس", session.query(Lesson).count(), "#e74c3c"),
                ("📅 کلاس‌ها", session.query(Presentation).count(), "#f39c12"),
                ("📊 میانگین نمرات", f"{avg:.1f}" if avg else "-", "#9b59b6"),
            ]
        finally:
            session.close()
        
        stats_frame = tk.Frame(main_container, bg='#e8ecf1')
        stats_frame.pack(fill='x', pady=(0, 15))
        
        for title, value, color in stats:
            card = tk.Frame(stats_frame, bg='white', bd=0, highlightthickness=1, highlightbackground='#ddd')
            card.pack(side='left', padx=8, expand=True, fill='x')
            
            tk.Frame(card, bg=color, height=5).pack(fill='x')
            content = tk.Frame(card, bg='white')
            content.pack(fill='both', expand=True, padx=15, pady=12)
            
            tk.Label(content, text=title, font=self.font, fg='#666', bg='white').pack(anchor='w')
            tk.Label(content, text=str(value), font=('Arial', 24, 'bold'), fg=color, bg='white').pack(anchor='e', pady=(5, 0))
        
        # ========== ۳ نمودار - فقط از fa() برای matplotlib استفاده کن ==========
        if HAS_MPL:
            charts_frame = tk.Frame(main_container, bg='white', bd=0, highlightthickness=1, highlightbackground='#ddd')
            charts_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(charts_frame, text="  📈 نمودارهای آماری", font=self.font_title,
                    fg='#2c3e50', bg='white').pack(anchor='w', padx=10, pady=10)
            
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))
            fig.patch.set_facecolor('white')
            
            session = get_session()
            try:
                # نمودار ۱
                majors = session.query(Student.major, func.count(Student.id)).group_by(Student.major).all()
                if majors:
                    labels = [fa(m[0]) for m in majors]
                    sizes = [m[1] for m in majors]
                    colors_pie = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
                    axes[0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_pie[:len(labels)], startangle=90)
                    axes[0].set_title(fa('توزیع رشته‌ها'), fontsize=11, fontweight='bold')
                
                # نمودار ۲
                scores = session.query(Selection.score).filter(Selection.score != None).all()
                if scores:
                    axes[1].hist([s[0] for s in scores], bins=10, color='#3498db', edgecolor='white')
                    axes[1].set_title(fa('توزیع نمرات'), fontsize=11, fontweight='bold')
                    axes[1].set_xlabel(fa('نمره'), fontsize=9)
                    axes[1].set_ylabel(fa('تعداد'), fontsize=9)
                
                # نمودار ۳
                grades = session.query(Student.graduation, func.count(Student.id)).group_by(Student.graduation).all()
                if grades:
                    g_labels = [fa(g[0]) if g[0] else fa('نامشخص') for g in grades]
                    g_values = [g[1] for g in grades]
                    axes[2].bar(g_labels, g_values, color=['#3498db', '#2ecc71', '#e74c3c'])
                    axes[2].set_title(fa('مقاطع تحصیلی'), fontsize=11, fontweight='bold')
            finally:
                session.close()
            
            plt.tight_layout()
            FigureCanvasTkAgg(fig, charts_frame).get_tk_widget().pack(fill='x', padx=10, pady=10)
        
        # ========== ۴ کارت تحلیلی ==========
        session = get_session()
        try:
            top_major = session.query(Student.major, func.count(Student.id)).group_by(Student.major).order_by(func.count(Student.id).desc()).first()
            best_student = session.query(Student.name, func.avg(Selection.score)).join(Selection).filter(Selection.score != None).group_by(Student.id).order_by(func.avg(Selection.score).desc()).first()
            busiest_day = session.query(Presentation.day_hold, func.count(Presentation.id)).group_by(Presentation.day_hold).order_by(func.count(Presentation.id).desc()).first()
            top_lesson = session.query(Lesson.name, func.count(Selection.id)).select_from(Lesson).join(Presentation, Lesson.id == Presentation.lesson_id).join(Selection, Presentation.id == Selection.presentation_id).group_by(Lesson.id).order_by(func.count(Selection.id).desc()).first()
        finally:
            session.close()
        
        info_cards = [
            ("🏆 متراکم ترین رشته", top_major[0] if top_major else "-", "#3498db"),
            ("⭐ بالاترین معدل", f"{best_student[0]} ({best_student[1]:.1f})" if best_student else "-", "#2ecc71"),
            ("📅 شلوغ‌ترین روز", busiest_day[0] if busiest_day else "-", "#e74c3c"),
            ("📚 پرطرفدارترین درس", top_lesson[0] if top_lesson else "-", "#f39c12"),
        ]
        
        info_frame = tk.Frame(main_container, bg='#e8ecf1')
        info_frame.pack(fill='x', pady=(0, 15))
        
        for title, value, color in info_cards:
            card = tk.Frame(info_frame, bg='white', bd=0, highlightthickness=1, highlightbackground='#ddd')
            card.pack(side='left', padx=8, expand=True, fill='x')
            
            tk.Frame(card, bg=color, height=5).pack(fill='x')
            content = tk.Frame(card, bg='white')
            content.pack(fill='both', expand=True, padx=15, pady=15)
            
            tk.Label(content, text=title, font=self.font, fg='#666', bg='white').pack(anchor='w')
            tk.Label(content, text=str(value), font=('Arial', 18, 'bold'), fg=color, bg='white').pack(anchor='e', pady=(5, 0))
        
        # ========== خوش‌آمدگویی ==========
        welcome = tk.Frame(main_container, bg='white', bd=0, highlightthickness=1, highlightbackground='#ddd')
        welcome.pack(fill='both', expand=True)
        
        tk.Label(welcome, text=f"🎓 خوش آمدید {self.user['full_name']}",
                font=self.font_big, fg='#2c3e50', bg='white').pack(pady=(20, 5))
        tk.Label(welcome, text=f"نقش شما: {AuthManager.get_user_role_name(self.user['role'])}",
                font=self.font_title, fg='#7f8c8d', bg='white').pack()
        tk.Label(welcome, text="به سیستم جامع مدیریت آموزشی AcadFlow خوش آمدید.",
                font=self.font, fg='#95a5a6', bg='white').pack(pady=(10, 20))
    
    def refresh_data(self):
        for w in self.frame.winfo_children():
            w.destroy()
        self._build()