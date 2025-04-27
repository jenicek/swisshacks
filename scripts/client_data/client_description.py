from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional
from datetime import datetime


@dataclass_json
@dataclass
class ClientDescription:
    # Client background information
    summary_note: Optional[str] = None
    family_background: Optional[str] = None
    education_background: Optional[str] = None
    occupation_history: Optional[str] = None
    wealth_summary: Optional[str] = None
    client_summary: Optional[str] = None
    
    # Metadata
    parsed_date: str = field(default_factory=lambda: datetime.now().isoformat())