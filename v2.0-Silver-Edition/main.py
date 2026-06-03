# AcadFlow v2.0 - Silver Edition
# سیستم جامع مدیریت آموزشی | نسخه نقره ای
# Code First with SQLAlchemy + Tkinter
# ارائه شده توسط تیم داتین آریا | ۱۴۰۵

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, func, event
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from enum import Enum
import os

# ============================================================
# تنظیمات
# ============================================================
APP_NAME = "AcadFlow"
VERSION = "2.0.0"
COMPANY = "داتین آریا"
DB_FILE = 'acadflow_v2.0.db'
Base = declarative_base()

# ============================================================
# Enum ها
# ============================================================
class GradeLevel(Enum):
    WEAK = ("ضعیف", 0, 9, "red")
    AVERAGE = ("متوسط", 9, 15, "#f39c12")
    EXCELLENT = ("عالی", 15, 20, "green")
    
    @classmethod
    def get_rank(cls, score):
        for level in cls:
            if level.value[1] <= score < level.value[2]:
                return level
        return cls.WEAK if score < 9 else cls.EXCELLENT

class Major(Enum):
    COMPUTER = "کامپیوتر"
    ELECTRICAL = "برق"
    CIVIL = "عمران"
    MECHANICAL = "مکانیک"
    ARCHITECTURE = "معماری"
    OTHER = "سایر"
    
    @classmethod
    def list_all(cls):
        return [m.value for m in cls]

class WeekDay(Enum):
    SATURDAY = "شنبه"
    SUNDAY = "یکشنبه"
    MONDAY = "دوشنبه"
    TUESDAY = "سه‌شنبه"
    WEDNESDAY = "چهارشنبه"
    
    @classmethod
    def list_all(cls):
        return [d.value for d in cls]

# ============================================================
# مدل های دیتابیس
# ============================================================
class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    student_code = Column(String(20), unique=True)
    national_code = Column(String(10), unique=True)
    entrance_term = Column(String(10))
    graduation = Column(String(50))
    mobile = Column(String(20), nullable=False)
    email = Column(String(100))
    major = Column(String(50), nullable=False)
    
    selections = relationship("Selection", back_populates="student", cascade="all, delete-orphan")
    
    COLUMNS = {
        "شناسه": "id", "نام": "name", "کد دانشجویی": "student_code",
        "کد ملی": "national_code", "ترم": "entrance_term", "مقطع": "graduation",
        "موبایل": "mobile", "ایمیل": "email", "رشته": "major"
    }

class Master(Base):
    __tablename__ = 'masters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    national_code = Column(String(10), unique=True)
    degree = Column(String(50))
    department = Column(String(50))
    mobile = Column(String(20), nullable=False)
    email = Column(String(100))
    
    presentations = relationship("Presentation", back_populates="master", cascade="all, delete-orphan")
    
    COLUMNS = {
        "شناسه": "id", "نام": "name", "کد ملی": "national_code",
        "مدرک": "degree", "دپارتمان": "department", "موبایل": "mobile", "ایمیل": "email"
    }

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    unit = Column(Integer, nullable=False)
    major = Column(String(50), nullable=False)
    description = Column(String(500))
    max_capacity = Column(Integer, default=50)
    
    presentations = relationship("Presentation", back_populates="lesson")
    
    COLUMNS = {
        "شناسه": "id", "نام": "name", "واحد": "unit",
        "رشته": "major", "ظرفیت": "max_capacity", "توضیحات": "description"
    }

class Presentation(Base):
    __tablename__ = 'presentations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(Integer, ForeignKey('masters.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    day_hold = Column(String(50))
    start_time = Column(Integer)
    finish_time = Column(Integer)
    capacity = Column(Integer, default=30)
    enrolled = Column(Integer, default=0)
    
    master = relationship("Master", back_populates="presentations")
    lesson = relationship("Lesson", back_populates="presentations")
    selections = relationship("Selection", back_populates="presentation", cascade="all, delete-orphan")
    
    COLUMNS = {
        "شناسه": "id", "استاد": "master_id", "درس": "lesson_id",
        "روز": "day_hold", "شروع": "start_time", "پایان": "finish_time",
        "ظرفیت": "capacity", "ثبت‌نامی": "enrolled"
    }
    
    @property
    def display_name(self):
        m = self.master.name if self.master else 'نامشخص'
        l = self.lesson.name if self.lesson else 'نامشخص'
        return f"{l} ({m}، {self.day_hold})"
    
    @property
    def summary(self):
        if self.lesson and self.master:
            return f"{self.lesson.name} ({self.master.name})"
        return 'نامشخص'
    
    @property
    def available_seats(self):
        return self.capacity - self.enrolled

