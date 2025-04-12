from abc import ABC, abstractmethod
from client_data.client_data import ClientData
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("validation")


class Model(ABC):
    @abstractmethod
    def predict(self, client: ClientData) -> int:
        pass


class SimpleModel(Model):
    def predict(self, client_data: ClientData) -> int:
        # Dictionary to store validation results
        validation_results = {
            "missing_values": flag_missing_values(client_data),
            "data_inconsistencies": check_data_inconsistencies(client_data),
            "wealth_inconsistencies": check_wealth_inconsistencies(client_data),
            "employment_inconsistencies": check_employment_inconsistencies(client_data),
            "education_inconsistencies": check_education_inconsistencies(client_data),
            "family_inconsistencies": check_family_inconsistencies(client_data),
            "country_inconsistencies": check_country_inconsistencies(client_data)
        }
        
        # Log overall validation results
        client_id = client_data.client_file.split('/')[-1] if client_data.client_file else "unknown"
        logger.info(f"Validation results for {client_id}:")
        for rule, result in validation_results.items():
            status = "FAILED" if result else "PASSED"
            logger.info(f"  {rule}: {status}")
        
        # Return 0 (invalid) if any validation fails, 1 (valid) otherwise
        if any(validation_results.values()):
            return 0
        return 1
    

def flag_missing_values(client_data: ClientData):
    """
    Check for missing or empty required fields in client data.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are missing required values, False otherwise
    """
    # Fields that can be null/empty without raising a flag
    NULLABLE_FIELDS = ("other_ccy", "account_number", "expected_transactional_behavior", 
                       "previous_profession", "since", "employer", "position", "annual_income")
    
    missing_values = []

    # Check profile data
    for key, value in client_data.client_profile.items():
        # Skip metadata fields
        if key in ("filename", "parsed_date"):
            continue
            
        # Handle nested dictionaries
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in NULLABLE_FIELDS and (sub_value is None or sub_value == ""):
                    missing_values.append(f"profile.{key}.{sub_key}")
        # Handle lists of dictionaries (like employment)
        elif isinstance(value, list) and value:
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    for item_key, item_value in item.items():
                        # Check nested dictionaries within lists
                        if isinstance(item_value, dict):
                            for nested_key, nested_value in item_value.items():
                                if nested_key not in NULLABLE_FIELDS and (nested_value is None or nested_value == ""):
                                    missing_values.append(f"profile.{key}[{i}].{item_key}.{nested_key}")
                        elif item_key not in NULLABLE_FIELDS and (item_value is None or item_value == ""):
                            missing_values.append(f"profile.{key}[{i}].{item_key}")
        # Check direct values
        elif key not in NULLABLE_FIELDS and (value is None or value == ""):
            missing_values.append(f"profile.{key}")
    
    # Check passport data
    for key, value in client_data.passport.items():
        if key not in NULLABLE_FIELDS and (value is None or value == ""):
            missing_values.append(f"passport.{key}")
    
    # Check account data
    for key, value in client_data.account_form.items():
        # Skip signature fields
        if key == "_signature_fields":
            continue
        if key not in NULLABLE_FIELDS and (value is None or value == ""):
            missing_values.append(f"account.{key}")
    
    # Check description data (this is usually free text and can vary)
    required_description_sections = ("Summary Note", "Family Background", "Education Background", 
                                    "Occupation History", "Wealth Summary", "Client Summary")
    
    for section in required_description_sections:
        if section not in client_data.client_description or not client_data.client_description[section]:
            missing_values.append(f"description.{section}")
    
    if missing_values:
        logger.warning(f"Missing values detected: {', '.join(missing_values)}")
        return True
    
    return False


