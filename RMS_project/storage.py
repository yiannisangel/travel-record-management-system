"""
storage.py

JSON persistence layer for the
Specialist Travel Agent Record Management System.
"""

import json
from pathlib import Path


class JsonStorage:
    """JSON storage implementation."""

    def __init__(self):
        """Initialise file locations."""

        base_dir = Path(__file__).resolve().parent

        self.client_file = base_dir / "data" / "clients.json"
        self.airline_file = base_dir / "data" / "airlines.json"
        self.flight_file = base_dir / "data" / "flights.json"

    def _load_json(self, filename):
        if not filename.exists():
            return []

        with open(filename, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []

    def _save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

    def _generate_id(self, records):
        if not records:
            return 1

        return max(record["id"] for record in records) + 1

    def get_all_clients(self):
        """Retrieves all client records from storage."""

        return self._load_json(self.client_file)

    def get_all_airlines(self):
        """Retrieves all airline records from storage."""

        return self._load_json(self.airline_file)

    def get_all_flights(self):
        """Retrieves all flight records from storage."""

        return self._load_json(self.flight_file)

    def get_client(self, client_id):
        """Retrieve a client record by its identifier."""

        for client in self.get_all_clients():
            if client["id"] == client_id:
                return client
        return None

    def get_airline(self, airline_id):
        """Retrieve an airline record by its identifier."""

        for airline in self.get_all_airlines():
            if airline["id"] == airline_id:
                return airline
        return None

    def get_flight(self, flight_id):
        """Retrieve a flight record by its identifier."""

        for flight in self.get_all_flights():
            if flight["id"] == flight_id:
                return flight
        return None

    def client_exists(self, client_id):
        """Determine if a client record exists."""

        return any(
            client["id"] == client_id
            for client in self.get_all_clients()
        )

    def airline_exists(self, airline_id):
        """Determine if an airline record exists."""

        return any(
            airline["id"] == airline_id
            for airline in self.get_all_airlines()
        )

    def insert_client(self, client):
        """Create and store a new client record."""

        records = self.get_all_clients()
        client["id"] = self._generate_id(records)
        client["recordType"] = "CLIENT"
        records.append(client)
        self._save_json(self.client_file, records)
        return client

    def insert_airline(self, airline):
        """Create and store a new airline record."""

        records = self.get_all_airlines()
        airline["id"] = self._generate_id(records)
        airline["recordType"] = "AIRLINE"
        records.append(airline)
        self._save_json(self.airline_file, records)
        return airline

    def insert_flight(self, flight):
        """Create and store a new flight record."""

        records = self.get_all_flights()
        flight["id"] = self._generate_id(records)
        flight["recordType"] = "FLIGHT"
        records.append(flight)
        self._save_json(self.flight_file, records)
        return flight

    def update_client(self, record_id, updated_record):
        """Update an existing client record."""

        records = self.get_all_clients()

        for index, record in enumerate(records):
            if record["id"] == record_id:
                updated_record["id"] = record_id
                updated_record["recordType"] = "CLIENT"
                records[index] = updated_record
                self._save_json(self.client_file, records)
                return updated_record

        return None

    def update_airline(self, record_id, updated_record):
        """Update an existing airline record."""

        records = self.get_all_airlines()

        for index, record in enumerate(records):
            if record["id"] == record_id:
                updated_record["id"] = record_id
                updated_record["recordType"] = "AIRLINE"
                records[index] = updated_record
                self._save_json(self.airline_file, records)
                return updated_record

        return None

    def update_flight(self, record_id, updated_record):
        """Update an existing flight record."""

        records = self.get_all_flights()

        for index, record in enumerate(records):
            if record["id"] == record_id:
                updated_record["id"] = record_id
                updated_record["recordType"] = "FLIGHT"
                records[index] = updated_record
                self._save_json(self.flight_file, records)
                return updated_record

        return None

    def delete_client(self, record_id):
        """Delete a client record by its identifier."""

        records = [
            record
            for record in self.get_all_clients()
            if record["id"] != record_id
        ]

        self._save_json(self.client_file, records)
        return True

    def delete_airline(self, record_id):
        """Delete an airline record by its identifier."""

        records = [
            record
            for record in self.get_all_airlines()
            if record["id"] != record_id
        ]

        self._save_json(self.airline_file, records)
        return True

    def delete_flight(self, record_id):
        """Delete a flight record by its identifier."""

        records = [
            record
            for record in self.get_all_flights()
            if record["id"] != record_id
        ]

        self._save_json(self.flight_file, records)
        return True

    def search(self, record_type, search_text):
        """Search records of a specified type."""

        search_text = (search_text or "").lower().strip()

        if record_type == "CLIENT":
            records = self.get_all_clients()
        elif record_type == "AIRLINE":
            records = self.get_all_airlines()
        elif record_type == "FLIGHT":
            records = self.get_all_flights()
        else:
            return []

        if not search_text:
            return records

        return [
            record
            for record in records
            if search_text in str(record).lower()
        ]

    def save(self):
        """Persist appliaction data."""

        return True
