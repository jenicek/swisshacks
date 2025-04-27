from pathlib import Path
from dataclasses import dataclass
from client_data.client_profile import ClientProfile
from client_data.client_account import ClientAccount
from client_data.client_description import ClientDescription
from client_data.client_passport import ClientPassport

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
    client_description: ClientDescription
    # Parsed client profile data (from docx).
    client_profile: ClientProfile
    # Parsed passport data (from png).
    passport: ClientPassport
    # Label (0 or 1) corresponding to the ground truth information used
    # for training. May be none.
    label: int | None = None

    def __post_init__(self):
        assert self.account_form is not None, "Account form cannot be None"
        assert self.client_description is not None, "Client description cannot be None"
        assert self.client_profile is not None, "Client profile cannot be None"
        assert self.passport is not None, "Passport cannot be None"

        assert self.account_form.is_valid(), "Account form is not valid"
        assert self.client_description.is_valid(), "Client description is not valid"
        assert self.client_profile.is_valid(), "Client profile is not valid"
        # assert self.passport.is_valid(), "Passport is not valid"