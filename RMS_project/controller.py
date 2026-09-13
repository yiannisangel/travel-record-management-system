"""
Business controller layer.
Acts between GUI and Storage.
"""

from validation import (
    Validator,
    ValidationError
)


class RecordController:
    """
    Main controller for the Record Management System.
    """

    def __init__(self, store):
        """
        Initialise controller.
        """
        self.store = store

    # =====================================================
    # Generic GUI Methods
    # =====================================================

    def get_records(self, record_type):
        """
        Return all records of a type.
        """

        if record_type == "CLIENT":
            return self.store.get_all_clients()

        if record_type == "AIRLINE":
            return self.store.get_all_airlines()

        if record_type == "FLIGHT":
            return self.store.get_all_flights()

        return []

    def get_record(self, record_type, record_id):
        """
        Return a single record.
        """

        records = self.get_records(record_type)

        for record in records:
            if record["id"] == record_id:
                return record

        return None

    def create_record(self, record_type, data):
        """
        Generic create method used by GUI.
        """

        if record_type == "CLIENT":
            return self.create_client(data)

        if record_type == "AIRLINE":
            return self.create_airline(data)

        if record_type == "FLIGHT":
            return self.create_flight(data)

        raise ValueError(
            f"Unsupported record type: {record_type}"
        )

    def update_record(
        self,
        record_type,
        record_id,
        data
    ):
        """
        Generic update method used by GUI.
        """

        if record_type == "CLIENT":
            return self.update_client(
                record_id,
                data
            )

        if record_type == "AIRLINE":
            return self.store.update_airline(
                record_id,
                data
            )

        if record_type == "FLIGHT":
            return self.store.update_flight(
                record_id,
                data
            )

        raise ValueError(
            f"Unsupported record type: {record_type}"
        )

    def delete_record(
        self,
        record_type,
        record_id
    ):
        """
        Generic delete method used by GUI.
        """

        if record_type == "CLIENT":
            return self.delete_client(record_id)

        if record_type == "AIRLINE":
            return self.store.delete_airline(
                record_id
            )

        if record_type == "FLIGHT":
            return self.store.delete_flight(
                record_id
            )

        raise ValueError(
            f"Unsupported record type: {record_type}"
        )

    # =====================================================
    # Client Operations
    # =====================================================

    def create_client(self, client):
        """
        Create client record.
        """

        Validator.validate_required(
            "Client Name",
            client["clientName"]
        )

        Validator.validate_required(
            "Phone Number",
            client["phoneNumber"]
        )

        Validator.validate_uk_phone(
            client["phoneNumber"]
        )

        Validator.validate_postcode(
            client["zipCode"]
        )

        if client.get("email"):
            Validator.validate_email(
                client["email"]
            )

        Validator.validate_duplicate(
            client,
            self.store.get_all_clients(),
            [
                "clientName",
                "phoneNumber"
            ]
        )

        return self.store.insert_client(client)

    def update_client(
        self,
        record_id,
        client
    ):
        """
        Update client.
        """

        return self.store.update_client(
            record_id,
            client
        )

    def delete_client(
        self,
        record_id
    ):
        """
        Delete client.
        """

        return self.store.delete_client(
            record_id
        )

    # =====================================================
    # Airline Operations
    # =====================================================

    def create_airline(
        self,
        airline
    ):
        """
        Create airline record.
        """

        Validator.validate_required(
            "Airline Name",
            airline["airlineName"]
        )

        Validator.validate_duplicate(
            airline,
            self.store.get_all_airlines(),
            ["airlineName"]
        )

        return self.store.insert_airline(
            airline
        )

    # =====================================================
    # Flight Operations
    # =====================================================

    def create_flight(
        self,
        flight
    ):
        """
        Create flight record.
        """

        Validator.validate_future_date(
            flight["date"]
        )

        Validator.validate_city(
            flight["startCity"]
        )

        Validator.validate_city(
            flight["endCity"]
        )

        if not self.store.client_exists(
            flight["clientId"]
        ):
            raise ValidationError(
                "Client does not exist."
            )

        if not self.store.airline_exists(
            flight["airlineId"]
        ):
            raise ValidationError(
                "Airline does not exist."
            )

        Validator.validate_duplicate(
            flight,
            self.store.get_all_flights(),
            [
                "clientId",
                "airlineId",
                "date"
            ]
        )

        return self.store.insert_flight(
            flight
        )

    # =====================================================
    # Search
    # =====================================================

    def search(
        self,
        record_type,
        text
    ):
        """
        Search records.
        """

        return self.store.search(
            record_type,
            text
        )

    # =====================================================
    # Dropdown Support
    # =====================================================

    def list_clients(self):
        """
        Return all clients.
        """

        return self.store.get_all_clients()

    def list_airlines(self):
        """
        Return all airlines.
        """

        return self.store.get_all_airlines()

    # =====================================================
    # Status Bar Support
    # =====================================================

    def get_counts(self):
        """
        Record counts by type.
        """

        return {
            "clients":
                len(
                    self.store.get_all_clients()
                ),

            "airlines":
                len(
                    self.store.get_all_airlines()
                ),

            "flights":
                len(
                    self.store.get_all_flights()
                )
        }

    # =====================================================
    # Persistence Support
    # =====================================================

    def save(self):
        """
        Persist data.
        """

        if hasattr(self.store, "save"):
            return self.store.save()

        return True