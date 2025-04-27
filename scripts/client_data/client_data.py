from pathlib import Path
from dataclasses import dataclass
from client_data.client_profile import ClientProfile
from client_data.client_account import ClientAccount

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"


@dataclass
class ClientData:
    """Client data."""

    client_file: str  # identifier
    account_form: ClientAccount  # pdf client account form
    client_description: dict  # txt
    client_profile: ClientProfile  # docx client profile
    passport: dict  # png
    label: int | None = None  # may be none
