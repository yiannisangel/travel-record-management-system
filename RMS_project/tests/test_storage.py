import tempfile
import unittest
from pathlib import Path

from storage import JsonStorage


class TestJsonStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)

        self.storage = JsonStorage()
        self.storage.client_file = base / "clients.json"
        self.storage.airline_file = base / "airlines.json"
        self.storage.flight_file = base / "flights.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    # Loading / saving
    def test_missing_file_loads_as_empty_list(self):
        self.assertEqual(self.storage.get_all_clients(), [])

    def test_malformed_json_loads_as_empty_list(self):
        self.storage.client_file.write_text(
            "{not valid json",
            encoding="utf-8"
        )
        self.assertEqual(self.storage.get_all_clients(), [])

    def test_save_and_load_preserves_unicode_data(self):
        data = [{"id": 1, "clientName": "José Álvarez"}]
        self.storage._save_json(self.storage.client_file, data)
        self.assertEqual(self.storage.get_all_clients(), data)

    # ID generation
    def test_generate_id_starts_at_one(self):
        self.assertEqual(self.storage._generate_id([]), 1)

    def test_generate_id_uses_highest_existing_id_plus_one(self):
        records = [{"id": 2}, {"id": 7}, {"id": 4}]
        self.assertEqual(self.storage._generate_id(records), 8)

    # Create / persistence
    def test_insert_client_assigns_id_type_and_persists(self):
        client = {"clientName": "Alice"}
        result = self.storage.insert_client(client)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["recordType"], "CLIENT")
        self.assertEqual(self.storage.get_all_clients(), [result])

    def test_insert_airline_assigns_id_type_and_persists(self):
        airline = {"airlineName": "Example Air"}
        result = self.storage.insert_airline(airline)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["recordType"], "AIRLINE")
        self.assertEqual(self.storage.get_all_airlines(), [result])

    def test_insert_flight_assigns_id_type_and_persists(self):
        flight = {
            "clientId": 1,
            "airlineId": 1,
            "date": "2026-10-01",
            "startCity": "Manchester",
            "endCity": "Madrid",
        }
        result = self.storage.insert_flight(flight)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["recordType"], "FLIGHT")
        self.assertEqual(self.storage.get_all_flights(), [result])

    def test_each_entity_type_has_its_own_id_sequence(self):
        client = self.storage.insert_client({"clientName": "Alice"})
        airline = self.storage.insert_airline({"airlineName": "Example Air"})
        flight = self.storage.insert_flight({
            "clientId": 1,
            "airlineId": 1,
            "date": "2026-10-01",
            "startCity": "Manchester",
            "endCity": "Madrid",
        })

        self.assertEqual(client["id"], 1)
        self.assertEqual(airline["id"], 1)
        self.assertEqual(flight["id"], 1)

    # Retrieval / existence
    def test_get_client_returns_matching_record(self):
        created = self.storage.insert_client({"clientName": "Alice"})
        self.assertEqual(
            self.storage.get_client(created["id"]),
            created
        )

    def test_get_client_returns_none_when_missing(self):
        self.assertIsNone(self.storage.get_client(99))

    def test_client_and_airline_exists_report_correctly(self):
        client = self.storage.insert_client({"clientName": "Alice"})
        airline = self.storage.insert_airline(
            {"airlineName": "Example Air"}
        )

        self.assertTrue(self.storage.client_exists(client["id"]))
        self.assertTrue(self.storage.airline_exists(airline["id"]))
        self.assertFalse(self.storage.client_exists(999))
        self.assertFalse(self.storage.airline_exists(999))

    # Update
    def test_update_client_preserves_id_type_and_persists(self):
        created = self.storage.insert_client({"clientName": "Alice"})
        updated = self.storage.update_client(
            created["id"],
            {"clientName": "Alice Jones"}
        )

        self.assertEqual(updated["id"], created["id"])
        self.assertEqual(updated["recordType"], "CLIENT")
        self.assertEqual(updated["clientName"], "Alice Jones")
        self.assertEqual(
            self.storage.get_client(created["id"]),
            updated
        )

    def test_update_missing_client_returns_none(self):
        self.assertIsNone(
            self.storage.update_client(
                99,
                {"clientName": "Nobody"}
            )
        )

    # Delete
    def test_delete_client_removes_record_from_persistent_file(self):
        first = self.storage.insert_client({"clientName": "Alice"})
        second = self.storage.insert_client({"clientName": "Bob"})

        self.storage.delete_client(first["id"])

        self.assertIsNone(self.storage.get_client(first["id"]))
        self.assertEqual(
            self.storage.get_client(second["id"]),
            second
        )

    # Search
    def test_search_is_case_insensitive_and_partial(self):
        self.storage.insert_client({"clientName": "Alice Smith"})
        self.storage.insert_client({"clientName": "Bob Jones"})

        results = self.storage.search("CLIENT", "ALI")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["clientName"],
            "Alice Smith"
        )

    def test_empty_search_returns_all_records_of_type(self):
        self.storage.insert_airline(
            {"airlineName": "Example Air"}
        )
        self.storage.insert_airline(
            {"airlineName": "Second Air"}
        )

        self.assertEqual(
            len(self.storage.search("AIRLINE", "")),
            2
        )

    def test_unknown_search_type_returns_empty_list(self):
        self.assertEqual(
            self.storage.search("UNKNOWN", "anything"),
            []
        )

    # Public save method
    def test_save_returns_true(self):
        self.assertTrue(self.storage.save())


if __name__ == "__main__":
    unittest.main()
