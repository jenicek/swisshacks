from pathlib import Path
from dataclasses import dataclass
from client_data.client_profile import ClientProfile

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"


@dataclass
class ClientData:
    """Client data."""

    client_file: str  # identifier
    account_form: dict  # pdf
    client_description: dict  # txt
    client_profile: ClientProfile  # docx
    passport: dict  # png
    label: int | None = None  # may be none
