from pathlib import Path
from dataclasses import dataclass

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"
print(data_dir)

@dataclass
class ClientData:
    """Client data."""

    client_file: str
    account_form: dict
    client_description: dict
    client_profile: dict
    passport: dict
    label: int | None = None