def check_data_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies between different data sources.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies between data sources, False otherwise
    """
    inconsistencies = []
    
    # Check passport number consistency
    passport_id = client_data.client_profile.get("passport_id")
    passport_number_account = client_data.account_form.get("passport_number")
    passport_number_passport = client_data.passport.get("passport_number")
    
    if passport_id and passport_number_account and not are_strings_ocr_equivalent(passport_id, passport_number_account):
        inconsistencies.append(f"Passport number mismatch: profile '{passport_id}' vs account '{passport_number_account}'")
    
    if passport_id and passport_number_passport and not are_strings_ocr_equivalent(passport_id, passport_number_passport):
        inconsistencies.append(f"Passport number mismatch: profile '{passport_id}' vs passport '{passport_number_passport}'")
    
    # Check name consistency
    first_name = client_data.client_profile.get("first_name", "")
    last_name = client_data.client_profile.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()
    
    account_name = client_data.account_form.get("account_name", "")
    passport_given_name = client_data.passport.get("given_name", "")
    passport_surname = client_data.passport.get("surname", "")
    
    # Check profile name against account name
    if full_name and account_name and not are_names_similar(full_name, account_name):
        inconsistencies.append(f"Name mismatch: profile '{full_name}' vs account '{account_name}'")
    
    # Check profile name against passport name
    if first_name and passport_given_name and not are_names_similar(first_name, passport_given_name):
        inconsistencies.append(f"First name mismatch: profile '{first_name}' vs passport '{passport_given_name}'")
    
    if last_name and passport_surname and not are_names_similar(last_name, passport_surname):
        inconsistencies.append(f"Last name mismatch: profile '{last_name}' vs passport '{passport_surname}'")
    
    # Check address consistency
    profile_address = client_data.client_profile.get("address", "")
    if profile_address:
        street = client_data.account_form.get("street_name", "")
        building = client_data.account_form.get("building_number", "")
        postal = client_data.account_form.get("postal_code", "")
        city = client_data.account_form.get("city", "")
        
        address_components = []
        if street:
            address_components.append((street, "street"))
        if building:
            address_components.append((building, "building number"))
        if postal:
            address_components.append((postal, "postal code"))
        if city:
            address_components.append((city, "city"))
            
        for component, component_type in address_components:
            if component not in profile_address and not are_strings_similar(component, profile_address):
                inconsistencies.append(f"Address component mismatch: {component_type} '{component}' not found in profile address")
    
    # Check contact information consistency
    profile_phone = client_data.client_profile.get("contact_info", {}).get("telephone", "")
    account_phone = client_data.account_form.get("phone_number", "")
    
    profile_email = client_data.client_profile.get("contact_info", {}).get("email", "")
    account_email = client_data.account_form.get("email", "")
    
    if profile_phone and account_phone and not are_strings_similar(profile_phone, account_phone):
        inconsistencies.append(f"Phone number mismatch: profile '{profile_phone}' vs account '{account_phone}'")
        
    if profile_email and account_email and not are_strings_similar(profile_email, account_email):
        inconsistencies.append(f"Email mismatch: profile '{profile_email}' vs account '{account_email}'")
    
    # Check birth date consistency (passport may have different format)
    try:
        profile_birth_date = client_data.client_profile.get("birth_date", "")
        passport_birth_date = client_data.passport.get("birth_date", "")
        
        if profile_birth_date and passport_birth_date:
            if not are_dates_ocr_equivalent(profile_birth_date, passport_birth_date):
                inconsistencies.append(f"Birth date mismatch: profile '{profile_birth_date}' vs passport '{passport_birth_date}'")
    except (IndexError, AttributeError) as e:
        inconsistencies.append(f"Birth date comparison error: {str(e)}")
    
    if inconsistencies:
        logger.warning(f"Data inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def check_wealth_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies in wealth information between profile and description.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies in wealth information, False otherwise
    """
    inconsistencies = []
    
    description_wealth = client_data.client_description.get("Wealth Summary", "")
    profile_wealth_sources = client_data.client_profile.get("wealth_info", {}).get("wealth_sources", [])
    profile_source_info = client_data.client_profile.get("wealth_info", {}).get("source_info", [])
    
    # Check inheritance information
    has_inheritance_in_profile = "Inheritance" in profile_wealth_sources
    has_inheritance_in_description = "inheritance" in description_wealth.lower() or "inherited" in description_wealth.lower()
    
    # if has_inheritance_in_profile != has_inheritance_in_description:
    #     inconsistencies.append(f"Inheritance mismatch: profile has inheritance: {has_inheritance_in_profile}, description mentions inheritance: {has_inheritance_in_description}")
    
    # Check if inheritance details match between sources
    if has_inheritance_in_profile and profile_source_info:
        # Extract inheritance details from profile
        for source in profile_source_info:
            parts = source.split(',')
            if len(parts) >= 3:
                relation, year, occupation = parts[0], parts[1], parts[2]
                
                # Check if these details are mentioned in the description
                if relation not in description_wealth.lower() and occupation not in description_wealth:
                    inconsistencies.append(f"Inheritance detail mismatch: relation '{relation}' or occupation '{occupation}' not mentioned in description")
                
                # Check if year is mentioned in description
                if year not in description_wealth:
                    inconsistencies.append(f"Inheritance year mismatch: year '{year}' not mentioned in description")
    
    # Check if amount information matches
    try:
        # Extract monetary amounts from description
        amounts_in_description = re.findall(r'(\d[\d\s,.]*\d)\s*([A-Z]{3})', description_wealth)
        
        # Get total assets from profile
        total_assets = client_data.client_profile.get("account_details", {}).get("total_assets")
        
        if total_assets is not None and amounts_in_description:
            # Compare magnitudes (rough check)
            description_amounts = []
            for amount, currency in amounts_in_description:
                # Clean up amount (remove spaces, replace commas with dots)
                clean_amount = amount.replace(" ", "").replace(",", "")
                try:
                    description_amounts.append((float(clean_amount), currency))
                except ValueError:
                    continue
            
            # If we have extracted amounts from description and they're significantly different from profile
            # for amount, currency in description_amounts:
            #     if abs(total_assets - amount) / max(total_assets, amount) > 0.2:  # 20% tolerance
            #         inconsistencies.append(f"Wealth amount mismatch: profile has {total_assets}, description mentions {amount} {currency}")
    except (ValueError, TypeError) as e:
        inconsistencies.append(f"Wealth amount comparison error: {str(e)}")
    
    if inconsistencies:
        logger.warning(f"Wealth inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def check_employment_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies in employment information between profile and description.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies in employment information, False otherwise
    """
    inconsistencies = []
    
    # Extract employment info from profile
    employment_list = client_data.client_profile.get("employment", [])
    description_occupation = client_data.client_description.get("Occupation History", "")
    
    if not employment_list or not description_occupation:
        return False
    
    # Get current employment status
    current_status = None
    employer = None
    position = None
    annual_income = None
    
    if employment_list:
        employment = employment_list[0]
        current_status = employment.get("current_status", {}).get("status_type", "")
        employer = employment.get("employer", "")
        position = employment.get("position", "")
        annual_income = employment.get("annual_income")
    
    # Check for employment status consistency
    # if current_status:
    #     status_pattern = ""
    #     status_description = ""
        
    #     if current_status == "Employee":
    #         status_pattern = r"employee|working|employed"
    #         status_description = "employed"
    #     elif current_status == "Self-Employed":
    #         status_pattern = r"self.?employed|entrepreneur|own.*business"
    #         status_description = "self-employed"
    #     elif current_status == "Retired":
    #         status_pattern = r"retired|retirement|former"
    #         status_description = "retired"
    #     elif current_status == "Student":
    #         status_pattern = r"student|studying|attends"
    #         status_description = "student"
    #     elif current_status == "Not employed":
    #         status_pattern = r"not (yet )?employed|unemployed|did not.*career"
    #         status_description = "not employed"
        
    #     if status_pattern and not re.search(status_pattern, description_occupation, re.IGNORECASE):
    #         inconsistencies.append(f"Employment status mismatch: profile status is '{current_status}', but description doesn't indicate '{status_description}'")
    
    # Check for employer consistency
    if employer and employer not in description_occupation:
        inconsistencies.append(f"Employer mismatch: profile employer '{employer}' not mentioned in description")
    
    # Check for position consistency
    if position and position not in description_occupation:
        inconsistencies.append(f"Position mismatch: profile position '{position}' not mentioned in description")
    
    # Check for salary/income consistency
    # if annual_income:
    #     # Extract the numeric part
    #     income_amount_match = re.search(r'(\d[\d\s,.]*\d)', str(annual_income))
    #     if income_amount_match:
    #         income_amount = income_amount_match.group(1).replace(" ", "").replace(",", "")
            
    #         # Check if this amount appears in the description
    #         if income_amount not in description_occupation.replace(" ", "").replace(",", ""):
    #             inconsistencies.append(f"Income mismatch: profile income '{annual_income}' not mentioned in description")
    
    if inconsistencies:
        logger.warning(f"Employment inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def check_education_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies in education information.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies in education information, False otherwise
    """
    inconsistencies = []
    
    education_history = client_data.client_profile.get("personal_info", {}).get("education_history", "")
    description_education = client_data.client_description.get("Education Background", "")
    
    if not education_history or not description_education:
        return False
    
    # Extract school/university names and years from profile
    # education_parts = education_history.split("(")
    # if len(education_parts) >= 2:
    #     school_name = education_parts[0].strip()
    #     graduation_year = education_parts[1].strip().rstrip(")")
        
    #     # Check if school name appears in description
    #     if school_name not in description_education:
    #         inconsistencies.append(f"Education institution mismatch: profile institution '{school_name}' not found in description")
        
    #     # Check if graduation year appears in description
    #     if graduation_year not in description_education:
    #         inconsistencies.append(f"Graduation year mismatch: profile year '{graduation_year}' not found in description")
    
    if inconsistencies:
        logger.warning(f"Education inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def check_family_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies in family information.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies in family information, False otherwise
    """
    inconsistencies = []
    
    marital_status = client_data.client_profile.get("personal_info", {}).get("marital_status", "")
    family_background = client_data.client_description.get("Family Background", "")
    
    if not marital_status or not family_background:
        return False
    
    # Check marital status consistency
    marital_status_lower = marital_status.lower()
    
    # Map marital status to expected patterns in description
    status_patterns = {
        "single": r"single|unmarried",
        "married": r"married|husband|wife|spouse",
        "divorced": r"divorced|separated",
        "widowed": r"widowed|widow"
    }
    
    for status, pattern in status_patterns.items():
        # If this is the client's status, it should be mentioned in description
        if status in marital_status_lower and not re.search(pattern, family_background, re.IGNORECASE):
            inconsistencies.append(f"Marital status mismatch: profile says '{marital_status}', but description doesn't indicate this")
        
        # If this is NOT the client's status but is mentioned, it's inconsistent
        if status not in marital_status_lower and re.search(pattern, family_background, re.IGNORECASE):
            # But "single" could be implied by not mentioning marriage
            if status != "single":
                inconsistencies.append(f"Marital status mismatch: profile doesn't say '{status}', but description indicates this")
    
    if inconsistencies:
        logger.warning(f"Family inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def check_country_inconsistencies(client_data: ClientData):
    """
    Check for inconsistencies in country information.
    
    Args:
        client_data: Client data object containing all client information
        
    Returns:
        bool: True if there are inconsistencies in country information, False otherwise
    """
    inconsistencies = []
    
    # Extract country information from different sources
    profile_country = client_data.client_profile.get("country_of_domicile", "")
    account_country = client_data.account_form.get("country", "")
    passport_country = client_data.passport.get("issuing_country", [])
    if isinstance(passport_country, list) and passport_country:
        passport_country = passport_country[0]
    passport_code = client_data.passport.get("code", "")
    
    # Check for nationality inconsistency
    nationality = client_data.client_profile.get("nationality", "")
    citizenship = client_data.passport.get("citizenship", "")
    
    # First check if the country information matches between profile and account
    if profile_country and account_country and profile_country != account_country:
        inconsistencies.append(f"Country of domicile mismatch: profile '{profile_country}' vs account '{account_country}'")
    
    # Check nationality against passport citizenship if both are present
    if nationality and citizenship and not is_nationality_equivalent(nationality, citizenship):
        inconsistencies.append(f"Nationality mismatch: profile '{nationality}' vs passport '{citizenship}'")
    
    if inconsistencies:
        logger.warning(f"Country inconsistencies detected:")
        for inconsistency in inconsistencies:
            logger.warning(f"  - {inconsistency}")
        return True
    
    return False


def are_strings_ocr_equivalent(str1, str2):
    """
    Check if two strings are equivalent accounting for common OCR errors.
    
    Args:
        str1 (str): First string to compare
        str2 (str): Second string to compare
        
    Returns:
        bool: True if strings are equivalent accounting for OCR errors
    """
    if str1 == str2:
        return True
    
    # Common OCR substitution errors
    ocr_substitutions = {
        '0': 'O', 'O': '0',
        '1': 'l', 'l': '1', 'I': '1', '1': 'I',
        '5': 'S', 'S': '5',
        '8': 'B', 'B': '8',
        'G': '6', '6': 'G',
        'Z': '2', '2': 'Z',
        'A': '4', '4': 'A',
        'n': 'h', 'h': 'n',
        'm': 'rn', 'rn': 'm',
        'N': 'H', 'H': 'N'
    }
    
    # Convert strings to uppercase for easier comparison
    str1_upper = str1.upper() if isinstance(str1, str) else ""
    str2_upper = str2.upper() if isinstance(str2, str) else ""
    
    if str1_upper == str2_upper:
        logger.debug(f"Strings match after uppercasing: '{str1}' vs '{str2}'")
        return True
    
    # If lengths differ too much, they're probably not the same
    if abs(len(str1_upper) - len(str2_upper)) > 2:
        logger.debug(f"String lengths differ too much: '{str1}' ({len(str1_upper)}) vs '{str2}' ({len(str2_upper)})")
        return False
    
    # Check by replacing each character with potential OCR mistakes
    mismatches = []
    for i in range(min(len(str1_upper), len(str2_upper))):
        if i < len(str1_upper) and i < len(str2_upper) and str1_upper[i] != str2_upper[i]:
            if str1_upper[i] in ocr_substitutions and ocr_substitutions[str1_upper[i]] == str2_upper[i]:
                logger.debug(f"OCR substitution match at position {i}: '{str1_upper[i]}' -> '{str2_upper[i]}'")
                continue
            if str2_upper[i] in ocr_substitutions and ocr_substitutions[str2_upper[i]] == str1_upper[i]:
                logger.debug(f"OCR substitution match at position {i}: '{str2_upper[i]}' -> '{str1_upper[i]}'")
                continue
            
            mismatches.append(i)
    
    # More than one character different that's not an OCR substitution
    if len(mismatches) > 3:  # Allow up to 3 mismatches
        logger.debug(f"Too many character mismatches ({len(mismatches)}) between '{str1}' and '{str2}'")
        return False
    
    # For longer strings, calculate similarity ratio
    if len(str1_upper) > 5 or len(str2_upper) > 5:
        # Calculate Levenshtein distance
        distance = levenshtein_distance(str1_upper, str2_upper)
        max_len = max(len(str1_upper), len(str2_upper))
        similarity_ratio = 1.0 - (distance / max_len)
        
        logger.debug(f"Similarity ratio between '{str1}' and '{str2}': {similarity_ratio:.2f}")
        
        # If similarity is high enough (80%), consider them equivalent
        return similarity_ratio >= 0.8
    
    return True


def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        
    Returns:
        int: The Levenshtein distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def are_names_similar(name1, name2):
    """
    Check if two names are similar, accounting for OCR errors and variations.
    
    Args:
        name1 (str): First name to compare
        name2 (str): Second name to compare
        
    Returns:
        bool: True if names are similar
    """
    if name1 == name2:
        return True
    
    # Convert both names to uppercase
    name1_upper = name1.upper() if isinstance(name1, str) else ""
    name2_upper = name2.upper() if isinstance(name2, str) else ""
    
    # Remove common titles and prefixes
    prefixes = ["MR ", "MR. ", "MS ", "MS. ", "MRS ", "MRS. ", "DR ", "DR. ", "PROF ", "PROF. "]
    for prefix in prefixes:
        if name1_upper.startswith(prefix):
            name1_upper = name1_upper[len(prefix):]
        if name2_upper.startswith(prefix):
            name2_upper = name2_upper[len(prefix):]
    
    # Check if name1 appears in name2 or vice versa
    if name1_upper in name2_upper or name2_upper in name1_upper:
        logger.debug(f"Name containment match: '{name1}' vs '{name2}'")
        return True
    
    # Split names into parts and compare
    name1_parts = name1_upper.split()
    name2_parts = name2_upper.split()
    
    # Check if at least one part matches with OCR tolerance
    for part1 in name1_parts:
        for part2 in name2_parts:
            if are_strings_ocr_equivalent(part1, part2):
                logger.debug(f"Name part OCR match: '{part1}' vs '{part2}'")
                return True
    
    # Calculate overall similarity
    if name1_parts and name2_parts:
        # Calculate Levenshtein distance for each pair of parts
        min_distance = float('inf')
        for part1 in name1_parts:
            for part2 in name2_parts:
                distance = levenshtein_distance(part1, part2)
                min_distance = min(min_distance, distance)
                logger.debug(f"Name part distance: '{part1}' vs '{part2}' = {distance}")
        
        # If the smallest distance is small relative to the length, names are similar
        max_part_len = max(len(part) for parts in [name1_parts, name2_parts] for part in parts)
        if max_part_len > 0 and min_distance <= max_part_len * 0.3:  # 30% tolerance
            logger.debug(f"Name similarity by part distance: min_distance={min_distance}, threshold={max_part_len * 0.3}")
            return True
    
    # Overall name similarity as a fallback
    combined_len = len(name1_upper) + len(name2_upper)
    if combined_len > 0:
        distance = levenshtein_distance(name1_upper, name2_upper)
        similarity = 1.0 - (distance / (combined_len / 2))
        logger.debug(f"Overall name similarity: '{name1}' vs '{name2}' = {similarity:.2f}")
        return similarity >= 0.7  # 70% similarity threshold
    
    return False


def are_strings_similar(str1, str2):
    """
    Check if two strings are similar.
    
    Args:
        str1 (str): First string
        str2 (str): Second string
        
    Returns:
        bool: True if strings are similar
    """
    if not str1 or not str2:
        return False
        
    # Convert to string if not already
    str1 = str(str1)
    str2 = str(str2)
    
    # Exact match
    if str1 == str2:
        return True
    
    # Case insensitive match
    if str1.lower() == str2.lower():
        return True
    
    # One is contained in the other
    if str1.lower() in str2.lower() or str2.lower() in str1.lower():
        return True
    
    # Levenshtein distance for longer strings
    if len(str1) > 3 and len(str2) > 3:
        distance = levenshtein_distance(str1.lower(), str2.lower())
        max_len = max(len(str1), len(str2))
        similarity = 1.0 - (distance / max_len)
        logger.debug(f"String similarity: '{str1}' vs '{str2}' = {similarity:.2f}")
        return similarity >= 0.7  # 70% similarity threshold
    
    return False


def are_dates_ocr_equivalent(date1, date2):
    """
    Check if two dates are equivalent, accounting for different formats and OCR errors.
    
    Args:
        date1 (str): First date string
        date2 (str): Second date string
        
    Returns:
        bool: True if dates are equivalent
    """
    if date1 == date2:
        return True
    
    logger.debug(f"Comparing dates: '{date1}' vs '{date2}'")
    
    # Extract year, month, day from date1 (assuming format like "2000-12-24")
    year1, month1, day1 = None, None, None
    date1_parts = date1.split("-") if "-" in date1 else date1.split("/")
    if len(date1_parts) == 3:
        # Standard format YYYY-MM-DD or YYYY/MM/DD
        year1 = date1_parts[0]
        month1 = date1_parts[1]
        day1 = date1_parts[2]
        logger.debug(f"Date1 parsed: year={year1}, month={month1}, day={day1}")
    
    # Extract from date2, which might be in various formats
    year2, month2, day2 = None, None, None
    
    # Handle format like "24-Dec-2ooo" (with potential OCR errors in the year)
    if "-" in date2:
        date2_parts = date2.split("-")
        if len(date2_parts) == 3:
            # Format like DD-MMM-YYYY
            day2 = date2_parts[0]
            
            # Handle month names
            months = {
                "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", 
                "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
                "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
            }
            
            month_name = date2_parts[1].upper()
            for month_key, month_value in months.items():
                if month_key in month_name:
                    month2 = month_value
                    break
            
            # Clean up year with potential OCR errors
            year_part = date2_parts[2].upper()
            year2 = ""
            for char in year_part:
                if char == 'O' or char == 'o':
                    year2 += '0'
                elif char == 'l' or char == 'I':
                    year2 += '1'
                elif char.isdigit():
                    year2 += char
            
            # Ensure 4-digit year
            if year2 and len(year2) == 2:
                if int(year2) > 50:  # Assume 19xx
                    year2 = "19" + year2
                else:  # Assume 20xx
                    year2 = "20" + year2
                    
            logger.debug(f"Date2 parsed: year={year2}, month={month2}, day={day2}")
    
    # Compare year, month, day if available
    if year1 and year2:
        if not are_strings_ocr_equivalent(year1, year2):
            logger.debug(f"Year mismatch: '{year1}' vs '{year2}'")
            return False
        else:
            logger.debug(f"Year match: '{year1}' vs '{year2}'")
    
    if month1 and month2 and month1 != month2:
        logger.debug(f"Month mismatch: '{month1}' vs '{month2}'")
        return False
    elif month1 and month2:
        logger.debug(f"Month match: '{month1}' vs '{month2}'")
        
    if day1 and day2 and not are_strings_ocr_equivalent(day1, day2):
        logger.debug(f"Day mismatch: '{day1}' vs '{day2}'")
        return False
    elif day1 and day2:
        logger.debug(f"Day match: '{day1}' vs '{day2}'")
    
    logger.debug(f"Dates are equivalent: '{date1}' vs '{date2}'")
    return True


def is_nationality_equivalent(nationality, citizenship):
    """
    Check if nationality and citizenship are equivalent, accounting for variations.
    
    Args:
        nationality (str): Nationality string
        citizenship (str): Citizenship string from passport
        
    Returns:
        bool: True if nationality and citizenship are equivalent
    """
    if not nationality or not citizenship:
        return False
        
    # Convert to uppercase for comparison
    nationality_upper = nationality.upper()
    citizenship_upper = citizenship.upper()
    
    # Exact match
    if nationality_upper == citizenship_upper:
        return True
    
    # Check if nationality is contained in citizenship
    if nationality_upper in citizenship_upper:
        logger.debug(f"Nationality '{nationality}' found in citizenship '{citizenship}'")
        return True
    
    # Handle common variations
    nationality_mapping = {
        "GERMAN": ["DEUTSCHLAND", "DEUTSCH", "GERMANY", "DEU"],
        "DANISH": ["DANMARK", "DENMARK", "DANSK", "DNK"],
        "FRENCH": ["FRANCE", "FRANÇAIS", "FRA"],
        "POLISH": ["POLSKA", "POLAND", "POL"],
        "ITALIAN": ["ITALIA", "ITALIAN", "ITA"],
        "SPANISH": ["ESPAÑA", "SPAIN", "ESP"],
        "AUSTRIAN": ["ÖSTERREICH", "AUSTRIA", "AUT"],
        "SWISS": ["SCHWEIZ", "SWITZERLAND", "SUISSE", "CHE"],
        "BELGIAN": ["BELGIQUE", "BELGIUM", "BEL"],
        "DUTCH": ["NEDERLAND", "NETHERLANDS", "NLD"],
        "SWEDISH": ["SVERIGE", "SWEDEN", "SWE"],
        "HUNGARIAN": ["MAGYAR", "HUNGARY", "HUN"]
    }
    
    # Check mapping
    for key, values in nationality_mapping.items():
        if key in nationality_upper:
            for value in values:
                if value in citizenship_upper:
                    logger.debug(f"Nationality mapping match: '{key}' -> '{value}' in citizenship '{citizenship}'")
                    return True
        # Check the reverse mapping
        for value in values:
            if value in nationality_upper:
                if key in citizenship_upper:
                    logger.debug(f"Reverse nationality mapping match: '{value}' -> '{key}' in citizenship '{citizenship}'")
                    return True
    
    logger.debug(f"No nationality mapping match between '{nationality}' and '{citizenship}'")
    return False