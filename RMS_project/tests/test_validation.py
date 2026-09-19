import unittest
from datetime import date, timedelta

from validation import Validator, ValidationError


class TestValidator(unittest.TestCase):

    def test_required_accepts_non_blank_value(self):
        Validator.validate_required("Client Name", "Alice")

    def test_required_rejects_blank_value(self):
        with self.assertRaises(ValidationError):
            Validator.validate_required("Client Name", "   ")

    def test_valid_email_is_accepted(self):
        Validator.validate_email("alice@example.com")

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValidationError):
            Validator.validate_email("alice.example.com")

    def test_valid_uk_phone_is_accepted(self):
        Validator.validate_uk_phone("+441612345678")

    def test_invalid_uk_phone_is_rejected(self):
        with self.assertRaises(ValidationError):
            Validator.validate_uk_phone("12345")

    def test_valid_uk_postcode_is_accepted(self):
        Validator.validate_postcode("M1 1AE")

    def test_invalid_uk_postcode_is_rejected(self):
        with self.assertRaises(ValidationError):
            Validator.validate_postcode("NOT A POSTCODE")

    def test_city_allows_common_name_characters(self):
        Validator.validate_city("Saint-Étienne")

    def test_city_rejects_numbers(self):
        with self.assertRaises(ValidationError):
            Validator.validate_city("London123")

    def test_future_date_is_accepted(self):
        future = date.today() + timedelta(days=1)
        Validator.validate_future_date(future)

    def test_today_is_rejected(self):
        with self.assertRaises(ValidationError):
            Validator.validate_future_date(date.today())

    def test_past_date_is_rejected(self):
        past = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            Validator.validate_future_date(past)

    def test_invalid_date_string_is_rejected(self):
        with self.assertRaises(ValidationError):
            Validator.validate_future_date("not-a-date")

    def test_duplicate_record_is_rejected(self):
        existing = [
            {"clientName": "Alice", "phoneNumber": "07123456789"}
        ]
        new = {
            "clientName": "Alice",
            "phoneNumber": "07123456789"
        }

        with self.assertRaises(ValidationError):
            Validator.validate_duplicate(
                new,
                existing,
                ["clientName", "phoneNumber"],
            )

    def test_non_duplicate_record_is_accepted(self):
        existing = [
            {"clientName": "Alice", "phoneNumber": "07123456789"}
        ]
        new = {
            "clientName": "Alice",
            "phoneNumber": "07999999999"
        }

        Validator.validate_duplicate(
            new,
            existing,
            ["clientName", "phoneNumber"],
        )


if __name__ == "__main__":
    unittest.main()
