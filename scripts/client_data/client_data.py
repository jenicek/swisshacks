from pathlib import Path
from dataclasses import dataclass
from client_data.client_profile import ClientProfile
from client_data.client_account import ClientAccount

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"


@dataclass
class ClientData:
    """Client data."""

    # Client identifier.
    client_file: str
    # Parsed client account data (from pdf).
    account_form: ClientAccount
    # Parsed client account data (from txt).
    client_description: dict
    # Parsed client profile data (from docx).
    client_profile: ClientProfile
    # Parsed passport data (from png).
    passport: dict
    # Label corresponding to the ground truth information used for training.
    # May be none.
    label: int | None = None
