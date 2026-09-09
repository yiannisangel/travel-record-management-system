"""
storage.py
==========
Non-GUI data layer for the Specialist Travel Agent Record Management System.

Holds:
    * constants / configuration
    * field & column definitions for each record type
    * RecordStore: the in-memory list-of-dictionaries store, with
      load/save persistence and CRUD helper methods.

Nothing in this file imports tkinter - it can be reused by a different
front end (CLI, web, tests, etc.) or unit-tested without a display.
"""

import json
import os
import pickle
from tkinter import messagebox  # only used for user-facing warnings on load/save

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel_records.json")
STORAGE_FORMAT = "json"        # "json" or "pickle"
DATE_FORMAT = "%Y-%m-%d %H:%M"  # e.g. 2026-09-01 14:30

TYPE_CLIENT = "Client"
TYPE_AIRLINE = "Airline"
TYPE_FLIGHT = "Flight"


# ---------------------------------------------------------------------------
# Field definitions for each record type
# ---------------------------------------------------------------------------
# Each field: (key, label, widget)   widget is "entry" or "combobox"

CLIENT_FIELDS = [
    ("Name", "Name", "entry"),
    ("Address1", "Address Line 1", "entry"),
    ("Address2", "Address Line 2", "entry"),
    ("Address3", "Address Line 3", "entry"),
    ("City", "City", "entry"),
    ("State", "State", "entry"),
    ("ZipCode", "Zip Code", "entry"),
    ("Country", "Country", "entry"),
    ("Phone", "Phone Number", "entry"),
]
CLIENT_COLUMNS = [
    ("ID", "ID", 50), ("Name", "Name", 140), ("City", "City", 100),
    ("Country", "Country", 100), ("Phone", "Phone", 110),
]

AIRLINE_FIELDS = [
    ("CompanyName", "Company Name", "entry"),
]
AIRLINE_COLUMNS = [
    ("ID", "ID", 50), ("CompanyName", "Company Name", 250),
]

FLIGHT_FIELDS = [
    ("Client_ID", "Client", "combobox"),
    ("Airline_ID", "Airline", "combobox"),
    ("Date", "Date & Time", "datetime"),
    ("StartCity", "Start City", "entry"),
    ("EndCity", "End City", "entry"),
]
FLIGHT_COLUMNS = [
    ("ID", "ID", 50), ("Client_ID", "Client", 160), ("Airline_ID", "Airline", 160),
    ("Date", "Date", 130), ("StartCity", "Start City", 100), ("EndCity", "End City", 100),
]


# ---------------------------------------------------------------------------
# Storage layer
# ---------------------------------------------------------------------------
class RecordStore:
    """Keeps the master list of dictionaries in memory and persists it.

    Internal storage is a single flat list of dictionaries:

        records = [ {...}, {...}, {...} ]

    Each dictionary carries a "Type" key ("Client" / "Airline" / "Flight")
    so that one list can hold every record type, as required by the spec.
    """

    def __init__(self, filepath=DATA_FILE, fmt=STORAGE_FORMAT):
        self.filepath = filepath
        self.fmt = fmt
        self.records = []          # <-- the single list of dictionaries
        self.dirty = False         # True if there are unsaved changes
        self.load()

    # -- persistence ---------------------------------------------------
    def load(self):
        """Load records from disk if the file exists, else start empty."""
        if os.path.exists(self.filepath):
            try:
                if self.fmt == "pickle":
                    with open(self.filepath, "rb") as f:
                        self.records = pickle.load(f)
                else:
                    with open(self.filepath, "r", encoding="utf-8") as f:
                        self.records = json.load(f)
            except (json.JSONDecodeError, pickle.UnpicklingError, EOFError, OSError) as exc:
                messagebox.showwarning(
                    "Data file problem",
                    f"Could not read existing data file:\n{exc}\n\n"
                    "Starting with an empty record set."
                )
                self.records = []
        else:
            self.records = []

    def save(self):
        """Write the current record list to disk."""
        try:
            if self.fmt == "pickle":
                with open(self.filepath, "wb") as f:
                    pickle.dump(self.records, f)
            else:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(self.records, f, indent=2, default=str)
            self.dirty = False
            return True
        except OSError as exc:
            messagebox.showerror("Save failed", f"Could not save data file:\n{exc}")
            return False

    # -- JSON-Lines alternative (kept for reference / optional use) ----
    def save_jsonl(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for rec in self.records:
                f.write(json.dumps(rec, default=str) + "\n")

    def load_jsonl(self, path):
        recs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
        self.records = recs

    # -- CRUD helpers ----------------------------------------------------
    def next_id(self):
        """Auto-increment ID unique across ALL record types."""
        ids = [r.get("ID", 0) for r in self.records if isinstance(r.get("ID", 0), int)]
        return (max(ids) + 1) if ids else 1

    def add(self, record: dict) -> dict:
        record["ID"] = self.next_id()
        self.records.append(record)
        self.dirty = True
        return record

    def update(self, record_id: int, new_values: dict) -> bool:
        for rec in self.records:
            if rec.get("ID") == record_id:
                rec.update(new_values)
                self.dirty = True
                return True
        return False

    def delete(self, record_id: int) -> bool:
        before = len(self.records)
        self.records = [r for r in self.records if r.get("ID") != record_id]
        changed = len(self.records) != before
        if changed:
            self.dirty = True
        return changed

    def get(self, record_id: int):
        for rec in self.records:
            if rec.get("ID") == record_id:
                return rec
        return None

    def by_type(self, record_type: str):
        return [r for r in self.records if r.get("Type") == record_type]

    def search(self, record_type: str, text: str):
        """Case-insensitive substring search across all fields of a type."""
        text = (text or "").strip().lower()
        rows = self.by_type(record_type)
        if not text:
            return rows
        out = []
        for rec in rows:
            if any(text in str(v).lower() for v in rec.values()):
                out.append(rec)
        return out
