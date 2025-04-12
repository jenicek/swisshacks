from pathlib import Path
from dataclasses import dataclass

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"
<<<<<<< HEAD
print(data_dir)
=======
>>>>>>> d61c4347120d85ccaa848ca661b5c4386a65188d

@dataclass
class ClientData:
    """Client data."""

    client_file: str
    account_form: dict
    client_description: dict
    client_profile: dict
    passport: dict
<<<<<<< HEAD
    label: int | None = None
=======
    label: int | None = None
>>>>>>> d61c4347120d85ccaa848ca661b5c4386a65188d
