#GUI file for the end of module assignment (Travel Agent Record Management System). 

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date as date_cls
from tkcalendar import DateEntry

from storage import (
    RecordStore,
    DATA_FILE,
    DATE_FORMAT,
    TYPE_CLIENT,
    TYPE_AIRLINE,
    TYPE_FLIGHT,
    CLIENT_FIELDS,
    CLIENT_COLUMNS,
    AIRLINE_FIELDS,
    AIRLINE_COLUMNS,
    FLIGHT_FIELDS,
    FLIGHT_COLUMNS,
)

class RecordTab(tk.Frame):
    record_type = None
    fields = []
    columns = []

    def __init__(self, parent, store: RecordStore, app):
        super().__init__(parent)
        self.store = store
        self.app = app
        self.entries = {}          # key -> widget
        self.selected_id = None    # ID currently loaded in the form
        self.search_var = tk.StringVar()
        self._build_ui()
        self.refresh_tree()
 

    def _build_ui(self):
        #creating a cusotmized form 
        form = ttk.LabelFrame(self, text=f"{self.record_type} details", padding=10)
        form.pack(side=tk.TOP, fill=tk.X)

        for row, (key, lable, widget) in enumerate(self.fields):
            ttk.Label(form, text=lable + ":").grid(row=row, column=0, sticky="e", padx=4, pady=3)
            if widget == "combobox":
                var = tk.StringVar()
                cb = ttk.Combobox(form, textvariable=var, state="readonly", width=35)
                cb.grid(row=row, column=1, sticky="w", padx=4, pady=3)
                self.entries[key] = cb

            else: 
                 var = tk.StringVar()
                 ent = ttk.Entry(form, textvariable=var, width=38)
                 ent.grid(row=row, column=1, sticky="w", padx=4, pady=3)
                 self.entries[key] = ent

        #ID display label 
        self.id_label_var = tk.StringVar(value="New record (no ID yet)")
        ttk.Label(form, textvariable=self.id_label_var, foreground="#555").grid(
            row=len(self.fields), column=0, columnspan=2, sticky="w", padx=4, pady=(6, 0))

        #Creating buttons for the form
        btns = ttk.Frame(self)
        btns.pack(side=tk.TOP, fill=tk.X, pady=8)
        ttk.Button(btns, text="New / Clear", command=self.on_clear).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Create Record", command=self.on_create).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Update Selected", command=self.on_update).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Delete Selected", command=self.on_delete).pack(side=tk.LEFT, padx=3)

        # Search fields
        search_frame = ttk.LabelFrame(self, text="Search", padding=8)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=4)
        ttk.Button(search_frame, text="Search", command=self.on_search).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_frame, text="Show All", command=self.refresh_tree).pack(side=tk.LEFT, padx=3)

        #treeview for displaying records
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(8,0))

        col_ids = [col[0] for col in self.columns]
        self.tree = ttk.Treeview(tree_frame, columns=col_ids, show="headings", height=10)
        for key, heading, width in self.columns:
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=width, anchor="w")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    #Form widgets
    def get_form_values(self):
        values = {}
        for key, label, widget in self.fields:
            w = self.entries[key]
            if widget == "combobox":
                text = w.get()
                choices = self.combobox_choices(key)
                values[key] = choices.get(text, None)  # store the internal value
            elif widget == "datetime":
                values[key] = w.get_date()  # store as date object
            else:
                values[key] = w.get().strip()
        return values

    def set_form_values(self, record):
        for key, label, widget in self.fields:
            w = self.entries[key]
            if widget == "combobox":
                choices = self.combobox_choices(key) 
                target_id = record.get(key)
                display = ""
                for disp, rid in choices.items():
                    if rid == target_id:
                        display = disp
                        break
                w.set(display)
            elif widget == "datetime":
                value = record.get(key)
                if value:
                    w.set_date(value)
            else:
                w.delete(0, tk.END)
                w.insert(0, record.get(key, ""))

    def clear_form(self):
        for key, label, widget in self.fields:
            w = self.entries[key]
            if widget == "combobox":
                w.set("")
            elif widget == "datetime":
                w.delete(0, tk.END)
            else:
                w.delete(0, tk.END)
        self.selected_id = None
        self.id_label_var.set("New record (no ID yet)")
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def combobox_choices(self, key):
        return {}

    def display_value(self, record, key):
        return record.get(key, "")

    def validate(self, values: dict):
        for key, label, widget in self.fields:
            if not str(values.get(key, "")).strip() and key not in ("Address2", "Address3"):
                return False, f"{label} is required."
        return True, ""

    def before_save(self, values: dict):
        return values

    def refresh_related(self):
        pass

    def on_clear(self):
        self.clear_form()

    def on_search(self):
        filter_text = self.search_var.get().strip()
        self.refresh_tree(filter_text if filter_text else None)

    def on_create(self):
        values = self.get_form_values()
        ok, msg = self.validate(values)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return
        values = self.before_save(values)
        if values is None:
            return
        values["Type"] = self.record_type
        new_rec = self.store.create_record(values)
        self.app.save_and_notify(f"{self.record_type} record created with ID {new_rec['ID']}.")
        self.clear_form()
        self.refresh_tree()
        self.refresh_related()

    def on_update(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a record in the table first then edit the fields and click Update.")
            return
        values = self.get_form_values()
        ok, msg = self.validate(values)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return
        values = self.before_save(values)
        if values is None:
            return
        self.store.update_record(self.selected_id, values)
        self.app.save_and_notify(f"{self.record_type} record with ID {self.selected_id} updated.")
        self.clear_form()
        self.refresh_tree()
        self.refresh_related()

    def on_delete(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a record in the table first then click Delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the selected {self.record_type} record with ID {self.selected_id}?"):
            return
        rid = self.selected_id
        self.store.delete(rid)
        self.app.save_and_notify(f"{self.record_type} record with ID {rid} deleted.")
        self.clear_form()
        self.refresh_tree()
        self.refresh_related()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        rid = int(self.tree.item(sel[0], "values")[0])
        record = self.store.get(rid)
        if record:
            self.selected_id = rid
            self.id_label_var.set(f"Selected record ID: {rid}")
            self.set_form_values(record)

    def refresh_tree(self, filter_text=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.store.search(self.record_type, filter_text) if filter_text else self.store.by_type(self.record_type)
        for rec in rows:
            values = [self.display_value(rec, key) for key, _, _ in self.columns]
            self.tree.insert("", tk.END, values=values)
        self.app.update_status_counts()

#Creating the Client, Airlines and Flights tabs
class ClientTab(RecordTab):
    record_type = TYPE_CLIENT
    fields = CLIENT_FIELDS
    columns = CLIENT_COLUMNS

class AirlineTab(RecordTab):
    record_type = TYPE_AIRLINE
    fields = AIRLINE_FIELDS
    columns = AIRLINE_COLUMNS

    def refresh_related(self):
        self.app.flight_tab.reload_comboboxes()

class FlightTab(RecordTab):
    record_type = TYPE_FLIGHT
    fields = FLIGHT_FIELDS
    columns = FLIGHT_COLUMNS

    def combobox_choices(self, key):
        if key == "Client_ID":
            return {f"{r['ID']} - {r.get('Name', '')}": r["ID"] for r in self.store.by_type(TYPE_CLIENT)}
        if key == "Airline_ID":
            return {f"{r['ID']} - {r.get('CompanyName', '')}": r["ID"] for r in self.store.by_type(TYPE_AIRLINE)}
        return {}

    def display_value(self, record, key):
        if key == "Client_ID":
            client = self.store.get(record.get("Client_ID"))
            return f"{record.get('Client_ID')} - {client.get('Name', '?')}" if client else record.get("Client_ID")
        if key == "Airline_ID":
            airline = self.store.get(record.get("Airline_ID"))
            return f"{record.get('Airline_ID')} - {airline.get('CompanyName', '?')}" if airline else record.get("Airline_ID")
        return record.get(key, "")

    def validate(self, values):
        if not self.store.by_type(TYPE_CLIENT):
            return False, "No clients exist. Please create a client record first."
        if not self.store.by_type(TYPE_AIRLINE):
            return False, "No airlines exist. Please create an airline record first."
        if values.get("Client_ID") is None:
            return False, "Please choose a client."
        if values.get("Airline_ID") is None:
            return False, "Please choose an airline."
        if not values.get("StartCity"): 
            return False, "'Start City' is required."
        if not values.get("EndCity"):
            return False, "'End City' is required."
        if values.get("Date") is None:
            return False, "Please select a flight date and time."
        return True, ""

    def reload_comboboxes(self):
        for key in ("Client_ID", "Airline_ID"):
            widget = self.entries[key]
            widget["values"] = list(self.combobox_choices(key).keys())
        self.refresh_tree()


#Sidebar navigation button 
class SidebarButton(ttk.Frame):
    def __init__(self, parent, text, command):
        super().__init__(parent, padding=(10, 8))
        self.command = command
        self.label = ttk.Label(self, text=text, font=("TkDefaultFont", 10))
        self.label.pack(side=tk.LEFT)
        self.set_selected(False)
        for widget in (self, self.label):
            widget.bind("<Button-1>", lambda e: self.command())
            widget.configure(cursor="hand2")

    def set_selected(self, selected: bool):
        style = "Sidebar.Selected.TFrame" if selected else "Sidebar.TFrame"
        label_style = "Sidebar.Selected.TLabel" if selected else "Sidebar.TLabel"
        self.configure(style=style)
        self.label.configure(style=label_style)

#Main application window

class TravelAgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Specialist Travel Agent - Record Management System")
        self.geometry("900x620")
        self.minsize(780, 520)

        self.store = RecordStore()

        self._setup_sidebar_styles()
        self._build_menu()

        self.status_var = tk.StringVar()
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=4)
        status.pack(fill=tk.X, side=tk.BOTTOM)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        sidebar = ttk.Frame(body, width=150, style="Sidebar.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="Record Types", style="Sidebar.Heading.TLabel", padding=(10, 8, 10, 4)).pack(fill=tk.X)

        content = ttk.Frame(body)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # Setting up tab contents 
        self.client_tab = ClientTab(content, self.store, self)
        self.airline_tab = AirlineTab(content, self.store, self)
        self.flight_tab = FlightTab(content, self.store, self)
        for tab in (self.client_tab, self.airline_tab, self.flight_tab):
            tab.place(x=0, y=0, relwidth=1, relheight=1)

        # Sidebar buttons
        self.sidebar_buttons = {}
        nav_items = [
            ("Clients", self.client_tab),
            ("Airlines", self.airline_tab),
            ("Flights", self.flight_tab),
        ]
        for label, tab in nav_items:
            btn = SidebarButton(sidebar, label, command=lambda t=tab: self.show_tab(t))
            btn.pack(fill=tk.X)
            self.sidebar_buttons[tab] = btn

        self.show_tab(self.client_tab)

        # making sure the flight comboboxes are populated at the start 
        self.flight_tab.reload_comboboxes()

        self.update_status_counts(f"Loaded data from {DATA_FILE}" if os.path.exists(DATA_FILE) else "No existing data file found")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_sidebar_styles(self):
        style = ttk.Style(self)
        style.configure("Sidebar.TFrame", background="#e8e8ea")
        style.configure("Sidebar.Selected.TFrame", background="#c9d8f5")
        style.configure("Sidebar.TLabel", background="#e8e8ea", foreground="#333")
        style.configure("Sidebar.Selected.TLabel", background="#c9d8f5", foreground="#1a4fa0",
                         font=("TkDefaultFont", 10, "bold"))
        style.configure("Sidebar.Heading.TLabel", background="#e8e8ea", foreground="#777",
                         font=("TkDefaultFont", 9))

    def show_tab(self, tab):
        """Raise the chosen tab above the others and highlight its sidebar button."""
        tab.tkraise()
        for other_tab, btn in self.sidebar_buttons.items():
            btn.set_selected(other_tab is tab)
        self.current_tab = tab

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Now", command=lambda: self.save_and_notify("Data saved."))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Specialist Travel Agent\nRecord Management System\n\n"
            "Manages Client, Airline and Flight records.\n"
            f"Data file: {DATA_FILE}"
        )

    def save_and_notify(self, message):
        if self.store.save():
            self.update_status_counts(message)

    def update_status_counts(self, message=None):
        n_c = len(self.store.by_type(TYPE_CLIENT))
        n_a = len(self.store.by_type(TYPE_AIRLINE))
        n_f = len(self.store.by_type(TYPE_FLIGHT))
        base = f"Clients: {n_c}   Airlines: {n_a}   Flights: {n_f}"
        self.status_var.set(f"{base}    |    {message}" if message else base)

    def on_close(self):
        if self.store.dirty:
            if not self.store.save():
                if not messagebox.askyesno("Save failed", "Saving failed. Quit anyway and lose changes?"):
                    return
        self.destroy()


if __name__ == "__main__":
    app = TravelAgentApp()
    app.mainloop()
    