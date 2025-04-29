from dataclasses import dataclass, field
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
    issue_date: str
    expiry_date: str
    signature: bool
    passport_mrz: list = field(default_factory=list)
    version: str = "2.0"
    
    def validate_fields(self):       
        for name, dc_field in self.__dataclass_fields__.items():
            if not isinstance(self.__getattribute__(name), dc_field.type):
                raise TypeError(f"Field {name} is not of type {dc_field.type}")
        
    def is_valid(self) -> bool:
        try:
            self.validate_fields()
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            return False
        