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
        return 1



def flag_missing_values(client: ClientData):

    NULLABLE_FIELDS = ("middle_name", "other_ccy", "employer", "position", "annual_income", "previous_profession", "is_primary", "source_info", "account_number", "expected_transactional_behavior")

    for data in (client.client_profile, client.client_description, client.passport, client.account_form):
        print(data)
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


