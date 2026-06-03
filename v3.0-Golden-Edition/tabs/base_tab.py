# tabs/base_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from database import get_session
from auth import AuthManager

class BaseTab:
    def __init__(self, parent, user, main_window, title, model, permission='view'):
        self.parent = parent; self.user = user; self.main_window = main_window
        self.title = title; self.model = model; self.permission = permission
        self.entries = {}; self.combo_cache = {}; self.fields_config = []; self.input_frame = None
        self.frame = ttk.Frame(self.parent); self.parent.add(self.frame, text=title)
        try: self.font = ('B Nazanin', 11); self.font_bold = ('B Nazanin', 11, 'bold')
        except: self.font = ('Tahoma', 10); self.font_bold = ('Tahoma', 10, 'bold')
    
    def _has_permission(self, action):
        role = self.user['role']
        if role == 'admin': return True
        if self.permission == 'view': return True
        if self.permission == 'manage' and role in ['admin', 'manager']: return True
        if self.permission == 'grade' and role in ['admin', 'manager', 'professor']: return True
        return False
    
    def setup_ui(self, fields_config):
        self.fields_config = fields_config
        can_manage = self._has_permission('manage') or self._has_permission('grade')
        
        if can_manage:
            self.input_frame = ttk.LabelFrame(self.frame, text=f"📝 فرم {self.title}", padding="15")
            self.input_frame.pack(fill='x', padx=10, pady=10)
            for i, field in enumerate(fields_config):
                label, db_field = field[0], field[1]; field_type = field[2] if len(field) > 2 else 'str'
                row, col = i // 3, (i % 3) * 2
                ttk.Label(self.input_frame, text=f"{label}:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
                if field_type.startswith('combo'):
                    widget = ttk.Combobox(self.input_frame, width=20, state='readonly', font=self.font)
                    if field_type == 'combo': widget['values'] = field[3] if len(field) > 3 else []
                    elif field_type == 'combo_major':
                        from config import MAJORS; widget['values'] = MAJORS
                        widget.bind('<<ComboboxSelected>>', self._on_major_filter)
                    elif field_type in ('combo_fk', 'combo_fk_filtered'):
                        self.combo_cache[db_field] = {'widget': widget, 'model': field[3], 'name_field': field[4]}
                else: widget = ttk.Entry(self.input_frame, width=22, font=self.font)
                widget.grid(row=row, column=col+1, padx=5, pady=5, sticky='ew')
                self.entries[db_field] = widget
            
            btn_row = (len(fields_config) // 3) + 1
            btn_frame = ttk.Frame(self.input_frame)
            btn_frame.grid(row=btn_row, column=0, columnspan=6, pady=15)
            ttk.Button(btn_frame, text="✔افزودن", command=self.add_record, width=15).pack(side='left', padx=4)
            ttk.Button(btn_frame, text="✏ویرایش", command=self.update_record, width=15).pack(side='left', padx=4)
            ttk.Button(btn_frame, text="❌حذف", command=self.delete_record, width=15).pack(side='left', padx=4)
            ttk.Button(btn_frame, text="🔁تازه سازی", command=self.refresh_data, width=15).pack(side='left', padx=4)
        else:
            info_frame = ttk.Frame(self.frame); info_frame.pack(fill='x', padx=10, pady=10)
            ttk.Label(info_frame, text="ⓘ شما دسترسی فقط نمایش دارید", font=self.font, foreground='#e67e22').pack(side='right', padx=5)
            ttk.Button(info_frame, text="🔁تازه سازی", command=self.refresh_data, width=10).pack(side='left', padx=4)
        
        # ========== TABLE + SEARCH ==========
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Search bar
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(search_frame, text="🔍 جستجو:", font=self.font).pack(side='right', padx=5)
        self.search_entry = ttk.Entry(search_frame, font=self.font, width=25)
        self.search_entry.pack(side='right', padx=5)
        self.search_entry.bind('<KeyRelease>', self._filter_data)
        
        # Tree container
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill='both', expand=True)
        
        columns = list(self.model.COLUMNS.keys())
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', selectmode='browse', height=15)
        for col in columns: self.tree.heading(col, text=col, anchor='center'); self.tree.column(col, anchor='center', width=100, minwidth=80)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.ctx_menu = Menu(self.frame, tearoff=0, font=self.font)
        self.ctx_menu.add_command(label="🔁تازه سازی", command=self.refresh_data)
        if can_manage: self.ctx_menu.add_command(label="حذف", command=self.delete_record)
        self.tree.bind("<Button-3>", lambda e: self.ctx_menu.tk_popup(e.x_root, e.y_root))
        self.tree.tag_configure('even', background='#f8f9fa'); self.tree.tag_configure('odd', background='white')
    
    def _on_major_filter(self, event=None): pass
    
    def _on_select(self, event):
        if not self._has_permission('manage') and not self._has_permission('grade'): return
        if not self.input_frame: return
        selected = self.tree.focus()
        if not selected: return
        pk = self.tree.item(selected)['values'][0]
        session = get_session()
        try:
            record = session.query(self.model).get(pk)
            if record: self._clear_form(); self._fill_form(record, session)
        finally: session.close()
    
    def _clear_form(self):
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox): w.set('')
            else: w.delete(0, tk.END)
    
    def _fill_form(self, record, session):
        for field in self.fields_config:
            db_field, field_type = field[1], field[2] if len(field) > 2 else 'str'
            if db_field == 'major_filter': continue
            value, widget = getattr(record, db_field, ''), self.entries.get(db_field)
            if not widget: continue
            if field_type.startswith('combo_fk') and value:
                fk_record = session.query(field[3]).get(value)
                if fk_record: widget.set(self._get_display(fk_record))
            elif field_type.startswith('combo') and value: widget.set(str(value))
            elif value is not None: widget.insert(0, str(value))
    
    def _get_display(self, record):
        if hasattr(record, 'get_display_name'): return record.get_display_name()
        return getattr(record, 'name', str(record))
    
    def _get_form_data(self):
        data = {}
        for field in self.fields_config:
            label, db_field, field_type = field[0], field[1], field[2] if len(field) > 2 else 'str'
            if db_field == 'major_filter': continue
            widget = self.entries.get(db_field)
            if not widget: continue
            value = widget.get().strip()
            is_optional = 'optional' in field_type
            if not is_optional and not value: raise ValueError(f"فیلد '{label}' اجباری است")
            if not value and is_optional: data[db_field] = None; continue
            if field_type.startswith('combo_fk'):
                cache_info = self.combo_cache.get(db_field)
                if cache_info:
                    session = get_session()
                    try:
                        found = None
                        for r in session.query(cache_info['model']).all():
                            if self._get_display(r) == value: found = r.id; break
                        if found is None: raise ValueError(f"'{value}' معتبر نیست")
                        data[db_field] = found
                    finally: session.close()
            elif 'int' in field_type:
                try: data[db_field] = int(value)
                except: raise ValueError(f"'{label}' باید عدد باشد")
            elif 'float' in field_type:
                try: data[db_field] = float(value)
                except: raise ValueError(f"'{label}' باید عدد باشد")
            else: data[db_field] = value
        return data
    
    def add_record(self):
        if not self._has_permission('manage') and not self._has_permission('grade'):
            messagebox.showwarning("عدم دسترسی", "شما اجازه افزودن ندارید"); return
        try:
            data = self._get_form_data()
            session = get_session()
            try: record = self.model(**data); session.add(record); session.commit(); self._clear_form(); self.refresh_data(); messagebox.showinfo("موفق", "رکورد افزوده شد")
            except: session.rollback(); raise
            finally: session.close()
        except ValueError as e: messagebox.showerror("خطا", str(e))
        except Exception as e: messagebox.showerror("خطا", str(e))
    
    def update_record(self):
        if not self._has_permission('manage') and not self._has_permission('grade'):
            messagebox.showwarning("عدم دسترسی", "شما اجازه ویرایش ندارید"); return
        selected = self.tree.focus()
        if not selected: messagebox.showwarning("هشدار", "رکوردی انتخاب نشده"); return
        try:
            pk, data = self.tree.item(selected)['values'][0], self._get_form_data()
            session = get_session()
            try:
                record = session.query(self.model).get(pk)
                if record:
                    for k, v in data.items(): setattr(record, k, v)
                    session.commit(); self._clear_form(); self.refresh_data(); messagebox.showinfo("موفق", "رکورد ویرایش شد")
            except: session.rollback(); raise
            finally: session.close()
        except ValueError as e: messagebox.showerror("خطا", str(e))
        except Exception as e: messagebox.showerror("خطا", str(e))
    
    def delete_record(self):
        if not self._has_permission('manage'):
            messagebox.showwarning("عدم دسترسی", "شما اجازه حذف ندارید"); return
        selected = self.tree.focus()
        if not selected: messagebox.showwarning("هشدار", "رکوردی انتخاب نشده"); return
        if not messagebox.askyesno("تأیید", "آیا از حذف اطمینان دارید؟"): return
        try:
            pk = self.tree.item(selected)['values'][0]
            session = get_session()
            try:
                record = session.query(self.model).get(pk)
                if record: session.delete(record); session.commit(); self._clear_form(); self.refresh_data(); messagebox.showinfo("موفق", "رکورد حذف شد")
            except: session.rollback(); messagebox.showerror("خطا", "رکورد وابستگی دارد")
            finally: session.close()
        except Exception as e: messagebox.showerror("خطا", str(e))
    
    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        session = get_session()
        try:
            records = session.query(self.model).all()
            col_keys = list(self.model.COLUMNS.values())
            for i, rec in enumerate(records):
                row = [self._format_value(rec, attr, getattr(rec, attr, '')) or '' for attr in col_keys]
                self.tree.insert("", "end", values=row, tags=('even' if i % 2 == 0 else 'odd',))
        finally: session.close()
    
    def _format_value(self, record, attr, value): return value
    
    def _filter_data(self, event=None):
        search_text = self.search_entry.get().strip()
        for item in self.tree.get_children(): self.tree.delete(item)
        session = get_session()
        try:
            records = session.query(self.model).all()
            col_keys = list(self.model.COLUMNS.values())
            count = 0
            for rec in records:
                row = []; match = False
                for attr in col_keys:
                    value = self._format_value(rec, attr, getattr(rec, attr, ''))
                    str_value = str(value) if value is not None else ''
                    row.append(str_value)
                    if search_text and search_text.lower() in str_value.lower(): match = True
                if not search_text or match:
                    self.tree.insert("", "end", values=row, tags=('even' if count % 2 == 0 else 'odd',))
                    count += 1
        finally: session.close()
    
    def load_foreign_keys(self):
        if not self._has_permission('manage') and not self._has_permission('grade'): return
        for db_field, cache_info in self.combo_cache.items():
            widget, current = cache_info['widget'], cache_info['widget'].get()
            session = get_session()
            try:
                options = [self._get_display(r) for r in session.query(cache_info['model']).all()]
                widget['values'] = sorted(options)
                if current in options: widget.set(current)
            finally: session.close()
    
    def refresh_data(self): self.load_data(); self.load_foreign_keys()