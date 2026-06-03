# tabs/report_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import get_session
from models import Student, Selection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import pandas as pd
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ReportTab:
    def __init__(self, parent, user, main_window):
        self.parent = parent
        self.user = user
        self.main_window = main_window
        self.frame = ttk.Frame(self.parent)
        self.parent.add(self.frame, text="📈 گزارش")
        self.current_student = None
        try:
            self.font = ('B Nazanin', 11)
            self.font_bold = ('B Nazanin', 11, 'bold')
            self.font_title = ('B Nazanin', 14, 'bold')
            self.font_big = ('B Nazanin', 20, 'bold')
        except:
            self.font = ('Tahoma', 10)
            self.font_bold = ('Tahoma', 10, 'bold')
            self.font_title = ('Tahoma', 13, 'bold')
            self.font_big = ('Tahoma', 18, 'bold')
        self._build()
    
    def _build(self):
        search_frame = ttk.LabelFrame(self.frame, text="🔍 محاسبه معدل", padding="15")
        search_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(search_frame, text="شناسه دانشجو:", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_id = ttk.Entry(search_frame, width=12, font=self.font)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="🧮محاسبه", command=self._calc_gpa, width=15).grid(row=0, column=2, padx=3)
        ttk.Button(search_frame, text="👨‍🎓لیست کلی", command=self._show_list, width=15).grid(row=0, column=3, padx=3)
        ttk.Button(search_frame, text="📕PDF", command=self._export_pdf, width=15).grid(row=0, column=4, padx=3)
        ttk.Button(search_frame, text="📊Excel", command=self._export_excel, width=15).grid(row=0, column=5, padx=3)
        
        result_frame = ttk.LabelFrame(self.frame, text="📈 نتیجه", padding="15")
        result_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.lbl_info = ttk.Label(result_frame, text="", font=self.font_title)
        self.lbl_info.pack(pady=3)
        self.lbl_gpa = ttk.Label(result_frame, text="", font=self.font_big)
        self.lbl_gpa.pack(pady=3)
        self.lbl_rank = ttk.Label(result_frame, text="", font=self.font_bold)
        self.lbl_rank.pack(pady=3)
        
        columns = ("درس", "واحد", "نمره", "استاد", "وضعیت")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(fill='both', expand=True)
    
    def _calc_gpa(self):
        sid = self.entry_id.get().strip()
        self._clear()
        if not sid.isdigit():
            messagebox.showwarning("هشدار", "شناسه معتبر وارد کنید")
            return
        
        session = get_session()
        try:
            student = session.query(Student).get(int(sid))
            if not student:
                messagebox.showerror("خطا", "دانشجو یافت نشد")
                return
            self.current_student = student
            self.lbl_info.config(text=f"👤 {student.name} | رشته: {student.major}")
            
            selections = session.query(Selection).filter(
                Selection.student_id == student.id, Selection.score != None
            ).all()
            
            if not selections:
                self.lbl_gpa.config(text="نمره‌ای ثبت نشده", foreground="gray")
                return
            
            total_w = 0
            total_u = 0
            for s in selections:
                lesson = s.presentation.lesson if s.presentation else None
                master = s.presentation.master if s.presentation else None
                name = lesson.name if lesson else 'نامشخص'
                unit = lesson.unit if lesson else 0
                mname = master.name if master else 'نامشخص'
                status = "✅ قبول" if s.score >= 10 else "❌ مردود"
                total_w += s.score * unit
                total_u += unit
                self.tree.insert("", "end", values=(name, unit, f"{s.score:.1f}", mname, status))
            
            if total_u > 0:
                gpa = total_w / total_u
                if gpa < 9: rank, color = "ضعیف", "red"
                elif gpa < 15: rank, color = "متوسط", "orange"
                else: rank, color = "عالی", "green"
                self.lbl_gpa.config(text=f"معدل: {gpa:.2f}", foreground="#2c3e50")
                self.lbl_rank.config(text=f"رتبه: {rank}", foreground=color)
        finally:
            session.close()
    
    def _export_pdf(self):
        if not self.current_student:
            messagebox.showwarning("هشدار", "ابتدا معدل را محاسبه کنید")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        
        try:
            import os
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            def fa(text):
                if not text:
                    return ""
                reshaped = arabic_reshaper.reshape(str(text))
                return get_display(reshaped)
            
            student = self.current_student
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            w, h = A4
            right = w - 40  # حاشیه راست
            
            font_path = "C:/Windows/Fonts/AP_Yekan__TrueType_.ttf"
            
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Yekan', font_path))
                
                # === راست‌چین: همه از right کم میشن ===
                
                c.setFont('Yekan', 18)
                title = fa("AcadFlow - کارنامه دانشجو")
                c.drawRightString(right, h - 45, title)
                
                c.setFont('Yekan', 13)
                c.drawRightString(right, h - 80, fa(f"نام: {student.name}"))
                c.drawRightString(right, h - 110, fa(f"رشته: {student.major}"))
                c.drawRightString(right, h - 140, fa(f"کد دانشجویی: {student.student_code or '-'}"))
                
                # جدول راست‌چین
                data = [[fa('وضعیت'), fa('نمره'), fa('واحد'), fa('درس'), fa('ردیف')]]
                for i, item in enumerate(self.tree.get_children(), 1):
                    vals = list(self.tree.item(item)['values'])
                    data.append([fa(vals[4]), fa(vals[2]), fa(vals[1]), fa(vals[0]), fa(str(i))])
                
                col_widths = [70, 50, 50, 200, 40]
                table_width = sum(col_widths)
                table_x = right - table_width  # جدول از راست شروع بشه
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 0), (-1, -1), 'Yekan'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))
                
                table_y = h - 190 - len(data) * 22
                table.wrapOn(c, table_width, table_y)
                table.drawOn(c, table_x, table_y)
                
                # معدل راست‌چین
                y = table_y - 50
                c.setFont('Yekan', 16)
                gpa_text = self.lbl_gpa.cget("text") if self.lbl_gpa.cget("text") else ""
                rank_text = self.lbl_rank.cget("text") if self.lbl_rank.cget("text") else ""
                c.drawRightString(right, y, fa(gpa_text))
                c.drawRightString(right, y - 35, fa(rank_text))
            
            else:
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, h - 40, "AcadFlow - Student Report")
                c.setFont("Helvetica", 11)
                c.drawString(40, h - 70, f"Name: {student.name}")
                c.drawString(40, h - 90, f"Major: {student.major}")
                
                data = [['#', 'Lesson', 'Unit', 'Score', 'Status']]
                for i, item in enumerate(self.tree.get_children(), 1):
                    vals = list(self.tree.item(item)['values'])
                    data.append([str(i)] + vals[:3] + [vals[4]])
                
                table = Table(data, colWidths=[40, 200, 50, 50, 70])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                table.wrapOn(c, w - 80, h)
                table.drawOn(c, 40, h - 130 - len(data) * 20)
            
            c.save()
            messagebox.showinfo("موفق", f"PDF ذخیره شد:\n{file_path}")
        except Exception as e:
            messagebox.showerror("خطا", str(e))
    
    def _export_excel(self):
        if not self.tree.get_children():
            messagebox.showwarning("هشدار", "داده‌ای برای خروجی نیست")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path: return
        try:
            columns = ["درس", "واحد", "نمره", "استاد", "وضعیت"]
            data = [self.tree.item(item)['values'] for item in self.tree.get_children()]
            pd.DataFrame(data, columns=columns).to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("موفق", f"Excel saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _show_list(self):
        win = tk.Toplevel(self.frame)
        win.title("لیست دانشجویان")
        win.geometry("550x450")
        win.configure(bg='#e8ecf1')
        
        # Search bar
        search_frame = tk.Frame(win, bg='#e8ecf1')
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍 جستجو:", font=self.font, bg='#e8ecf1').pack(side='right', padx=5)
        search_entry = ttk.Entry(search_frame, font=self.font, width=25)
        search_entry.pack(side='right', padx=5)
        
        # Tree
        tree = ttk.Treeview(win, columns=("شناسه", "نام", "کد", "رشته"), show="headings")
        tree.heading("شناسه", text="شناسه")
        tree.heading("نام", text="نام")
        tree.heading("کد", text="کد دانشجویی")
        tree.heading("رشته", text="رشته")
        tree.column("شناسه", width=60, anchor='center')
        tree.column("نام", width=180, anchor='center')
        tree.column("کد", width=100, anchor='center')
        tree.column("رشته", width=120, anchor='center')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        def load_students(filter_text=""):
            for item in tree.get_children():
                tree.delete(item)
            session = get_session()
            try:
                query = session.query(Student)
                if filter_text:
                    query = query.filter(
                        (Student.name.contains(filter_text)) |
                        (Student.student_code.contains(filter_text)) |
                        (Student.major.contains(filter_text))
                    )
                for s in query.order_by(Student.name).all():
                    tree.insert("", "end", values=(s.id, s.name, s.student_code or '-', s.major))
            finally:
                session.close()
        
        load_students()
        search_entry.bind('<KeyRelease>', lambda e: load_students(search_entry.get()))
        
        def select():
            sel = tree.focus()
            if sel:
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, str(tree.item(sel)['values'][0]))
                win.destroy()
                self._calc_gpa()
        
        ttk.Button(win, text="✅ انتخاب و محاسبه", command=select).pack(pady=10)
    
    def _clear(self):
        self.lbl_info.config(text="")
        self.lbl_gpa.config(text="", foreground="black")
        self.lbl_rank.config(text="", foreground="black")
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def refresh_data(self):
        self._clear()
        self.entry_id.delete(0, tk.END)