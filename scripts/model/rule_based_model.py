from abc import ABC, abstractmethod
from client_data.client_data import ClientData
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("validation_debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("validation")


class Model(ABC):
    @abstractmethod
    def predict(self, client: ClientData) -> int:
        pass


class SimpleModel(Model):
    def predict(self, client: ClientData) -> int:
        if flag_missing_values(client):
            return 0
        if flag_verify_email(client):
            return 0
        if flag_phone(client):
            return 0
        return 1



def flag_missing_values(client: ClientData):

    NULLABLE_FIELDS = ("middle_name", "other_ccy", "employer", "position", "annual_income", "previous_profession", "is_primary", "source_info", "account_number", "expected_transactional_behavior")

    for data in (client.client_profile, client.client_description, client.passport, client.account_form):
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

    if phone_number != client.client_profile["contact_info"]["telephone"].replace(" ", ""):
        return True

    if not re.match("^\+?\d+$", phone_number):
        return True

    if len(phone_number) > 15 or len(phone_number) < 8:
        return True

    return False

