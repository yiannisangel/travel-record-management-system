"""
Validation module for the Specialist Travel Agent
Record Management System.
"""

import re
from datetime import datetime
from datetime import date


class ValidationError(Exception):
    """Raised when validation fails."""


class Validator:
    """
    Provides validation methods used throughout the
    Specialist Travel Agent Record management system.
    """

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    UK_PHONE_PATTERN = re.compile(
        r"^(\+44|0)(1|2|3|7|8)\d{8,9}$"
    )

    UK_POSTCODE_PATTERN = re.compile(
        r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$",
        re.IGNORECASE
    )

    CITY_PATTERN = re.compile(
        r"^[A-Za-zÀ-ÿ\s\-']+$"
    )

    @staticmethod
    def validate_required(field_name, value):
        """
        Validate mandatory field.
        """
        if value is None or str(value).strip() == "":
            raise ValidationError(
                f"{field_name} is mandatory."
            )

    @staticmethod
    def validate_email(email):
        """
        Validate email format.
        """
        if not Validator.EMAIL_PATTERN.match(email):
            raise ValidationError(
                "Invalid email address format."
            )

    @staticmethod
    def validate_uk_phone(phone):
        """
        Validate UK phone number.
        """
        if not Validator.UK_PHONE_PATTERN.match(phone):
            raise ValidationError(
                "Invalid UK telephone number."
            )

    @staticmethod
    def validate_postcode(postcode):
        """
        Validate UK postcode.
        """
        if not Validator.UK_POSTCODE_PATTERN.match(postcode):
            raise ValidationError(
                "Invalid UK postcode."
            )

    @staticmethod
    def validate_city(city):
        """
        Validate airport/city name.
        """
        if not Validator.CITY_PATTERN.match(city):
            raise ValidationError(
                "Invalid city or airport name."
            )

    @staticmethod
    def validate_future_date(flight_date):
        """
        Validate that flight date is future.
        """

        try:
            if isinstance(flight_date, str):
                flight_date = (
                    datetime.fromisoformat(
                        flight_date
                    ).date()
                )
        except ValueError as ex:
            raise ValidationError(
                "Invalid flight date format."
            ) from ex

        if flight_date <= date.today():
            raise ValidationError(
                "Flight date must be in the future."
            )


    @staticmethod
    def validate_duplicate(
        record,
        existing_records,
        unique_fields
    ):
        """
        Check duplicate record.
        """

        for existing in existing_records:

            duplicate = all(
                existing.get(field) == record.get(field)
                for field in unique_fields
            )

            if duplicate:
                raise ValidationError(
                    "Duplicate record detected."
                )
