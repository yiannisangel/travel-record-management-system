"""
gui.py

Presentation layer for the Specialist Travel Agent
Record Management System.

Responsibilities:
    - Capture user input
    - Display records
    - Call controller methods
    - Display status and messages

No validation logic.
No storage access.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# ======================================================
# HLD FIELD DEFINITIONS
# ======================================================

CLIENT_FIELDS = [
    ("clientName", "Client Name", "entry"),
    ("email", "Email", "entry"),
    ("addressLineOne", "Address Line 1", "entry"),
    ("addressLineTwo", "Address Line 2", "entry"),
    ("addressLineThree", "Address Line 3", "entry"),
    ("city", "City", "entry"),
    ("state", "County / State", "entry"),
    ("zipCode", "Postcode", "entry"),
    ("country", "Country", "entry"),
    ("phoneNumber", "Telephone", "entry")
]

AIRLINE_FIELDS = [
    ("airlineName", "Airline Name", "entry")
]

FLIGHT_FIELDS = [
    ("clientId", "Client", "combobox"),
    ("airlineId", "Airline", "combobox"),
    ("date", "Flight Date", "date"),
    ("startCity", "Origin", "entry"),
    ("endCity", "Destination", "entry")
]

CLIENT_COLUMNS = [
    ("id", "ID", 60),
    ("clientName", "Client Name", 180),
    ("email", "Email", 220),
    ("phoneNumber", "Telephone", 140)
]

AIRLINE_COLUMNS = [
    ("id", "ID", 60),
    ("airlineName", "Airline Name", 250)
]

FLIGHT_COLUMNS = [
    ("id", "ID", 60),
    ("clientId", "Client", 220),
    ("airlineId", "Airline", 220),
    ("date", "Date", 150),
    ("startCity", "Origin", 150),
    ("endCity", "Destination", 150)
]

# ======================================================
# GENERIC RECORD TAB
# ======================================================

class RecordTab(ttk.Frame):
    """
    Base class used by all tabs.
    """

    record_type = None
    fields = []
    columns = []

    def __init__(self, parent, controller, app):
        super().__init__(parent)

        self.controller = controller
        self.app = app

        self.selected_id = None
        self.entries = {}
        self.tree = None
        self.search_var = tk.StringVar()

        self.clients_lookup = {}
        self.airlines_lookup = {}

        self.record_label = tk.StringVar(value="")
        self.build_ui()
        self.refresh_tree()

    def build_ui(self):
        """
        Build page layout.
        """
        self.build_form()
        self.build_buttons()
        self.build_search()
        self.build_tree()

    def build_form(self):
        """
        Build data entry form.
        """

        form = ttk.LabelFrame(
            self,
            text=f"{self.record_type} Details",
            padding=10
        )

        form.pack(fill=tk.X)

        for row, (field, label, widget_type) in enumerate(self.fields):

            ttk.Label(
                form,
                text=f"{label}:"
            ).grid(
                row=row,
                column=0,
                sticky="e",
                padx=6,
                pady=4
            )

            if widget_type == "entry":

                widget = ttk.Entry(
                    form,
                    width=40
                )

            elif widget_type == "date":

                widget = DateEntry(
                    form,
                    width=37,
                    date_pattern="yyyy-mm-dd"
                )

            else:

                widget = ttk.Combobox(
                    form,
                    width=37,
                    state="readonly"
                )

            widget.grid(
                row=row,
                column=1,
                sticky="w",
                padx=6,
                pady=4
            )

            self.entries[field] = widget

        self.record_label.set("New record")

        ttk.Label(
            form,
            textvariable=self.record_label
        ).grid(
            row=len(self.fields),
            column=0,
            columnspan=2,
            sticky="w"
        )

    def build_buttons(self):
        """
        Creates Create, Update, Delete and Clear actions.
        """

        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, pady=8)

        ttk.Button(
            frame,
            text="New / Clear",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            frame,
            text="Create Record",
            command=self.on_create
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            frame,
            text="Update Selected",
            command=self.on_update
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            frame,
            text="Delete Selected",
            command=self.on_delete
        ).pack(side=tk.LEFT, padx=3)

    def build_search(self):
        """
        Creates a reusable search interface shared by all record types.
        """

        frame = ttk.LabelFrame(
            self,
            text="Search",
            padding=8
        )

        frame.pack(fill=tk.X)

        ttk.Entry(
            frame,
            textvariable=self.search_var,
            width=40
        ).pack(side=tk.LEFT)

        ttk.Button(
            frame,
            text="Search",
            command=self.on_search
        ).pack(side=tk.LEFT)

        ttk.Button(
            frame,
            text="Show All",
            command=self.refresh_tree
        ).pack(side=tk.LEFT)

    def build_tree(self):
        """
        Constructs a Treeview control and vertical scrollbar.
        Treeview was selected because it provides a flexible
        tabular representation of records
        """

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=[c[0] for c in self.columns],
            show="headings",
            height=12
        )

        for key, heading, width in self.columns:

            self.tree.heading(
                key,
                text=heading
            )

            self.tree.column(
                key,
                width=width
            )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )

    def get_form_values(self):
        """
        Extracts values from widgets and returns a dictionary.
        Dictionaries provide clear field-name mapping and support
        communication with the controller layer.
        """

        values = {}

        for field, _, widget_type in self.fields:

            widget = self.entries[field]

            if widget_type == "date":
                values[field] = widget.get_date()
            else:
                values[field] = widget.get().strip()

        return values

    def clear_form(self):
        """
        Resets form controls and selected identifiers.
        """

        self.selected_id = None

        self.record_label.set(
            "New record"
        )

        for field, _, widget_type in self.fields:

            widget = self.entries[field]

            if widget_type == "entry":

                widget.delete(0, tk.END)

            elif widget_type == "combobox":

                widget.set("")

            elif widget_type == "date":

                pass

    def populate_tree(self, records):
        """
        Clears the existing Treeview contents and inserts refreshed records.
        """

        for row in self.tree.get_children():
            self.tree.delete(row)

        for record in records:

            values = [
                record.get(col[0], "")
                for col in self.columns
            ]

            self.tree.insert(
                "",
                tk.END,
                values=values
            )

    def refresh_tree(self):
        """
        Obtains data from the controller and updates both the data grid and
        application statistics.
        """
        records = self.controller.get_records(
            self.record_type
        )

        self.populate_tree(records)

        self.app.update_status_counts()

    def on_create(self):
        """
        Obtains data from the controller and updates both the data grid and
        and provides user feedback.
        """

        try:

            print(
                self.get_form_values()
            )

            self.controller.create_record(
                self.record_type,
                self.get_form_values()
            )

            self.refresh_tree()

            self.clear_form()

            messagebox.showinfo(
                "Success",
                "Record created."
            )

        except ValueError as ex:

            messagebox.showerror(
                "Error",
                str(ex)
            )

    def on_update(self):
        """
        Validates selection, submits modified values and refreshes the display.
        """

        if self.selected_id is None:

            messagebox.showwarning(
                "Warning",
                "Select a record first."
            )

            return

        try:

            self.controller.update_record(
                self.record_type,
                self.selected_id,
                self.get_form_values()
            )

            self.refresh_tree()

        except ValueError as ex:

            messagebox.showerror(
                "Error",
                str(ex)
            )

    def on_delete(self):
        """
        Confirms deletion before requesting removal through the controller. 
        """

        if self.selected_id is None:
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Delete selected record?"
        ):
            return

        self.controller.delete_record(
            self.record_type,
            self.selected_id
        )

        self.refresh_tree()

        self.clear_form()

    def on_search(self):
        """
        Delegates search operations to the controller. 
        """

        records = self.controller.search(
            self.record_type,
            self.search_var.get()
        )

        self.populate_tree(records)

    def on_select(self, _event):
        """
        Load selected record into the form.
        """

        selection = self.tree.selection()

        if not selection:
            return

        item = self.tree.item(selection[0])

        self.selected_id = item["values"][0]

        print(
            "Selected ID:",
            self.selected_id
        )

        record = self.controller.get_record(
            self.record_type,
            self.selected_id
        )

        print(
            "Record found =",
            record
        )

        if record:
            self.load_record(record)

    def load_record(self, record):
        """
        Load record data into form controls.
        """

        self.record_label.set(
            f"Selected Record ID: {record['id']}"
        )

        for field, _, widget_type in self.fields:

            widget = self.entries[field]

            value = record.get(field, "")

            if widget_type == "entry":

                widget.delete(0, tk.END)
                widget.insert(0, str(value))

            elif widget_type == "combobox":

                if (
                    field == "clientId"
                    and hasattr(self, "clients_lookup")
                ):

                    widget.set(
                        self.clients_lookup.get(
                            str(value),
                            str(value)
                        )
                    )

                elif (
                    field == "airlineId"
                    and hasattr(self, "airlines_lookup")
                ):

                    widget.set(
                        self.airlines_lookup.get(
                            str(value),
                            str(value)
                        )
                    )

                else:

                    widget.set(str(value))

            elif widget_type == "date":

                try:
                    widget.set_date(value)

                except ValueError as ex:
                    print(ex)


# ======================================================
# CLIENT TAB
# ======================================================

class ClientTab(RecordTab):
    """
    ClientTab specialises RecordTab through configuration rather than
    extensive code changes. It refreshes flight comboboxes when client
    data changes.
    """
    record_type = "CLIENT"
    fields = CLIENT_FIELDS
    columns = CLIENT_COLUMNS

    def refresh_tree(self):
        super().refresh_tree()

        print("CLIENT REFRESH")

        if hasattr(self.app, "flight_tab"):
            print("CALLING RELOAD")

            try:
                self.app.flight_tab.reload_comboboxes()
                print("RELOAD COMPLETED")
            except ValueError as ex:
                print("RELOAD FAILED", ex)

# ======================================================
# AIRLINE TAB
# ======================================================

class AirlineTab(RecordTab):
    """
    AirlineTab mirrors ClientTab and maintains flight-airline
    consistency after updates.
    """

    record_type = "AIRLINE"

    fields = AIRLINE_FIELDS

    columns = AIRLINE_COLUMNS

    def refresh_tree(self):
        super().refresh_tree()

        if hasattr(self.app, "flight_tab"):
            self.app.flight_tab.reload_comboboxes()

# ======================================================
# FLIGHT TAB
# ======================================================

class FlightTab(RecordTab):
    """
    FlightTab contains the most domain-specific logic. It loads airline
    and client lookup values, translates identifiers into human-readable
    names and implements enriched searching.
    """

    record_type = "FLIGHT"

    fields = FLIGHT_FIELDS

    columns = FLIGHT_COLUMNS

    def reload_comboboxes(self):
        """
        Load client and airline names into
        the flight dropdowns.
        """

        print("reload_comboboxes called")

        clients = self.controller.list_clients()

        print("Clients loaded:", clients)

        self.clients_lookup = {
            str(c["id"]): f'{c["id"]} - {c["clientName"]}'
            for c in clients
        }

        self.entries["clientId"].configure(
            values=list(self.clients_lookup.values())
        )

        airlines = self.controller.list_airlines()

        self.airlines_lookup = {
            str(a["id"]): f'{a["id"]} - {a["airlineName"]}'
            for a in airlines
        }

        self.entries["airlineId"]["values"] = list(
            self.airlines_lookup.values()
        )

    def populate_tree(self, records):
        """
        Display flight records using
        client and airline names.
        """

        for row in self.tree.get_children():
            self.tree.delete(row)

        clients = {
            c["id"]: c["clientName"]
            for c in self.controller.list_clients()
        }

        airlines = {
            a["id"]: a["airlineName"]
            for a in self.controller.list_airlines()
        }

        for record in records:

            values = [

                record["id"],

                clients.get(
                    record["clientId"],
                    record["clientId"]
                ),

                airlines.get(
                    record["airlineId"],
                    record["airlineId"]
                ),

                record["date"],
                record["startCity"],
                record["endCity"]
            ]

            self.tree.insert(
                "",
                tk.END,
                values=values
            )

    def get_form_values(self):
        """
        Convert combobox display values into IDs.
        """

        values = super().get_form_values()

        values["date"] = (
            values["date"].strftime(
                "%Y-%m-%dT00:00:00"
            )
        )

        if values["clientId"]:

            values["clientId"] = int(
                values["clientId"].split("-")[0].strip()
            )

        if values["airlineId"]:

            values["airlineId"] = int(
                values["airlineId"].split("-")[0].strip()
            )

        return values

    def on_search(self):
        """
        Search flights using client names,
        airline names and flight details.
        """

        search_text = self.search_var.get().lower().strip()

        records = self.controller.get_records(
            self.record_type
        )

        clients = {
            c["id"]: c["clientName"].lower()
            for c in self.controller.list_clients()
        }

        airlines = {
            a["id"]: a["airlineName"].lower()
            for a in self.controller.list_airlines()
        }

        filtered = []

        for record in records:

            client_name = clients.get(
                record["clientId"],
                ""
            )

            airline_name = airlines.get(
                record["airlineId"],
                ""
            )

            combined_text = (
                f"{client_name} "
                f"{airline_name} "
                f"{record['startCity']} "
                f"{record['endCity']} "
                f"{record['date']}"
            ).lower()

            if search_text in combined_text:
                filtered.append(record)

        self.populate_tree(filtered)

# ======================================================
# MAIN APPLICATION
# ======================================================

class TravelAgentApp(tk.Tk):
    """
    Acts as the application shell. Responsibilities include layout management,
    navigation, menu creation, status updates and shutdown processing.
    """

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        self.title(
            "Specialist Travel Agent - Record Management System"
        )

        self.geometry("1000x700")

        self.status_var = tk.StringVar()

        self.build_menu()

        self.build_layout()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

    def build_layout(self):
        """
        Creates sidebar navigation, content area, status bar and tab instances.
        """

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        sidebar = ttk.Frame(body, width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        content = ttk.Frame(body)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.client_tab = ClientTab(
            content,
            self.controller,
            self
        )

        self.airline_tab = AirlineTab(
            content,
            self.controller,
            self
        )

        self.flight_tab = FlightTab(
            content,
            self.controller,
            self
        )

        self.flight_tab.reload_comboboxes()

        for tab in (
            self.client_tab,
            self.airline_tab,
            self.flight_tab
        ):
            tab.place(
                relwidth=1,
                relheight=1
            )

        ttk.Button(
            sidebar,
            text="Clients",
            command=lambda: self.show_tab(self.client_tab)
        ).pack(fill=tk.X)

        ttk.Button(
            sidebar,
            text="Airlines",
            command=lambda: self.show_tab(self.airline_tab)
        ).pack(fill=tk.X)

        ttk.Button(
            sidebar,
            text="Flights",
            command=lambda: self.show_tab(self.flight_tab)
        ).pack(fill=tk.X)

        status = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor="w"
        )

        status.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        self.show_tab(self.client_tab)

    def build_menu(self):
        """
        Create application menu.
        """

        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        file_menu.add_command(
            label="Exit",
            command=self.on_close
        )

        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

        # Help menu
        help_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        help_menu.add_command(
            label="About",
            command=self.show_about
        )

        menubar.add_cascade(
            label="Help",
            menu=help_menu
        )

        self.config(menu=menubar)

    def show_about(self):
        """
        Display About dialog.
        """

        messagebox.showinfo(
            "About",
            "Specialist Travel Agent\n"
            "Record Management System\n\n"
            "Manages Client, Airline and Flight records.\n\n"
            "Storage:\n"
            "clients.json\n"
            "airlines.json\n"
            "flights.json\n\n"
            "Version 1.0"
        )

    def show_tab(self, tab):
        """
        Display the selected application tab and refresh its data.
        """

        tab.tkraise()
        tab.refresh_tree()

    def update_status_counts(self):
        """
        Update the status bar with current record counts.
        """

        counts = self.controller.get_counts()

        self.status_var.set(
            f"Clients: {counts['clients']}   "
            f"Airlines: {counts['airlines']}   "
            f"Flights: {counts['flights']}"
        )

    def on_close(self):
        """Close the application safely."""

        self.controller.save()

        self.destroy()


# ======================================================
# ENTRY POINT
# ======================================================

def main():
    """Application entry point."""

    from storage import JsonStorage
    from controller import RecordController

    storage = JsonStorage()

    controller = RecordController(
        storage
    )

    app = TravelAgentApp(
        controller
    )

    app.mainloop()


if __name__ == "__main__":
    main()
