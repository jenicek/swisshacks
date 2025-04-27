from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional
from datetime import datetime


@dataclass_json
@dataclass
class SignatureFields:
    specimen_signature: bool = False
    _signature_fields: bool = False


@dataclass_json
@dataclass
class ClientAccount:
    # Account holder information
    account_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_holder_surname: Optional[str] = None
    passport_number: Optional[str] = None
    
    # Currency preferences
    chf: bool = False
    eur: bool = False
    usd: bool = False
    other_ccy: Optional[str] = None
    
    # Address information
    building_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    street_name: Optional[str] = None
    
    # Contact information
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    
    # Signature information
    _signature_fields: SignatureFields = field(default_factory=SignatureFields)
    
    # Metadata
    parsed_date: str = field(default_factory=lambda: datetime.now().isoformat())