# auth.py
import bcrypt, datetime
from database import get_session
from models import User, AuditLog
from config import MAX_LOGIN_ATTEMPTS

class AuthManager:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_default_users():
        session = get_session()
        try:
            if not session.query(User).filter(User.username == 'admin').first():
                admin = User(username='admin', full_name='مدیر سیستم', email='admin@acadflow.com',
                            role='admin', security_question='کد ملی شما چیست؟')
                admin.password_hash = AuthManager.hash_password('admin123')
                admin.security_answer_hash = AuthManager.hash_password('1234567890')
                session.add(admin)
                
                manager = User(username='manager', full_name='مدیر آموزش', email='manager@acadflow.com',
                              role='manager', security_question='کد ملی شما چیست؟')
                manager.password_hash = AuthManager.hash_password('manager123')
                manager.security_answer_hash = AuthManager.hash_password('1234567890')
                session.add(manager)
                session.commit()
        except: session.rollback()
        finally: session.close()
    
    @staticmethod
    def create_user_from_person(full_name, email, national_code, role):
        session = get_session()
        try:
            if session.query(User).filter(User.username == email).first():
                return None, "کاربری با این ایمیل قبلاً ثبت شده"
            user = User(username=email, full_name=full_name, role=role, security_question='کد ملی شما چیست؟')
            user.password_hash = AuthManager.hash_password(national_code)
            user.security_answer_hash = AuthManager.hash_password(national_code)
            session.add(user); session.commit()
            return user, "کاربر ساخته شد"
        except Exception as e: session.rollback(); return None, str(e)
        finally: session.close()
    
    @staticmethod
    def login(username, password):
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user: return None, "نام کاربری یافت نشد"
            if not user.is_active: return None, "حساب غیرفعال است"
            if AuthManager.verify_password(password, user.password_hash):
                user.login_attempts = 0; user.last_login = datetime.datetime.now()
                session.add(AuditLog(user_id=user.id, action="ورود موفق")); session.commit()
                return {'id': user.id, 'username': user.username, 'full_name': user.full_name,
                        'role': user.role, 'email': user.email}, "ورود موفق"
            else:
                user.login_attempts += 1
                if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.is_active = False; session.commit()
                    return None, "حساب به دلیل ۵ تلاش ناموفق قفل شد"
                session.commit()
                return None, f"رمز اشتباه. {MAX_LOGIN_ATTEMPTS - user.login_attempts} تلاش باقی مانده"
        finally: session.close()
    
    @staticmethod
    def recover_password(username, security_answer):
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user: return None, "کاربر یافت نشد"
            if not user.security_answer_hash: return None, "سوال امنیتی ثبت نشده"
            if AuthManager.verify_password(security_answer, user.security_answer_hash):
                new_password = user.username[-4:] + "1234"
                user.password_hash = AuthManager.hash_password(new_password)
                user.login_attempts = 0; user.is_active = True
                session.commit()
                return new_password, "رمز بازنشانی شد"
            return None, "پاسخ اشتباه است"
        finally: session.close()
    
    @staticmethod
    def get_all_users():
        session = get_session()
        try: return session.query(User).order_by(User.created_at.desc()).all()
        finally: session.close()
    
    @staticmethod
    def toggle_user_status(user_id):
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            if user and user.username != 'admin':
                user.is_active = not user.is_active; user.login_attempts = 0
                session.commit(); return True, "وضعیت تغییر کرد"
            return False, "نمی‌توان ادمین را تغییر داد"
        except: session.rollback(); return False, "خطا"
        finally: session.close()
    
    @staticmethod
    def delete_user(user_id):
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            if user and user.username != 'admin': session.delete(user); session.commit(); return True, "کاربر حذف شد"
            return False, "نمی‌توان ادمین را حذف کرد"
        except: session.rollback(); return False, "خطا"
        finally: session.close()
    
    @staticmethod
    def update_user(user_id, full_name=None, email=None, role=None, password=None):
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            if not user: return False, "کاربر یافت نشد"
            if user.username == 'admin' and role and role != 'admin':
                return False, "نمی‌توان نقش ادمین را تغییر داد"
            
            if full_name: user.full_name = full_name
            if email is not None: user.email = email
            if role: user.role = role
            if password: user.password_hash = AuthManager.hash_password(password)
            
            session.commit()
            return True, "کاربر با موفقیت بروزرسانی شد"
        except Exception as e:
            session.rollback(); return False, str(e)
        finally: session.close()
    
    @staticmethod
    def add_audit_log(user_id, action):
        session = get_session()
        try: session.add(AuditLog(user_id=user_id, action=action)); session.commit()
        except: session.rollback()
        finally: session.close()
    
    @staticmethod
    def get_user_role_name(role_code):
        return {'admin': 'ادمین کل', 'manager': 'مدیر آموزش', 'professor': 'استاد', 'student': 'دانشجو'}.get(role_code, role_code)
    
    @staticmethod
    def can_user_manage(user_role): return user_role in ['admin', 'manager']
    @staticmethod
    def can_user_grade(user_role): return user_role in ['admin', 'manager', 'professor']
    @staticmethod
    def can_user_view_all(user_role): return user_role in ['admin', 'manager']
    @staticmethod
    def is_admin(user_role): return user_role == 'admin'