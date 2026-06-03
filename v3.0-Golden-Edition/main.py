# main.py
from database import init_database
from auth import AuthManager
from login_window import LoginWindow
from main_window import MainWindow

def main():
    print("=" * 50)
    print("  AcadFlow v2.0")
    print("=" * 50)
    print("[1/3] Initializing database..."); init_database()
    print("[2/3] Creating default users..."); AuthManager.create_default_users()
    print("[3/3] Starting login...")
    login = LoginWindow(); user_data = login.run()
    if not user_data: print("User exited."); return
    print(f"Welcome! User ID: {user_data['id']}")
    app = MainWindow(user_data); app.run()

if __name__ == "__main__": main()