class Selection(Base):
    __tablename__ = 'selections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    presentation_id = Column(Integer, ForeignKey('presentations.id'), nullable=False)
    score = Column(Float)
    year_education = Column(Integer)
    status = Column(String(20), default='active')
    
    student = relationship("Student", back_populates="selections")
    presentation = relationship("Presentation", back_populates="selections")
    
    COLUMNS = {
        "شناسه": "id", "دانشجو": "student_id", "درس": "presentation_id",
        "نمره": "score", "سال": "year_education", "وضعیت": "status"
    }
    
    def get_status_text(self):
        if self.score is None: return "ثبت نشده"
        return "✅ قبول" if self.score >= 10 else "❌ مردود"

# ============================================================
# دیتابیس
# ============================================================
engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ============================================================
# برنامه اصلی
# ============================================================
class AcadFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - سیستم جامع مدیریت آموزشی | نسخه نقره ای {VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(950, 600)
        
        try:
            self.font_small = ('B Nazanin', 10)
            self.font_normal = ('B Nazanin', 11)
            self.font_bold = ('B Nazanin', 11, 'bold')
            self.font_title = ('B Nazanin', 14, 'bold')
            self.font_header = ('B Nazanin', 16, 'bold')
        except:
            self.font_small = ('Tahoma', 9)
            self.font_normal = ('Tahoma', 10)
            self.font_bold = ('Tahoma', 10, 'bold')
            self.font_title = ('Tahoma', 13, 'bold')
            self.font_header = ('Tahoma', 14, 'bold')
        
        self.session = Session()
        self._setup_styles()
        self._create_header()
        
        self.majors_list = Major.list_all()
        self.week_days = WeekDay.list_all()
        self.id_to_name_map = {}
        self.combo_fk_cache = {}
        
        self._create_notebook()
        self._create_statusbar()
        
