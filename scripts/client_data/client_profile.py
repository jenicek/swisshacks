from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"

class EmploymentType(Enum):
    EMPLOYEE = "Employee"
    SELF_EMPLOYED = "Self-Employed"
    NOT_EMPLOYED = "Currently not employed"
    RETIRED = "Retired"
    STUDENT = "Student"
    DIPLOMAT = "Diplomat"
    MILITARY_REPRESENTATIVE = "Military representative"


class MaritalStatus(Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"


class RiskProfile(Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    CONSIDERABLE = "Considerable"
    HIGH = "High"


class MandateType(Enum):
    DISCRETIONARY = "Discretionary"
    ADVISORY = "Advisory"


class InvestmentExperience(Enum):
    INEXPERIENCED = "Inexperienced"
    EXPERIENCED = "Experienced"
    EXPERT = "Expert"


class InvestmentHorizon(Enum):
    SHORT_TERM = "Short"
    MEDIUM_TERM = "Medium"
    LONG_TERM = "Long-term"


@dataclass_json
@dataclass
class ContactInfo:
    telephone: Optional[str] = None
    email: Optional[str] = None


@dataclass_json
@dataclass
class PersonalInfo:
    is_politically_exposed: bool = False
    marital_status: Optional[MaritalStatus] = None
    highest_education: Optional[str] = None
    education_history: Optional[str] = None


@dataclass_json
@dataclass
class EmploymentStatus:
    status_type: Optional[EmploymentType] = None
    since: Optional[str] = None


@dataclass_json
@dataclass
class Employment:
    current_status: EmploymentStatus = field(default_factory=EmploymentStatus)
    employer: Optional[str] = None
    position: Optional[str] = None
    annual_income: Optional[str] = None
    previous_profession: Optional[str] = None
    is_primary: bool = True


@dataclass_json
@dataclass
class WealthInfo:
    total_wealth_range: Optional[str] = None
    wealth_sources: List[str] = field(default_factory=list)
    source_info: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)


@dataclass_json
@dataclass
class IncomeInfo:
    total_income_range: Optional[str] = None
    source_info: Optional[str] = None


@dataclass_json
@dataclass
class InvestmentPreferences:
    type_of_mandate: Optional[MandateType] = None
    investment_experience: Optional[InvestmentExperience] = None
    investment_horizon: Optional[InvestmentHorizon] = None
    expected_transactional_behavior: Optional[str] = None
    preferred_markets: List[str] = field(default_factory=list)


@dataclass_json
@dataclass
class AccountDetails:
    account_number: Optional[str] = None
    is_commercial_account: bool = False
    risk_profile: Optional[RiskProfile] = None
    total_assets: Optional[float] = None
    transfer_assets: Optional[float] = None
    investment_preferences: InvestmentPreferences = field(
        default_factory=InvestmentPreferences
    )


@dataclass_json
@dataclass
class ClientProfile:
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    nationality: Optional[str] = None
    passport_id: Optional[str] = None
    id_type: Optional[str] = None
    id_issue_date: Optional[str] = None
    id_expiry_date: Optional[str] = None
    gender: Optional[Gender] = None
    country_of_domicile: Optional[str] = None
    birth_date: Optional[str] = None

    address: Optional[str] = None
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    employment: List[Employment] = field(default_factory=list)
    wealth_info: WealthInfo = field(default_factory=WealthInfo)
    income_info: IncomeInfo = field(default_factory=IncomeInfo)
    account_details: AccountDetails = field(default_factory=AccountDetails)

    # Metadata
    parsed_date: str = field(default_factory=lambda: datetime.now().isoformat())
