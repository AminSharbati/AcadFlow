# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)
    security_question = Column(String(200))
    security_answer_hash = Column(String(256))
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    user = relationship("User", back_populates="audit_logs")

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    student_code = Column(String(20), unique=True)
    national_code = Column(String(10), unique=True)
    entrance_term = Column(String(10))
    graduation = Column(String(50))
    mobile = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    major = Column(String(50), nullable=False)
    selections = relationship("Selection", back_populates="student", cascade="all, delete-orphan")
    COLUMNS = {"شناسه": "id", "نام دانشجو": "name", "کد دانشجویی": "student_code", "کد ملی": "national_code",
               "ترم ورود": "entrance_term", "مقطع": "graduation", "موبایل": "mobile", "ایمیل": "email", "رشته": "major"}

class Master(Base):
    __tablename__ = 'masters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    national_code = Column(String(10), unique=True)
    degree = Column(String(50))
    department = Column(String(50))
    mobile = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    presentations = relationship("Presentation", back_populates="master", cascade="all, delete-orphan")
    COLUMNS = {"شناسه": "id", "نام استاد": "name", "کد ملی": "national_code", "مدرک": "degree",
               "گروه": "department", "موبایل": "mobile", "ایمیل": "email"}

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    unit = Column(Integer, nullable=False)
    major = Column(String(50), nullable=False)
    description = Column(String(500))
    prerequisite_id = Column(Integer, ForeignKey('lessons.id'), nullable=True)
    max_capacity = Column(Integer, default=50)
    presentations = relationship("Presentation", back_populates="lesson")
    prerequisite = relationship("Lesson", remote_side=[id], backref="required_for")
    COLUMNS = {"شناسه": "id", "نام درس": "name", "تعداد واحد": "unit", "رشته": "major", "ظرفیت": "max_capacity", "توضیحات": "description"}

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
    COLUMNS = {"شناسه": "id", "استاد": "master_id", "درس": "lesson_id", "روز": "day_hold",
               "شروع": "start_time", "پایان": "finish_time", "ظرفیت": "capacity", "ثبت‌نامی": "enrolled"}
    def get_display_name(self):
        m = self.master.name if self.master else 'نامشخص'
        l = self.lesson.name if self.lesson else 'نامشخص'
        return f"{l} ({m}، {self.day_hold})"
    def get_summary(self):
        if self.lesson and self.master: return f"{self.lesson.name} ({self.master.name})"
        return 'نامشخص'
    @property
    def available_seats(self): return self.capacity - self.enrolled

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
    COLUMNS = {"شناسه": "id", "دانشجو": "student_id", "درس ارائه شده": "presentation_id",
               "نمره": "score", "سال": "year_education", "وضعیت": "status"}
    def get_status_text(self):
        if self.score is None: return "ثبت نشده"
        return "✅ قبول" if self.score >= 10 else "❌ مردود"