        self.root.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self._update_status("✓ برنامه با موفقیت راه‌اندازی شد")
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=self.font_normal)
        style.configure('TLabel', font=self.font_normal, padding=3)
        style.configure('TButton', font=self.font_bold, padding=7)
        style.configure('TEntry', font=self.font_normal, padding=4)
        style.configure('TCombobox', font=self.font_normal, padding=4)
        style.configure('Treeview', font=self.font_normal, rowheight=28)
        style.configure('Treeview.Heading', font=self.font_bold, padding=7)
        style.configure('TLabelframe.Label', font=self.font_title, foreground='#2c3e50')
        style.configure('TNotebook.Tab', font=self.font_bold, padding=[15, 7])
    
    def _create_header(self):
        header = tk.Frame(self.root, bg='#1a1a2e', height=55)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"  {APP_NAME}", font=self.font_header,
                fg='#e94560', bg='#1a1a2e').pack(side='left', padx=15)
        tk.Label(header, text=f"نسخه {VERSION} | نسخه نقره ای | {COMPANY}  ",
                font=self.font_small, fg='#8b949e', bg='#1a1a2e').pack(side='right', padx=15)
    
    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.root, padding=(5, 5, 5, 0))
        self.notebook.pack(fill='both', expand=True, padx=8, pady=(0, 5))
        
        self.tabs = {}
        tab_configs = [
            ('student', Student, "👨‍🎓 دانشجویان", [
                ("نام دانشجو", "name"), ("کد دانشجویی", "student_code"),
                ("کد ملی", "national_code"), ("ترم ورود", "entrance_term", "optional"),
                ("مقطع", "graduation"), ("موبایل", "mobile"),
                ("ایمیل", "email", "optional"), ("رشته تحصیلی", "major", "combo", self.majors_list)
            ]),
            ('master', Master, "👨‍🏫 اساتید", [
                ("نام استاد", "name"), ("کد ملی", "national_code"),
                ("مدرک تحصیلی", "degree"), ("دپارتمان", "department"),
                ("موبایل", "mobile"), ("ایمیل", "email", "optional")
            ]),
            ('lesson', Lesson, "📚 دروس", [
                ("نام درس", "name"), ("تعداد واحد", "unit", "int"),
                ("رشته تحصیلی", "major", "combo", self.majors_list),
                ("ظرفیت", "max_capacity", "int_optional"),
                ("توضیحات", "description", "optional")
            ]),
            ('presentation', Presentation, "📅 ارائه دروس", [
                ("استاد", "master_id", "combo_fk", Master, 'id', 'name'),
                ("درس", "lesson_id", "combo_fk", Lesson, 'id', 'name'),
                ("روز برگزاری", "day_hold", "combo", self.week_days),
                ("ساعت شروع", "start_time", "int_optional"),
                ("ساعت پایان", "finish_time", "int_optional"),
                ("ظرفیت کلاس", "capacity", "int_optional")
            ]),
            ('selection', Selection, "📝 انتخاب واحد", [
                ("فیلتر رشته", "major_filter", "combo_major_filter", self.majors_list),
                ("دانشجو", "student_id", "combo_fk_filtered", Student, 'id', 'name'),
                ("درس (ارائه)", "presentation_id", "combo_fk_filtered", Presentation, 'id', 'display_name'),
                ("سال تحصیلی", "year_education", "int_optional"),
                ("نمره", "score", "score_optional")
            ])
        ]
        
        for key, model, title, fields in tab_configs:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=title)
            self.tabs[key] = {'frame': tab, 'model': model, 'title': title, 'fields': fields}
            self._build_tab(key)
            self._load_fk_combos(key)
        
        # تب گزارش
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text='📈 گزارش و آمار')
        self._build_report_tab()
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
    
    def _build_tab(self, tab_key):
        info = self.tabs[tab_key]
        frame = info['frame']
        model = info['model']
        fields = info['fields']
        
        # فرم
        form = ttk.LabelFrame(frame, text=f"📝 فرم {info['title']}", padding="15")
        form.pack(fill='x', padx=10, pady=10)
        
        info['entries'] = {}
        for i, f in enumerate(fields):
            label, db_field = f[0], f[1]
            field_type = f[2] if len(f) > 2 else 'str'
            row, col = i // 3, (i % 3) * 2
            
            ttk.Label(form, text=f"{label}:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
            
            if field_type.startswith('combo'):
                widget = ttk.Combobox(form, width=20, state='readonly', font=self.font_normal)
                if field_type == 'combo':
                    widget['values'] = f[3] if len(f) > 3 else []
                elif field_type == 'combo_major_filter':
                    widget['values'] = self.majors_list
                    widget.bind('<<ComboboxSelected>>', lambda e: self._filter_selection_combos())
                elif field_type in ('combo_fk', 'combo_fk_filtered'):
                    self.combo_fk_cache[(tab_key, db_field)] = widget
                    widget['values'] = []
            else:
                widget = ttk.Entry(form, width=22, font=self.font_normal)
            
            widget.grid(row=row, column=col+1, padx=5, pady=5, sticky='ew')
            info['entries'][db_field] = widget
        
        # دکمه ها
        btn_row = (len(fields) // 3) + 1
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=btn_row, column=0, columnspan=6, pady=15)
        
        ttk.Button(btn_frame, text="✔افزودن", command=lambda: self._add_record(tab_key), width=15).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="✏ویرایش", command=lambda: self._update_record(tab_key), width=15).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="❌حذف", command=lambda: self._delete_record(tab_key), width=15).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="🔁تازه‌سازی", command=lambda: self._refresh_tab(tab_key), width=15).pack(side='left', padx=4)
        
        # جدول + جستجو
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # نوار جستجو
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(search_frame, text="🔍 جستجو:", font=self.font_normal).pack(side='right', padx=5)
        search_entry = ttk.Entry(search_frame, font=self.font_normal, width=25)
        search_entry.pack(side='right', padx=5)
        info['search_entry'] = search_entry
        
        # جدول
        cols = list(model.COLUMNS.keys())
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", height=12)
        for c in cols:
            tree.heading(c, text=c, anchor='center')
            tree.column(c, anchor='center', width=100, minwidth=75)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        
        info['treeview'] = tree
        tree.bind('<<TreeviewSelect>>', lambda e: self._on_row_select(tab_key))
        
        # منوی راست کلیک
        ctx_menu = tk.Menu(frame, tearoff=0, font=self.font_normal)
        ctx_menu.add_command(label="🔄 بازخوانی", command=lambda: self._refresh_tab(tab_key))
        ctx_menu.add_command(label="🗑️ حذف", command=lambda: self._delete_record(tab_key))
        tree.bind("<Button-3>", lambda e: ctx_menu.tk_popup(e.x_root, e.y_root))
        
        # رنگ ردیف ها
        tree.tag_configure('even', background='#f8f9fa')
        tree.tag_configure('odd', background='white')
        
        # bind جستجو
        search_entry.bind('<KeyRelease>', lambda e, k=tab_key: self._filter_table(k))
        
        self._load_data(tab_key)
    
    # ==================== CRUD ====================
    def _get_form_data(self, tab_key):
        info = self.tabs[tab_key]
        data = {}
        for f in info['fields']:
            label, db_field = f[0], f[1]
            field_type = f[2] if len(f) > 2 else 'str'
            if db_field == 'major_filter': continue
            
            widget = info['entries'][db_field]
            value = widget.get().strip()
            is_opt = 'optional' in field_type
            
            if not is_opt and not value:
                raise ValueError(f"فیلد '{label}' اجباری است")
            if not value and is_opt:
                data[db_field] = None; continue
            
            if field_type.startswith('combo_fk'):
                cache_info = self.combo_fk_cache.get((tab_key, db_field))
                if cache_info:
                    session = self.session
                    fk_model = f[3]
                    name_field = f[5]
                    for r in session.query(fk_model).all():
                        display = r.display_name if hasattr(r, 'display_name') else getattr(r, name_field, '')
                        if display == value:
                            data[db_field] = r.id; break
            elif field_type == 'score_optional':
                score = float(value)
                if not (0 <= score <= 20): raise ValueError("نمره باید بین ۰ تا ۲۰ باشد")
                data[db_field] = score
            elif 'int' in field_type:
                data[db_field] = int(value)
            elif field_type.startswith('combo'):
                data[db_field] = value
            else:
                data[db_field] = value
        return data
    
    def _add_record(self, tab_key):
        try:
            data = self._get_form_data(tab_key)
            record = self.tabs[tab_key]['model'](**data)
            self.session.add(record)
            self.session.commit()
            self._clear_form(tab_key)
            self._refresh_tab(tab_key)
            messagebox.showinfo("موفق", "رکورد با موفقیت افزوده شد")
        except ValueError as e: messagebox.showerror("خطا", str(e))
        except IntegrityError: self.session.rollback(); messagebox.showerror("خطا", "اطلاعات تکراری است")
        except Exception as e: self.session.rollback(); messagebox.showerror("خطا", str(e))
    
    def _update_record(self, tab_key):
        info = self.tabs[tab_key]
        sel = info['treeview'].focus()
        if not sel: messagebox.showwarning("هشدار", "رکوردی انتخاب نشده"); return
        try:
            pk = info['treeview'].item(sel)['values'][0]
            data = self._get_form_data(tab_key)
            record = self.session.query(info['model']).get(pk)
            if record:
                for k, v in data.items(): setattr(record, k, v)
                self.session.commit()
                self._clear_form(tab_key)
                self._refresh_tab(tab_key)
                messagebox.showinfo("موفق", "رکورد با موفقیت ویرایش شد")
        except ValueError as e: messagebox.showerror("خطا", str(e))
        except Exception as e: self.session.rollback(); messagebox.showerror("خطا", str(e))
    
    def _delete_record(self, tab_key):
        info = self.tabs[tab_key]
        sel = info['treeview'].focus()
        if not sel: messagebox.showwarning("هشدار", "رکوردی انتخاب نشده"); return
        if not messagebox.askyesno("تأیید", "آیا از حذف اطمینان دارید؟"): return
        try:
            pk = info['treeview'].item(sel)['values'][0]
            record = self.session.query(info['model']).get(pk)
            if record: self.session.delete(record); self.session.commit()
            self._clear_form(tab_key); self._refresh_tab(tab_key)
            messagebox.showinfo("موفق", "رکورد حذف شد")
        except IntegrityError: self.session.rollback(); messagebox.showerror("خطا", "رکورد وابستگی دارد")
        except Exception as e: self.session.rollback(); messagebox.showerror("خطا", str(e))
    
    # ==================== کمکی ====================
    def _clear_form(self, tab_key):
        for w in self.tabs[tab_key]['entries'].values():
            if isinstance(w, ttk.Combobox): w.set('')
            else: w.delete(0, tk.END)
    
    def _load_data(self, tab_key):
        info = self.tabs[tab_key]
        tree = info['treeview']
        for item in tree.get_children(): tree.delete(item)
        
        records = self.session.query(info['model']).all()
        col_keys = list(info['model'].COLUMNS.values())
        
        for i, rec in enumerate(records):
            row = []
            for attr in col_keys:
                value = getattr(rec, attr)
                if info['model'] == Presentation:
                    if attr == 'master_id': value = rec.master.name if rec.master else 'نامشخص'
                    elif attr == 'lesson_id': value = rec.lesson.name if rec.lesson else 'نامشخص'
                elif info['model'] == Selection:
                    if attr == 'student_id': value = rec.student.name if rec.student else 'نامشخص'
                    elif attr == 'presentation_id': value = rec.presentation.summary if rec.presentation else 'نامشخص'
                    elif attr == 'status': value = rec.get_status_text()
                    elif attr == 'score' and value is not None: value = f"{value:.1f}"
                row.append(value if value is not None else '')
            tree.insert("", "end", values=row, tags=('even' if i % 2 == 0 else 'odd',))
    
    def _filter_table(self, tab_key):
        info = self.tabs[tab_key]
        search = info['search_entry'].get().strip()
        tree = info['treeview']
        for item in tree.get_children(): tree.delete(item)
        
        if not search:
            self._load_data(tab_key); return
        
        records = self.session.query(info['model']).all()
        col_keys = list(info['model'].COLUMNS.values())
        count = 0
        
        for rec in records:
            row = []; match = False
            for attr in col_keys:
                value = getattr(rec, attr)
                if info['model'] == Presentation:
                    if attr == 'master_id': value = rec.master.name if rec.master else 'نامشخص'
                    elif attr == 'lesson_id': value = rec.lesson.name if rec.lesson else 'نامشخص'
                elif info['model'] == Selection:
                    if attr == 'student_id': value = rec.student.name if rec.student else 'نامشخص'
                    elif attr == 'presentation_id': value = rec.presentation.summary if rec.presentation else 'نامشخص'
                    elif attr == 'status': value = rec.get_status_text()
                str_val = str(value) if value is not None else ''
                row.append(str_val)
                if search.lower() in str_val.lower(): match = True
            
            if match:
                tree.insert("", "end", values=row, tags=('even' if count % 2 == 0 else 'odd',))
                count += 1
    
    def _on_row_select(self, tab_key):
        info = self.tabs[tab_key]
        sel = info['treeview'].focus()
        if not sel: return
        vals = info['treeview'].item(sel)['values']
        pk = vals[0]
        
        self._clear_form(tab_key)
        record = self.session.query(info['model']).get(pk)
        if not record: return
        
        for f in info['fields']:
            db_field, field_type = f[1], f[2] if len(f) > 2 else 'str'
            if db_field == 'major_filter':
                if hasattr(record, 'student') and record.student:
                    info['entries'][db_field].set(record.student.major)
                    self._filter_selection_combos()
                continue
            value = getattr(record, db_field, '')
            widget = info['entries'][db_field]
            if field_type.startswith('combo_fk') and value:
                fk_model = f[3]
                fk_record = self.session.query(fk_model).get(value)
                if fk_record:
                    display = fk_record.display_name if hasattr(fk_record, 'display_name') else getattr(fk_record, f[5], '')
                    widget.set(display)
            elif field_type.startswith('combo') and value:
                widget.set(str(value))
            elif value is not None and not field_type.startswith('combo'):
                widget.insert(0, str(value))
    
    def _filter_selection_combos(self):
        info = self.tabs['selection']
        major = info['entries']['major_filter'].get()
        
        for key in ['student_id', 'presentation_id']:
            widget = info['entries'][key]
            widget.set('')
        
        if major:
            students = self.session.query(Student).filter(Student.major == major).all()
            info['entries']['student_id']['values'] = sorted([s.name for s in students])
            
            presentations = self.session.query(Presentation).join(Lesson).filter(Lesson.major == major).all()
            info['entries']['presentation_id']['values'] = sorted([p.display_name for p in presentations])
    
    def _load_fk_combos(self, tab_key):
        for (t_key, db_field), widget in self.combo_fk_cache.items():
            if t_key != tab_key: continue
            for f in self.tabs[tab_key]['fields']:
                if f[1] == db_field and f[2] in ('combo_fk', 'combo_fk_filtered'):
                    fk_model = f[3]
                    name_field = f[5]
                    records = self.session.query(fk_model).all()
                    options = []
                    for r in records:
                        display = r.display_name if hasattr(r, 'display_name') else getattr(r, name_field, '')
                        options.append(display)
                    widget['values'] = sorted(options)
                    break
    
    def _refresh_tab(self, tab_key):
        self._load_data(tab_key)
        self._load_fk_combos(tab_key)
        self._update_status(f"{self.tabs[tab_key]['title']} بروزرسانی شد")
    
    # ==================== گزارش ====================
    def _build_report_tab(self):
        frame = ttk.Frame(self.tab_report)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        search_frame = ttk.LabelFrame(frame, text="🔍 محاسبه معدل", padding="15")
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="شناسه دانشجو:", font=self.font_normal).grid(row=0, column=0, padx=10, pady=5)
        self.rep_sid = ttk.Entry(search_frame, width=15, font=self.font_normal)
        self.rep_sid.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Button(search_frame, text="📊 محاسبه", command=self._calc_gpa, width=25).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="👥 لیست دانشجویان", command=self._show_student_list, width=25).grid(row=0, column=3, padx=5)
        
        result_frame = ttk.LabelFrame(frame, text="📈 نتیجه", padding="15")
        result_frame.pack(fill="both", expand=True, pady=10)
        
        self.lbl_info = ttk.Label(result_frame, text="---", font=self.font_title)
        self.lbl_info.pack(pady=5)
        self.lbl_gpa = ttk.Label(result_frame, text="---", font=('Arial', 22, 'bold'))
        self.lbl_gpa.pack(pady=5)
        self.lbl_rank = ttk.Label(result_frame, text="---", font=self.font_title)
        self.lbl_rank.pack(pady=5)
        
        self.details_tree = ttk.Treeview(result_frame, columns=("درس", "واحد", "نمره", "استاد", "وضعیت"), show="headings", height=8)
        for c in ("درس", "واحد", "نمره", "استاد", "وضعیت"):
            self.details_tree.heading(c, text=c, anchor='center')
            self.details_tree.column(c, width=110, anchor='center')
        self.details_tree.pack(fill="x", pady=10)
    
    def _calc_gpa(self):
        sid = self.rep_sid.get().strip()
        self._clear_report()
        if not sid.isdigit(): messagebox.showwarning("هشدار", "شناسه معتبر نیست"); return
        
        student = self.session.query(Student).get(int(sid))
        if not student: messagebox.showerror("خطا", "دانشجو یافت نشد"); return
        
        self.lbl_info.config(text=f"👤 {student.name} | رشته: {student.major}")
        
        selections = self.session.query(Selection).filter(Selection.student_id == student.id, Selection.score != None).all()
        if not selections: self.lbl_gpa.config(text="نمره‌ای ثبت نشده", foreground="gray"); return
        
        total_w, total_u = 0, 0
        for s in selections:
            lesson = s.presentation.lesson if s.presentation else None
            master = s.presentation.master if s.presentation else None
            name = lesson.name if lesson else 'نامشخص'
            unit = lesson.unit if lesson else 0
            mname = master.name if master else 'نامشخص'
            status = "✅ قبول" if s.score >= 10 else "❌ مردود"
            total_w += s.score * unit; total_u += unit
            self.details_tree.insert("", "end", values=(name, unit, f"{s.score:.1f}", mname, status))
        
        if total_u > 0:
            gpa = total_w / total_u
            rank = GradeLevel.get_rank(gpa)
            self.lbl_gpa.config(text=f"معدل: {gpa:.2f}", foreground="#2c3e50")
            self.lbl_rank.config(text=f"رتبه: {rank.value[0]}", foreground=rank.value[3])
    
    def _show_student_list(self):
        win = tk.Toplevel(self.root); win.title("لیست دانشجویان"); win.geometry("550x450"); win.configure(bg='#e8ecf1')
        
        search_frame = tk.Frame(win, bg='#e8ecf1'); search_frame.pack(fill='x', padx=10, pady=10)
        tk.Label(search_frame, text="🔍 جستجو:", font=self.font_normal, bg='#e8ecf1').pack(side='right', padx=5)
        search_entry = ttk.Entry(search_frame, font=self.font_normal, width=25)
        search_entry.pack(side='right', padx=5)
        
        tree = ttk.Treeview(win, columns=("شناسه", "نام", "کد", "رشته"), show="headings")
        for c in ("شناسه", "نام", "کد", "رشته"): tree.heading(c, text=c, anchor='center'); tree.column(c, width=100, anchor='center')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        def load(filter_text=""):
            for item in tree.get_children(): tree.delete(item)
            query = self.session.query(Student)
            if filter_text: query = query.filter((Student.name.contains(filter_text)) | (Student.student_code.contains(filter_text)) | (Student.major.contains(filter_text)))
            for s in query.order_by(Student.name).all():
                tree.insert("", "end", values=(s.id, s.name, s.student_code or '-', s.major))
        
        load()
        search_entry.bind('<KeyRelease>', lambda e: load(search_entry.get()))
        
        def select():
            sel = tree.focus()
            if sel: self.rep_sid.delete(0, tk.END); self.rep_sid.insert(0, str(tree.item(sel)['values'][0])); win.destroy(); self._calc_gpa()
        
        ttk.Button(win, text="✅ انتخاب و محاسبه", command=select).pack(pady=10)
    
    def _clear_report(self):
        self.lbl_info.config(text="---"); self.lbl_gpa.config(text="---", foreground="black"); self.lbl_rank.config(text="---", foreground="black")
        for item in self.details_tree.get_children(): self.details_tree.delete(item)
    
    # ==================== سایر ====================
    def _create_statusbar(self):
        bar = tk.Frame(self.root, bg='#1a1a2e', height=28)
        bar.pack(side='bottom', fill='x'); bar.pack_propagate(False)
        self.status_label = tk.Label(bar, text="  ✓ آماده", fg='#8b949e', bg='#1a1a2e', font=self.font_small, anchor='w')
        self.status_label.pack(side='left', fill='both', expand=True)
        tk.Label(bar, text=f"ارائه شده توسط {COMPANY}  ", fg='#e94560', bg='#1a1a2e', font=self.font_small).pack(side='right', padx=10)
    
    def _update_status(self, msg): self.status_label.config(text=f"  ✓ {msg}")
    
    def _on_tab_change(self, event):
        idx = self.notebook.index(self.notebook.select())
        keys = list(self.tabs.keys())
        if idx < len(keys): self._refresh_tab(keys[idx])
    
    def _safe_exit(self):
        if messagebox.askyesno("خروج", "آیا مطمئن هستید؟"): self.session.close(); self.root.destroy()

# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    try: root.iconbitmap('acadflow.ico')
    except: pass
    root.configure(bg="#f0f2f5")
    app = AcadFlowApp(root)
    root.mainloop()