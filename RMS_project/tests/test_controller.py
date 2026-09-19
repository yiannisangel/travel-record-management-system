import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock

from controller import RecordController
from validation import ValidationError


class TestRecordController(unittest.TestCase):
    def setUp(self):
        self.store = MagicMock()
        self.controller = RecordController(self.store)

    # Retrieval / routing
    def test_get_records_routes_client_requests(self):
        self.store.get_all_clients.return_value = [{"id": 1}]
        result = self.controller.get_records("CLIENT")
        self.assertEqual(result, [{"id": 1}])
        self.store.get_all_clients.assert_called_once_with()

    def test_get_record_returns_matching_record(self):
        self.store.get_all_clients.return_value = [
            {"id": 1, "clientName": "Alice"},
            {"id": 2, "clientName": "Bob"},
        ]
        result = self.controller.get_record("CLIENT", 2)
        self.assertEqual(result["clientName"], "Bob")

    def test_get_record_returns_none_when_missing(self):
        self.store.get_all_clients.return_value = [{"id": 1}]
        self.assertIsNone(self.controller.get_record("CLIENT", 99))

    def test_create_record_rejects_unknown_type(self):
        with self.assertRaises(ValueError):
            self.controller.create_record("UNKNOWN", {})

    # Client creation
    def test_valid_client_is_inserted(self):
        client = {
            "clientName": "Alice Smith",
            "phoneNumber": "07123456789",
            "zipCode": "M1 1AE",
            "email": "alice@example.com",
        }
        self.store.get_all_clients.return_value = []
        self.store.insert_client.return_value = {**client, "id": 1}

        result = self.controller.create_client(client)

        self.store.insert_client.assert_called_once_with(client)
        self.assertEqual(result["id"], 1)

    def test_create_client_rejects_invalid_phone(self):
        client = {
            "clientName": "Alice Smith",
            "phoneNumber": "12345",
            "zipCode": "M1 1AE",
            "email": "alice@example.com",
        }
        self.store.get_all_clients.return_value = []

        with self.assertRaises(ValidationError):
            self.controller.create_client(client)

        self.store.insert_client.assert_not_called()

    def test_create_client_rejects_duplicate(self):
        client = {
            "clientName": "Alice Smith",
            "phoneNumber": "07123456789",
            "zipCode": "M1 1AE",
            "email": "alice@example.com",
        }
        self.store.get_all_clients.return_value = [client.copy()]

        with self.assertRaises(ValidationError):
            self.controller.create_client(client)

        self.store.insert_client.assert_not_called()

    # Airline creation
    def test_valid_airline_is_inserted(self):
        airline = {"airlineName": "Example Air"}
        self.store.get_all_airlines.return_value = []
        self.store.insert_airline.return_value = {**airline, "id": 1}

        result = self.controller.create_airline(airline)

        self.store.insert_airline.assert_called_once_with(airline)
        self.assertEqual(result["id"], 1)

    def test_create_airline_rejects_duplicate(self):
        airline = {"airlineName": "Example Air"}
        self.store.get_all_airlines.return_value = [airline.copy()]

        with self.assertRaises(ValidationError):
            self.controller.create_airline(airline)

        self.store.insert_airline.assert_not_called()

    # Flight creation
    def test_valid_flight_is_inserted(self):
        flight = {
            "clientId": 1,
            "airlineId": 1,
            "date": (date.today() + timedelta(days=5)).isoformat(),
            "startCity": "Manchester",
            "endCity": "Madrid",
        }
        self.store.client_exists.return_value = True
        self.store.airline_exists.return_value = True
        self.store.get_all_flights.return_value = []
        self.store.insert_flight.return_value = {**flight, "id": 1}

        result = self.controller.create_flight(flight)

        self.store.insert_flight.assert_called_once_with(flight)
        self.assertEqual(result["id"], 1)

    def test_create_flight_rejects_missing_client(self):
        flight = {
            "clientId": 99,
            "airlineId": 1,
            "date": (date.today() + timedelta(days=5)).isoformat(),
            "startCity": "Manchester",
            "endCity": "Madrid",
        }
        self.store.client_exists.return_value = False
        self.store.airline_exists.return_value = True

        with self.assertRaises(ValidationError):
            self.controller.create_flight(flight)

        self.store.insert_flight.assert_not_called()

    def test_create_flight_rejects_missing_airline(self):
        flight = {
            "clientId": 1,
            "airlineId": 99,
            "date": (date.today() + timedelta(days=5)).isoformat(),
            "startCity": "Manchester",
            "endCity": "Madrid",
        }
        self.store.client_exists.return_value = True
        self.store.airline_exists.return_value = False

        with self.assertRaises(ValidationError):
            self.controller.create_flight(flight)

        self.store.insert_flight.assert_not_called()

    def test_create_flight_rejects_past_date(self):
        flight = {
            "clientId": 1,
            "airlineId": 1,
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "startCity": "Manchester",
            "endCity": "Madrid",
        }

        with self.assertRaises(ValidationError):
            self.controller.create_flight(flight)

        self.store.insert_flight.assert_not_called()

    def test_create_flight_rejects_invalid_city(self):
        flight = {
            "clientId": 1,
            "airlineId": 1,
            "date": (date.today() + timedelta(days=5)).isoformat(),
            "startCity": "Manchester123",
            "endCity": "Madrid",
        }

        with self.assertRaises(ValidationError):
            self.controller.create_flight(flight)

        self.store.insert_flight.assert_not_called()

    # Search / status / persistence
    def test_search_delegates_to_storage(self):
        self.store.search.return_value = [{"id": 1}]
        result = self.controller.search("CLIENT", "alice")
        self.store.search.assert_called_once_with("CLIENT", "alice")
        self.assertEqual(result, [{"id": 1}])

    def test_get_counts_returns_counts_for_all_record_types(self):
        self.store.get_all_clients.return_value = [{}, {}]
        self.store.get_all_airlines.return_value = [{}]
        self.store.get_all_flights.return_value = [{}, {}, {}]

        self.assertEqual(
            self.controller.get_counts(),
            {"clients": 2, "airlines": 1, "flights": 3},
        )

    def test_save_delegates_to_storage(self):
        self.store.save.return_value = True
        self.assertTrue(self.controller.save())
        self.store.save.assert_called_once_with()

    # These three tests express the documented expectation that validation
    # should also be applied before updated data reaches storage.

    def test_update_client_rejects_invalid_phone(self):
        invalid_client = {
            "clientName": "Alice Smith",
            "phoneNumber": "12345",
            "zipCode": "M1 1AE",
            "email": "alice@example.com",
        }

        with self.assertRaises(ValidationError):
            self.controller.update_record(
                "CLIENT",
                1,
                invalid_client
            )
    def test_update_airline_rejects_blank_name(self):
        with self.assertRaises(ValidationError):
            self.controller.update_record(
                "AIRLINE",
                1,
                {"airlineName": "   "},
            )

    def test_update_flight_rejects_past_date(self):
        invalid_flight = {
            "clientId": 1,
            "airlineId": 1,
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "startCity": "Manchester",
            "endCity": "Madrid",
        }

        with self.assertRaises(ValidationError):
            self.controller.update_record(
                "FLIGHT",
                1,
                 invalid_flight)


if __name__ == "__main__":
    unittest.main()
