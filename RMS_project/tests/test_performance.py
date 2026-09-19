import tempfile
import time
import unittest
from pathlib import Path

from controller import RecordController
from storage import JsonStorage


class TestPerformance(unittest.TestCase):
    """
    Performance tests for common record operations with a dataset
    representative of the HLD scalability expectation ("hundreds of records").

    Temporary JSON files are used so the application's normal data files
    are not modified.
    """

    DATASET_SIZE = 500
    TARGET_SECONDS = 1.0

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)

        self.storage = JsonStorage()
        self.storage.client_file = base / "clients.json"
        self.storage.airline_file = base / "airlines.json"
        self.storage.flight_file = base / "flights.json"

        # Seed 500 records directly so setup time is not included
        # in the operation being measured.
        clients = [
            {
                "id": i,
                "recordType": "CLIENT",
                "clientName": f"Client {i}",
                "email": f"client{i}@example.com",
                "addressLineOne": f"{i} Test Street",
                "addressLineTwo": "",
                "addressLineThree": "",
                "city": "Manchester",
                "state": "Greater Manchester",
                "zipCode": "M1 1AE",
                "country": "United Kingdom",
                "phoneNumber": f"07123{i:06d}"[-11:],
            }
            for i in range(1, self.DATASET_SIZE + 1)
        ]

        self.storage._save_json(self.storage.client_file, clients)
        self.storage._save_json(self.storage.airline_file, [])
        self.storage._save_json(self.storage.flight_file, [])

        self.controller = RecordController(self.storage)

    def tearDown(self):
        self.temp_dir.cleanup()

    def timed(self, operation_name, function):
        start = time.perf_counter()
        result = function()
        elapsed = time.perf_counter() - start

        print(
            f"\n{operation_name}: "
            f"{elapsed:.6f} seconds "
            f"({elapsed * 1000:.3f} ms)"
        )

        self.assertLess(
            elapsed,
            self.TARGET_SECONDS,
            f"{operation_name} exceeded "
            f"{self.TARGET_SECONDS} second"
        )

        return result

    def test_create_performance_with_500_existing_records(self):
        new_client = {
            "clientName": "Performance Test Client",
            "email": "performance@example.com",
            "addressLineOne": "1 Performance Street",
            "addressLineTwo": "",
            "addressLineThree": "",
            "city": "Manchester",
            "state": "Greater Manchester",
            "zipCode": "M1 1AE",
            "country": "United Kingdom",
            "phoneNumber": "07123456789",
        }

        self.timed(
            "CREATE with 500 existing records",
            lambda: self.controller.create_record(
                "CLIENT",
                new_client
            )
        )

    def test_search_performance_with_500_records(self):
        results = self.timed(
            "SEARCH across 500 records",
            lambda: self.controller.search(
                "CLIENT",
                "Client 499"
            )
        )

        self.assertGreaterEqual(len(results), 1)

    def test_update_performance_with_500_records(self):
        updated_client = {
            "clientName": "Updated Client 250",
            "email": "updated250@example.com",
            "addressLineOne": "250 Updated Street",
            "addressLineTwo": "",
            "addressLineThree": "",
            "city": "Manchester",
            "state": "Greater Manchester",
            "zipCode": "M1 1AE",
            "country": "United Kingdom",
            "phoneNumber": "07123456789",
        }

        self.timed(
            "UPDATE within 500 records",
            lambda: self.controller.update_record(
                "CLIENT",
                250,
                updated_client
            )
        )

    def test_delete_performance_with_500_records(self):
        self.timed(
            "DELETE within 500 records",
            lambda: self.controller.delete_record(
                "CLIENT",
                250
            )
        )


if __name__ == "__main__":
    unittest.main()
