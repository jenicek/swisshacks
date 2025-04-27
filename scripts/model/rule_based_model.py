from client_data.client_data import ClientData
import re
import os
import logging
from datetime import datetime, date
from typing import Tuple
import unicodedata
import textdistance
from collections import defaultdict
import pycountry
from openai import AzureOpenAI
import json
from model.base_predictor import BasePredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("validation_debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("validation")


# def remove_accents(text):
#     # Normalize to NFKD form (decomposes characters)
#     nfkd_form = unicodedata.normalize("NFKD", text)
#     # Filter out diacritical marks
#     only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
#     return only_ascii


def remove_accents(input_str) -> str:
    # Normalize to NFKD form and encode to ASCII bytes, ignoring non-ASCII chars
    normalized = unicodedata.normalize("NFKD", input_str)
    ascii_bytes = normalized.encode("ASCII", "ignore")
    return ascii_bytes.decode("ASCII")


class SimpleModel(BasePredictor):
    def predict(self, client: ClientData) -> int:
        # Missing value check is already done in the client_data class
        if flag_verify_email(client):
            print("Email mismatch")
            return 0
        if flag_phone(client):
            print("Phone number mismatch")
            return 0
        if flag_country(client):
            print("Country mismatch")
            return 0
        if flag_inconsistent_name(client):
            return 0
        if flag_passport(client):
            print("Passport mismatch")
            return 0
        if flag_address(client):
            print("Address mismatch")
            return 0
        if flag_birth_date(client):
            print("Birth date mismatch")
            return 0
        if flag_nationality(client):
            print("Nationality mismatch")
            return 0
        if flat_date_consistencies(client):
            print("Date inconsistencies detected")
            return 0
        if flag_wealth(client):
            print("Wealth inconsistencies detected")
            return 0
        if flag_gender(client):
            print("Gender mismatch")
            return 0
        if flat_date_consistencies(client):
            print("Date inconsistencies detected")
            return 0
        if flag_description(client):
            print("Description mismatch")
            return 0
        if flag_passport_country_code(client):
            print("Passport country code mismatch")
            return 0
        # If all checks pass, return 1
        return 1 


def flag_gender(client: ClientData) -> bool:
    if client.client_profile.gender[0] != client.passport.gender:
        return True
    return False


def flag_passport_country_code(client: ClientData) -> bool:
    passport_country_code = client.passport.country_code
    passport_country_name = client.passport.country

    if len(passport_country_code) != 3:
        print("Passport country code is incorrect!")
        return True

    pycntry_country_code = pycountry.countries.get(alpha_3=passport_country_code)
    if not pycntry_country_code:
        print(f"Country code {passport_country_code} is not valid.")
        return True

    pycountry_country_fz_name = pycountry.countries.search_fuzzy(passport_country_name)

    if pycountry_country_fz_name:
        if pycountry_country_fz_name[0] != pycntry_country_code:
            print(
                f"Country name {passport_country_name} does not match country code {passport_country_code}"
            )
            return True

    return False


def flag_verify_email(client: ClientData) -> bool:
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    # Check if the email in the account form matches the one in the client profile
    if client.account_form.email != client.client_profile.contact_info.email:
        return True
    if not re.match(email_pattern, client.account_form.email):
        return True
    return False


def flag_phone(client: ClientData) -> bool:
    phone_number = client.account_form.phone_number.replace(" ", "")

    if phone_number != client.client_profile.contact_info.telephone.replace(" ", ""):
        return True
    # Check if the phone number contains only digits and optional leading '+'
    if not re.match("^\+?\d+$", phone_number):
        return True
    # Check if the phone number is too long or too short
    if len(phone_number) > 15 or len(phone_number) < 8:
        return True
    return False


def flag_country(client: ClientData) -> bool:
    if client.account_form.country != client.client_profile.country_of_domicile:
        return True
    return False


def flag_nationality(client: ClientData) -> bool:
    passport_nationality = client.passport.nationality.lower()
    profile_nationality = client.client_profile.nationality.lower()

    if len(passport_nationality) == len(profile_nationality):
        if passport_nationality != profile_nationality:
            print(
                f"Client nationality mismatch: {client.passport.nationality} != {client.client_profile.nationality}"
            )
            return True
    else:
        if profile_nationality not in passport_nationality:
            print(
                f"Profile nationality {profile_nationality} does not match {passport_nationality}"
            )
            return True
    return False


def flag_address(client: ClientData):
    address = client.client_profile.address  # i.e., "Place de la Concorde 17, 26627 Toulon"
    street, street_number, postal_code, city = "", "", "", ""
    if address:
        address_parts = address.split(",")
        if len(address_parts) >= 2:
            # First part contains street name and number: "Place de la Concorde 17"
            street_part = address_parts[0].strip()
            # Find the last word which should be the street number
            words = street_part.split()
            if words and words[-1].isdigit():
                street_number = words[-1]
                street = " ".join(words[:-1])
            else:
                # If no number is found at the end, assume entire string is street name
                street = street_part

            # Second part contains postal code and city: "26627 Toulon"
            location_part = address_parts[1].strip()
            location_words = location_part.split()
            nondigit_idxs = [
                i
                for i, x in enumerate(location_words)
                if not re.search(r"^[0-9-_/]+$", x)
            ]
            if location_words and nondigit_idxs:
                first_nondigit = nondigit_idxs[0]
                postal_code = " ".join(location_words[:first_nondigit])
                city = " ".join(location_words[first_nondigit:])
            else:
                postal_code = location_part

    # Log the parsed address for debugging
    # logger.info(
    #     f"Parsed address: street='{street}', number='{street_number}', postal='{postal_code}', city='{city}'"
    # )

    if remove_accents(street) != remove_accents(client.account_form.street_name):
        return True
    if street_number != client.account_form.building_number:
        return True
    if postal_code != client.account_form.postal_code:
        return True
    if remove_accents(city) != remove_accents(client.account_form.city):
        return True

    return False


def flag_inconsistent_name(client: ClientData):
    """
    Check if the name in the client profile and passport are inconsistent.
    """

    profile_last_name: str = remove_accents(
        client.client_profile.last_name.lower()
    )
    profile_given_name: str = remove_accents(
        client.client_profile.first_name.lower()
    )
    profile_full_name: str = remove_accents(
        " ".join([profile_given_name, profile_last_name]).lower().strip()
    )

    account_account_name: str = remove_accents(
        client.account_form.account_name.lower()
    )
    account_holder_name: str = remove_accents(
        client.account_form.account_holder_name.lower()
    )
    account_holder_surname: str = remove_accents(
        client.account_form.account_holder_surname.lower()
    )
    account_name: str = remove_accents(client.account_form.name.lower())

    passport_last_name: str = remove_accents(client.passport.last_name.lower())
    passport_given_name: str = remove_accents(client.passport.given_name.lower())

    # account.json data consistency
    if account_account_name != account_name:
        print(f"Account name mismatch: {account_account_name=} != {account_name=}")
        return True

    if (
        account_account_name
        != (account_holder_name + " " + account_holder_surname).strip()
    ):
        print(
            f"Account name mismatch: {account_account_name=} != {account_holder_name} {account_holder_surname}"
        )
        return True

    # cross value consistency

    if profile_last_name != passport_last_name:
        print(f"Last name mismatch: {profile_last_name=} != {passport_last_name=}")
        return True

    if profile_full_name != account_name:
        print(f"Full name mismatch: {profile_full_name=} != {account_name=}")
        return True

    if passport_given_name != account_holder_name:
        print(f"Given name mismatch: {passport_given_name=} != {account_holder_name=}")
        return True

    if passport_last_name != profile_last_name:
        print(f"Full name mismatch: {passport_last_name=} != {profile_last_name=}")
        return True

    return False


def simple_mrz(passport_data: dict) -> Tuple[str, str]:
    # Clean up passport data to remove accents and special characters
    last_name = remove_accents(passport_data.last_name)
    first_name = remove_accents(passport_data.given_name)

    names = first_name.split(" ")  # Take only the first part of the name
    first_name = names[0].strip()
    middle_name = ""
    if len(names) > 1:
        middle_name = " ".join(names[1:]).strip()

    line1 = [
        "P",
        f"{passport_data.country_code}{last_name.upper()}",
        first_name.upper(),
    ]
    if middle_name != "":
        line1.append(middle_name.upper())

    birth_date = datetime.strptime(passport_data.birth_date, "%Y-%m-%d").strftime(
        "%y%m%d"
    )
    line2 = f"{passport_data.passport_number.upper()}{passport_data.country_code}{birth_date}"
    return [remove_accents(l1.upper()) for l1 in line1], line2.upper()


def flag_passport(client: ClientData):
    if not (
        client.client_profile.passport_id
        == client.account_form.passport_number
        == client.passport.passport_number
    ):
        print(
            f"Passport numbers are not matching: {client.client_profile.passport_id} != {client.account_form.passport_number} != {client.passport.passport_number}"
        )
        return True

    if len(client.passport.passport_mrz) != 2:
        print("MRZ not in prescribed format")
        return True

    mrz_line1, mrz_line2 = simple_mrz(client.passport)

    passport_line1, passport_line2 = client.passport.passport_mrz
    passport_line1 = [remove_accents(s.upper()) for s in passport_line1.split("<") if s]

    if (
        textdistance.levenshtein(" ".join(mrz_line1), " ".join(passport_line1)) > 1
        or textdistance.levenshtein(mrz_line2[:18], passport_line2[:18]) > 2
    ):
        print(mrz_line1, passport_line1)
        print(mrz_line2[:18], passport_line2[:18])
        return True

    if not re.match("\w\w\d{7}", client.passport.passport_number):
        return True

    return False

def flag_birth_date(client: ClientData):
    # Check if birth dates match between client profile and passport
    if client.client_profile.birth_date != client.passport.birth_date:
        print(
            f"Birth date mismatch: {client.client_profile.birth_date} != {client.passport.birth_date}"
        )
        return True

    passport_issue_date = client.passport.passport_issue_date
    passport_expiry_date = client.passport.passport_expiry_date

    if client.client_profile.id_type == "passport":
        if passport_issue_date != client.client_profile.id_issue_date:
            print(
                f"Passport issue date mismatch: {passport_issue_date} != {client.client_profile.id_issue_date}"
            )
            return True

        if passport_expiry_date != client.client_profile.id_expiry_date:
            print(
                f"Passport expiry date mismatch: {passport_expiry_date} != {client.client_profile.id_expiry_date}"
            )
            return True

    today = datetime.strptime("2025-04-13", "%Y-%m-%d").date()

    if (
        datetime.strptime(passport_issue_date, "%Y-%m-%d").date()
        > datetime.strptime(passport_expiry_date, "%Y-%m-%d").date()
    ):
        print(
            f"Passport issue date {passport_issue_date} is after expiry date {passport_expiry_date}"
        )
        return True
    if (
        datetime.strptime(passport_issue_date, "%Y-%m-%d").date()
        < datetime.strptime(client.client_profile.birth_date, "%Y-%m-%d").date()
    ):
        print(
            f"Passport issue date {passport_issue_date} is before birth date {client.client_profile.birth_date}"
        )
        return True
    if (
        datetime.strptime(passport_expiry_date, "%Y-%m-%d").date()
        < datetime.strptime(client.client_profile.birth_date, "%Y-%m-%d").date()
    ):
        print(
            f"Passport expiry date {passport_expiry_date} is before birth date {client.client_profile.birth_date}"
        )
        return True
    if datetime.strptime(passport_issue_date, "%Y-%m-%d").date() > today:
        print(f"Passport issue date {passport_issue_date} is in the future")
        return True
    if datetime.strptime(passport_expiry_date, "%Y-%m-%d").date() < today:
        print(f"Passport expiry date {passport_expiry_date} is in the past")
        return True

    try:
        birth_date = datetime.strptime(
            client.client_profile.birth_date, "%Y-%m-%d"
        ).date()

        # Calculate age
        if birth_date > today:
            logger.info("Birth date is in the future")
            return True
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        # Check if age is reasonable (typically 18-120 years for banking clients)
        if age < 18:
            logger.info(f"Client is too young: {age} years old")
            return True
        if age > 120:
            logger.info(f"Client age is unrealistic: {age} years old")
            return True
    except ValueError:
        # If there's an issue parsing the date
        logger.error(
            f"Invalid birth date format: {client.client_profile.birth_date}"
        )
        return True

    return False


def find_redundant_sentences(data_dict):
    sentence_map = defaultdict(set)

    # Helper: normalize a sentence
    def clean_sentence(sentence):
        return re.sub(r"\s+", " ", sentence.strip()).rstrip(".")

    # Step 1: Split and map sentences to fields
    for field, content in data_dict.items():
        sentences = re.split(r"(?<=[.!?])\s+", content)
        for raw_sentence in sentences:
            sentence = clean_sentence(raw_sentence)
            if sentence:
                sentence_map[sentence].add(field)

    # Step 2: Find duplicates (appearing in >1 field)
    redundant_sentences = {
        sentence: fields for sentence, fields in sentence_map.items() if len(fields) > 1
    }

    return redundant_sentences


def flat_date_consistencies(client: ClientData):
    for field1, field2 in (
        ("birth_date", "birth_date"),
        ("passport_issue_date", "id_issue_date"),
        ("passport_expiry_date", "id_expiry_date"),
        ("passport_number", "passport_id"),
    ):
        if client.passport[field1] != client.client_profile[field2]:
            return True

    today = datetime.strptime("2025-04-13", "%Y-%m-%d").date()
    birth_date = datetime.strptime(
        client.client_profile.birth_date, "%Y-%m-%d"
    ).date()
    issue_date = datetime.strptime(
        client.client_profile.id_issue_date, "%Y-%m-%d"
    ).date()
    expiry_date = datetime.strptime(
        client.client_profile.id_expiry_date, "%Y-%m-%d"
    ).date()

    # TODO: validate dates from key "employment"

    if not birth_date < issue_date < today:
        return True
    if not issue_date < expiry_date:
        return True
    if not 18 <= today.year - birth_date.year < 120:
        return True
    return False


# TODO: check correct dates (i.e., work since <today, graduation_year < today)
# TODO: Check passport dates are reasonable; (not too far in the past, not too far in the future)
# TODO: Check valid passport


def flag_wealth(client: ClientData):
    total_assets = client.client_profile.account_details.total_assets
    transfer_assets = client.client_profile.account_details.transfer_assets

    if total_assets < 0 or transfer_assets < 0:
        print("Negative assets detected")
        return True
    if transfer_assets > total_assets:
        print("Transfer assets exceed total assets")
        return True

    combined_assets = 0
    for _, value in client.client_profile.wealth_info.assets.items():
        value = int(value)
        if value < 0:
            return True
        combined_assets += value

    if combined_assets > total_assets:
        print(
            f"Combined assets exceed total assets: {combined_assets} > {total_assets}"
        )
        return True

    total_wealth_range = client.client_profile.wealth_info.total_wealth_range
    # "< EUR 1.5m", "EUR 1.5m-5m", "EUR 5m-10m", "EUR 10m.-20m", "EUR 20m.-50m", "> EUR 50m"

    # Check if the total assets fall within the specified range
    total_wealth_range = total_wealth_range.replace(" ", "")
    if total_wealth_range == "< EUR 1.5m" and combined_assets > 1_500_000:
        return True
    elif total_wealth_range == "EUR 1.5m-5m" and (
        1_500_000 > combined_assets or combined_assets > 5_000_000
    ):
        return True
    elif total_wealth_range == "EUR 5m-10m" and (
        5_000_000 > combined_assets or combined_assets > 10_000_000
    ):
        return True
    elif total_wealth_range == "EUR 10m.-20m" and (
        10_000_000 > combined_assets or combined_assets > 20_000_000
    ):
        return True
    elif total_wealth_range == "EUR 20m.-50m" and (
        20_000_000 > combined_assets or combined_assets > 50_000_000
    ):
        return True
    elif total_wealth_range == "> EUR 50m" and combined_assets <= 50_000_000:
        return True

    return False


prompt = """
I have this json:
{client_data}

fill these keys:
{{
    "age": age,
    "marital_status": single / married / divorced / widowed
    "education": 
           {{
                 "university": university,
                 "graduation_year": graduation_year
           }}
    ,
    "employment": 
    {{
        "company": company,
        "position": position
    }}
    ,
    "savings": savings,
    "inheritance": boolean inheritance (1 word, i.e., true, false),
    "inherited_from": inherited_from (1 word, i.e., grandmother, father, mother, uncle, aunt, etc.),
    "inheritment_year": inheritment_year (YYYY),
    "occupation_of_the_person_from_whom_inherited": occupation_of_the_person_from_whom_inherited,
}}
 DONT infer data, just use whats there.
 Missing values should be marked with empty string ""
 Denominations, dimensions for prices and numbers should be ignored. just put the number e.g 15000 and NOT 15000 EUR. marital status should be 1 word, e.g. single, married, divorced, widowed
 output should be a valid json with the given template. just fill the values, nothing else. 
"""


def flag_compare_age(gpt_age, client: ClientData):
    if gpt_age in (None, "", "none", "None"):
        return False
    gpt_age = int(gpt_age)
    today = date.today()

    birth_date = datetime.strptime(
        client.client_profile.birth_date, "%Y-%m-%d"
    ).date()

    birthday_age = today.year - birth_date.year

    return abs(gpt_age - birthday_age) > 2


def simple_compare(gpt_value, client_value):
    if gpt_value in (None, "", "none", "None"):
        return False
    gpt_value = str(gpt_value).lower()
    client_value = str(client_value).lower()

    return gpt_value != client_value


def flag_description(client: ClientData):
    openai_client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2025-03-01-preview",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt.format(client_data=client.client_description),
            }
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    try:
        response_data = json.loads(response.choices[0].message.content)
    except json.decoder.JSONDecodeError:
        return False

    print(response_data)

    if flag_compare_age(response_data.get("age"), client):
        print(
            f"age mismatch: {response_data.get('age')} != {client.client_profile.birth_date}"
        )
        return True

    if simple_compare(
        response_data.get("marital_status"),
        client.client_profile.personal_info.marital_status,
    ):
        print(
            f"marital status mismatch: {response_data.get('marital_status')} != {client.client_profile.personal_info.marital_status}"
        )
        return True

    if simple_compare(
        response_data.get("company"), client.client_profile.employment[0]["employer"]
    ):
        print(
            f"company mismatch: {response_data.get('company')} != {client.client_profile.employment[0]['employer']}"
        )
        return True

    if simple_compare(
        response_data.get("position"),
        client.client_profile.employment[0]["position"],
    ):
        print(
            f"position mismatch: {response_data.get('position')} != {client.client_profile.employment[0]['position']}"
        )
        return True

    inheritance = response_data.get("inheritance")
    if isinstance(inheritance, str):
        inheritance = inheritance.lower() == "true"

    wealth_sources = client.client_profile.wealth_info.wealth_sources
    inherit_profile = "Inheritance" in wealth_sources
    if inheritance != inherit_profile and response_data.get("inherited_from"):
        print(f"inheritance mismatch: {inheritance} != {inherit_profile}")
        return True

    # Inheritance source
    if inheritance:
        inh_from = response_data.get("inherited_from")
        inh_year = response_data.get("inheritment_year")
        inh_pos = response_data.get("occupation_of_the_person_from_whom_inherited")

        inh_info = client.client_profile.wealth_info.source_info
        if inh_from and inh_from not in inh_info[0]:
            print(f"inheritance source mismatch: {inh_from} != {inh_info}")
            return True
        if inh_year and str(inh_year) not in inh_info[0]:
            print(f"inheritance year mismatch: {inh_year} != {inh_info}")
            return True
        if inh_pos and inh_pos not in inh_info[0]:
            print(f"inheritance position mismatch: {inh_pos} != {inh_info}")
            return True

        # # Education
        # education = response_data.get('education')

        # if education:
        #     edu_prof = client.client_profile.personal_info.education_history
        #     

    # except Exception as e:
    #     logger.error(f"Error processing response: {e}")
    #     return False

    return False
