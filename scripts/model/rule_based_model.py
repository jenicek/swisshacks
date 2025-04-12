from abc import ABC, abstractmethod
from client_data.client_data import ClientData
import re
import logging
from datetime import datetime
from typing import Tuple
import unicodedata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("validation_debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("validation")


def remove_accents(text):
    # Normalize to NFKD form (decomposes characters)
    nfkd_form = unicodedata.normalize("NFKD", text)
    # Filter out diacritical marks
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii


class Model(ABC):
    @abstractmethod
    def predict(self, client: ClientData) -> int:
        pass


class SimpleModel(Model):
    def predict(self, client: ClientData) -> int:
        if flag_missing_values(client):
            print("Missing values")
            return 0
        if flag_verify_email(client):
            print("Email mismatch")
            return 0
        if flag_phone(client):
            print("Phone number mismatch")
            return 0
        if flag_country(client):
            print("Country mismatch")
            return 0
        # if flag_inconsistent_name(client):
        #     return 0
        if flag_passport(client):
            print("Passport mismatch")
            return 0
        # if flag_address(client):
        #     print("Address mismatch")
        #     return 0
        if flag_risk_profile(client):
            print("Risk profile mismatch")
            return 0
        return 1


def to_ascii(input_str):
    # Normalize to NFKD form and encode to ASCII bytes, ignoring non-ASCII chars
    normalized = unicodedata.normalize("NFKD", input_str)
    ascii_bytes = normalized.encode("ASCII", "ignore")
    return ascii_bytes.decode("ASCII")


def flag_missing_values(client: ClientData):
    NULLABLE_FIELDS = (
        "other_ccy",
        "employer",
        "position",
        "annual_income",
        "previous_profession",
        "is_primary",
        "source_info",
        "account_number",
        "expected_transactional_behavior",
    )

    for data in (
        client.client_profile,
        client.client_description,
        client.passport,
        client.account_form,
    ):
        for path, value in data.items():
            if isinstance(path, str):
                path = path.lower()
                if path.lower() in NULLABLE_FIELDS:
                    continue
            if isinstance(value, dict):
                for key in value.keys():
                    if isinstance(key, str):
                        key = key.lower()
                        if key.lower() in NULLABLE_FIELDS:
                            continue
            if isinstance(value, str) and value is None or value == "":
                return True
    return False


def flag_verify_email(client: ClientData):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if client.account_form["email"] != client.client_profile["contact_info"]["email"]:
        return True

    if not re.match(email_pattern, client.account_form["email"]):
        return True

    return False


def flag_phone(client: ClientData):
    phone_number = client.account_form["phone_number"].replace(" ", "")

    if phone_number != client.client_profile["contact_info"]["telephone"].replace(
        " ", ""
    ):
        return True

    if not re.match("^\+?\d+$", phone_number):
        return True

    if len(phone_number) > 15 or len(phone_number) < 8:
        return True

    return False


def flag_country(client: ClientData):
    if client.account_form["country"] != client.client_profile["country_of_domicile"]:
        return True
    return False


def flag_address(client: ClientData):
    address = client.client_profile[
        "address"
    ]  # i.e., "Place de la Concorde 17, 26627 Toulon"
    street, street_number, postal_code, city = "", "", "", ""
    if address:
        address_parts = address.split(",")
        if len(address_parts) >= 2:
            # First part contains street name and number: "Place de la Concorde 17"
            street_part = address_parts[0].strip()
            # Find the last word which should be the street number
            words = street_part.split()
            if words and words[-1].isdigit():
                street_number = words[-1]
                street = " ".join(words[:-1])
            else:
                # If no number is found at the end, assume entire string is street name
                street = street_part

            # Second part contains postal code and city: "26627 Toulon"
            location_part = address_parts[1].strip()
            location_words = location_part.split()
            nondigit_idxs = [
                i
                for i, x in enumerate(location_words)
                if not re.search(r"^[0-9-_/]+$", x)
            ]
            if location_words and nondigit_idxs:
                first_nondigit = nondigit_idxs[0]
                postal_code = " ".join(location_words[:first_nondigit])
                city = " ".join(location_words[first_nondigit:])
            else:
                postal_code = location_part

    # Log the parsed address for debugging
    logger.info(
        f"Parsed address: street='{street}', number='{street_number}', postal='{postal_code}', city='{city}'"
    )

    if to_ascii(street) != to_ascii(client.account_form["street_name"]):
        return True
    if street_number != client.account_form["building_number"]:
        return True
    if postal_code != client.account_form["postal_code"]:
        return True
    if to_ascii(city) != to_ascii(client.account_form["city"]):
        return True

    return False


def flag_inconsistent_name(client: ClientData):
    """
    Check if the name in the client profile and passport are inconsistent.
    """

    profile_last_name: str = remove_accents(
        client.client_profile.get("last_name").lower()
    )
    profile_given_name: str = remove_accents(
        client.client_profile.get("first_name").lower()
    )
    profile_full_name: str = remove_accents(
        " ".join([profile_given_name, profile_last_name]).lower().strip()
    )

    account_account_name: str = remove_accents(
        client.account_form.get("account_name").lower()
    )
    account_holder_name: str = remove_accents(
        client.account_form.get("account_holder_name").lower()
    )
    account_holder_surname: str = remove_accents(
        client.account_form.get("account_holder_surname").lower()
    )
    account_name: str = remove_accents(client.account_form.get("name").lower())

    passport_last_name: str = remove_accents(client.passport.get("last_name").lower())
    passport_first_name: str = remove_accents(client.passport.get("first_name").lower())
    passport_middle_name = client.passport.get("middle_name")

    ## null value safeguarding
    if passport_middle_name is not None:
        passport_given_name = remove_accents(
            " ".join([passport_first_name, passport_middle_name]).lower().strip()
        )
        if profile_given_name != passport_given_name:
            print(
                f"Given name mismatch: {profile_given_name=} !=  {passport_given_name=}"
            )
            return True

    else:
        passport_given_name = remove_accents(passport_first_name.strip())
        if profile_given_name[: len(passport_given_name)] != passport_given_name:
            print(
                f"Given name mismatch: {profile_given_name[:len(passport_given_name)]=} !=  {passport_given_name=}"
            )
            return True

    # account.json data consistency
    if account_account_name != account_name:
        print(f"Account name mismatch: {account_account_name=} != {account_name=}")
        return True

    if (
        account_account_name
        != (account_holder_name + " " + account_holder_surname).strip()
    ):
        print(
            f"Account name mismatch: {account_account_name=} != {account_holder_name} {account_holder_surname}"
        )
        return True

    # cross value consistency

    if profile_last_name != passport_last_name:
        print(f"Last name mismatch: {profile_last_name=} != {passport_last_name=}")
        return True

    if profile_full_name != account_name:
        print(f"Full name mismatch: {profile_full_name=} != {account_name=}")
        return True

    if passport_last_name != profile_last_name:
        print(f"Full name mismatch: {passport_last_name=} != {profile_last_name=}")
        return True

    return False


def simple_mrz(passport_data: dict) -> Tuple[str, str]:
    # Clean up passport data to remove accents and special characters
    last_name = remove_accents(passport_data["last_name"])
    first_name = remove_accents(passport_data["given_name"])

    names = first_name.split(" ")  # Take only the first part of the name
    first_name = names[0].strip()
    middle_name = ""
    if len(names) > 1:
        middle_name = " ".join(names[1:]).strip()

    line1 = [
        "P",
        f"{passport_data['country_code']}{last_name.upper()}",
        first_name.upper(),
    ]
    if middle_name != "":
        line1.append(middle_name.upper())

    birth_date = datetime.strptime(passport_data["birth_date"], "%Y-%m-%d").strftime(
        "%y%m%d"
    )
    line2 = f"{passport_data['passport_number'].upper()}{passport_data['country_code']}{birth_date}"
    return [l1.upper() for l1 in line1], line2.upper()


def flag_passport(client: ClientData):
    if not (
        client.client_profile["passport_id"]
        == client.account_form["passport_number"]
        == client.passport["passport_number"]
    ):
        return True

    if len(client.passport["passport_mrz"]) != 2:
        return True

    mrz_line1, mrz_line2 = simple_mrz(client.passport)

    passport_line1, passport_line2 = client.passport["passport_mrz"]
    passport_line1 = [s for s in passport_line1.split("<") if s]

    if mrz_line1 != passport_line1 or mrz_line2[:18] != passport_line2[:18]:
        print(mrz_line1, passport_line1)
        print(mrz_line2[:18], passport_line2[:18])
        return True

    if not re.match("\w\w\d{7}", client.passport["passport_number"]):
        return True

    return False


def flag_risk_profile(client: ClientData):
    if client.client_profile["account_details"]["risk_profile"] == "High":
        return True
    return False


# def flat_date_consistencies(client: ClientData):

#     for duplicate_field in (
#         "birth_date",
#         "passport_issue_date",
#         "passport_expiry_date",
#         "passport_number",
#     ):
#         if client.passport[duplicate_field] != client.client_profile[duplicate_field]:
#             return True

#     today = datetime.strptime("2025-04-01", "%Y-%m-%d").date()
#     birth_date = datetime.strptime(
#         client.client_profile["birth_date"], "%Y-%m-%d"
#     ).date()
#     passport_issue_date = datetime.strptime(
#         client.client_profile["passport_issue_date"], "%Y-%m-%d"
#     ).date()
#     passport_expiry_date = datetime.strptime(
#         client.client_profile["passport_expiry_date"], "%Y-%m-%d"
#     ).date()

#     secondary_school_grad = client.client_profile["secondary_school"]["graduation_year"]
#     higher_education_years = [
#         edu["graduation_year"] for edu in client.client_profile["higher_education"]
#     ]
#     employment_start_ends = [
#         (e["start_year"], e["end_year"])
#         for e in client.client_profile["employment_history"]
#     ]

#     try:
#         prev = 0
#         for start, end in employment_start_ends:
#             assert prev <= start  # TODO should be an error?

#         assert birth_date < passport_issue_date < passport_expiry_date
#         assert passport_issue_date < today
#         assert (
#             birth_date.year + 16 < employment_start_ends[0][0]
#             if employment_start_ends
#             else today.year
#         )
#         assert birth_date.year + 12 < secondary_school_grad
#         assert today.year - birth_date.year < 120
#         assert birth_date < date(secondary_school_grad, 1, 1) <= today
#         assert all(
#             date(secondary_school_grad, 1, 1) <= date(higher_edu, 1, 1) <= today
#             for higher_edu in higher_education_years
#         )
#         assert all(
#             birth_date
#             < date(start, 1, 1)
#             <= (date(end, 1, 1) if end else today)
#             <= today
#             for start, end in employment_start_ends
#         )
#     except AssertionError:
#         return True
#     return False


# def flag_dates(client: ClientData):
#     passport_issue_date = client.client_profile["passport_issue_date"]
#     if passport_issue_date != client.passport["passport_issue_date"]:
#         return True

#     date_pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
#     if not re.match(date_pattern, passport_issue_date):
#         return True

#     if passport_issue_date < client.client_profile["birth_date"]:
#         return True

#     if passport_issue_date > TODAY:
#         return True

#     if client.client_profile["birth_date"] > TODAY:
#         return True

#     if (len(client.client_profile["higher_education"]) > 0) and client.client_profile[
#         "higher_education"
#     ][0]["graduation_year"] < client.client_profile["secondary_school"][
#         "graduation_year"
#     ] + 2:
#         return True

#     return False


# def flag_wealth(client: ClientData):
#     real_state_value = client.client_profile["aum"]["real_estate_value"]
#     if (
#         sum([x["property value"] for x in client.client_profile["real_estate_details"]])
#         != real_state_value
#     ):
#         return True

#     return False
