from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum

class GenderEnum(Enum):
    MALE = "M"
    FEMALE = "F"


@dataclass_json
@dataclass
class ClientPassport:
    given_name: str
    surname: str
    sex: str
    birth_date: str
    citizenship: str
    issuing_country: str
    country_code: str
    number: str
    passport_mrz: list
    issue_date: str
    expiry_date: str
    signature: bool
    version: str = "2.0"
    
    def is_valid(self) -> bool:
        raise NotImplementedError("Passport validation logic not implemented.")
        