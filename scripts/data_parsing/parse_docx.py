import docx
import os
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Optional
from datetime import datetime

@dataclass_json
@dataclass
class ContactInfo:
    telephone: Optional[str] = None
    email: Optional[str] = None

@dataclass_json
@dataclass
class PersonalInfo:
    is_politically_exposed: bool = False
    marital_status: Optional[str] = None
    highest_education: Optional[str] = None
    education_history: Optional[str] = None

@dataclass_json
@dataclass
class EmploymentStatus:
    status_type: Optional[str] = None  # "Employee", "Not employed", "Retired"
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
    type_of_mandate: Optional[str] = None  # Discretionary, Advisory, Execution Only
    investment_experience: Optional[str] = None  # None, Limited, Good, Extensive
    investment_horizon: Optional[str] = None  # Short-term, Medium-term, Long-term
    expected_transactional_behavior: Optional[str] = None  # Low, Medium, High frequency
    preferred_markets: List[str] = field(default_factory=list) 

@dataclass_json
@dataclass
class AccountDetails:
    account_number: Optional[str] = None
    is_commercial_account: bool = False
    risk_profile: Optional[str] = None  # Low, Moderate, Considerable, High
    total_assets: Optional[float] = None
    transfer_assets: Optional[float] = None
    investment_preferences: InvestmentPreferences = field(default_factory=InvestmentPreferences)

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
    gender: Optional[str] = None
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
    filename: Optional[str] = None
    parsed_date: str = field(default_factory=lambda: datetime.now().isoformat())

class DocxParser:
    """Parser for client profile docx files"""
    
    @staticmethod
    def extract_cell_value(row, column_index):
        """Extract cell text value safely"""
        try:
            return row.cells[column_index].text.strip() if column_index < len(row.cells) else ""
        except:
            return ""
    
    @staticmethod
    def find_checkbox_value(text):
        """Determine if a checkbox is checked"""
        return "☒" in text
    
    @staticmethod
    def get_marital_status(text):
        """Extract marital status from checkbox text"""
        if "☒ Divorced" in text:
            return "Divorced"
        elif "☒ Married" in text:
            return "Married"
        elif "☒ Single" in text:
            return "Single"
        elif "☒ Widowed" in text:
            return "Widowed"
        return None
    
    @staticmethod
    def get_gender(text):
        """Extract marital status from checkbox text"""
        if "☒ Female" in text:
            return "Female"
        elif "☒ Male" in text:
            return "Male"
        return None
    
    @staticmethod
    def get_wealth_range(text):
        """Extract wealth range from checkbox text"""
        if "☒ < EUR 1.5m" in text:
            return "< EUR 1.5m"
        elif "☒ EUR 1.5m-5m" in text:
            return "EUR 1.5m-5m"
        elif "☒ EUR 5m-10m" in text:
            return "EUR 5m-10m"
        elif "☒ EUR 10m.-20m" in text:
            return "EUR 10m.-20m"
        elif "☒ EUR 20m.-50m" in text:
            return "EUR 20m.-50m"
        elif "☒ > EUR 50m" in text:
            return "> EUR 50m"
        return None

    @staticmethod
    def get_income_range(text):
        """Extract income range from checkbox text"""
        if "☒ < EUR 250,000" in text:
            return "< EUR 250,000"
        elif "☒ EUR 250,000 - 500,000" in text:
            return "EUR 250,000 - 500,000"
        elif "☒ EUR 500,000 – 1m" in text:
            return "EUR 500,000 – 1m"
        elif "☒ > EUR 1m" in text:
            return "> EUR 1m"
        return None
    
    @staticmethod
    def get_risk_profile(text):
        """Extract risk profile from checkbox text"""
        if "☒ Low" in text:
            return "Low"
        elif "☒ Moderate" in text:
            return "Moderate"
        elif "☒ Considerable" in text:
            return "Considerable"
        elif "☒ High" in text:
            return "High"
        return None

    @staticmethod
    def extract_wealth_sources(text):
        """Extract wealth sources from checkbox text"""
        sources = []
        if "☒ Employment" in text:
            sources.append("Employment")
        if "☒ Inheritance" in text:
            sources.append("Inheritance")
        if "☒ Business" in text:
            sources.append("Business")
        if "☒ Investments" in text:
            sources.append("Investments")
        if "☒ Sale of real estate" in text:
            sources.append("Sale of real estate")
        if "☒ Retirement package" in text:
            sources.append("Retirement package")
        if "☒ Other" in text:
            sources.append("Other")
        return sources
    
    @staticmethod
    def extract_assets(text):
        """Extract assets from checkbox text"""
        assets = {}
        for line in text.splitlines():
            if "☒" in line:
                print(line)
                line = line.replace("☒", "").strip()
                if line:
                    assets[line.split("EUR")[0].strip()] = line.split("EUR")[1].strip()
        return assets


    @staticmethod
    def get_mandate_type(text):
        """Extract mandate type from checkbox text"""
        if "☒ Discretionary" in text:
            return "Discretionary"
        elif "☒ Advisory" in text:
            return "Advisory"
        elif "☒ Execution Only" in text:
            return "Execution Only"
        return None

    @staticmethod
    def get_investment_experience(text):
        """Extract investment experience level from checkbox text"""
        if "☒ Inexperienced" in text:
            return "Inexperienced"
        elif "☒ Experienced" in text:
            return "Experienced"
        elif "☒ Expert" in text:
            return "Expert"
        return None
    
    @staticmethod
    def get_investment_horizon(text):
        """Extract investment horizon from checkbox text"""
        if "☒ Short" in text:
            return "Short"
        elif "☒ Medium" in text:
            return "Medium"
        elif "☒ Long-Term" in text:
            return "Long-Term"
        return None
    
        
    @staticmethod
    def extract_preferred_markets(text):
        """Extract preferred markets from checkbox text"""
        markets = text.split(",")
        return [market.strip() for market in markets] if markets else []
    
    @staticmethod
    def parse_docx_file(file_path):
        """Parse a docx file and return a ClientProfile object"""
        client = ClientProfile(filename=os.path.basename(file_path))
        primary_employment = Employment()
        
        try:
            doc = docx.Document(file_path)
            
            # Parse tables
            for i, table in enumerate(doc.tables):
                if i == 0:  # Skip the "Client Information" header table
                    continue
                
                # Identify tables by index based on the analysis
                if i == 1:  # Basic information table
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Last Name" in row_label:
                            client.last_name = row_value
                        elif "First/ Middle Name" in row_label:
                            client.first_name = row_value
                        elif "Address" in row_label:
                            client.address = row_value
                        elif "date of birth" in row_label.lower():
                            client.birth_date = row_value
                        elif "Nationality" in row_label:
                            client.nationality = row_value
                        elif "passport no/ unique id" in row_label.lower():
                            client.passport_id = row_value
                        elif "ID Type" in row_label:
                            client.id_type = row_value
                        elif "ID Issue Date" in row_label:
                            client.id_issue_date = row_value
                        elif "id expiry date" in row_label.lower():
                            client.id_expiry_date = row_value
                        elif "gender" in row_label.lower():
                            client.gender = DocxParser.get_gender(row_value)
                        elif "country of domicile" in row_label.lower():
                            client.country_of_domicile = row_value
                        
                
                elif i == 3:  # Contact info table
                    for row in table.rows:
                        row_value = DocxParser.extract_cell_value(row, 2)
                        if "Telephone" in row_value:
                            client.contact_info.telephone = row_value.replace("Telephone", "").strip()
                        elif "E-Mail" in row_value:
                            client.contact_info.email = row_value.replace("E-Mail", "").strip()
                
                elif i == 5:  # PEP status table
                    row_value = DocxParser.extract_cell_value(table.rows[0], 2)
                    client.personal_info.is_politically_exposed = "☒ Yes" in row_value
                
                elif i == 6:  # Marital status and education
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Marital Status" in row_label:
                            client.personal_info.marital_status = DocxParser.get_marital_status(row_value)
                        elif "Highest education" in row_label:
                            client.personal_info.highest_education = row_value
                        elif "Education History" in row_label:
                            client.personal_info.education_history = row_value
                
                elif i == 8:  # Employment info - first part
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Current employment and function" in row_label:
                            if "Employee" in row_value:
                                primary_employment.current_status.status_type = "Employee"
                                # Extract the "Since" date
                                if "Since" in row_value:
                                    primary_employment.current_status.since = row_value.split("Since")[1].strip()
                            elif "Name Employer" in row_value:
                                primary_employment.employer = row_value.replace("Name Employer", "").strip()
                            elif "Position" in row_value:
                                # Extract position and possibly annual income
                                parts = row_value.replace("Position", "").strip().split("(")
                                primary_employment.position = parts[0].strip()
                                if len(parts) > 1:
                                    primary_employment.annual_income = parts[1].replace(")", "").strip()
                
                elif i == 9:  # Employment status - second part
                    employment_status_found = False
                    
                    for row in table.rows:
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Currently not employed" in row_value and DocxParser.find_checkbox_value(row_value):
                            employment_status_found = True
                            primary_employment.current_status.status_type = "Not employed"
                            if "Since" in row_value:
                                since_value = row_value.split("Since")[1].strip()
                                if since_value:
                                    primary_employment.current_status.since = since_value
                        
                        elif "Previous Profession" in row_value:
                            primary_employment.previous_profession = row_value.replace("Previous Profession:", "").strip()
                        
                        elif "Retired" in row_value and DocxParser.find_checkbox_value(row_value):
                            employment_status_found = True
                            primary_employment.current_status.status_type = "Retired"
                            if "Since" in row_value:
                                since_value = row_value.split("Since")[1].strip()
                                if since_value:
                                    primary_employment.current_status.since = since_value
                    
                    # Add the parsed employment to client profile
                    if primary_employment.employer or primary_employment.position or primary_employment.current_status.status_type:
                        client.employment.append(primary_employment)
                
                elif i == 11:  # Wealth info
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Total wealth estimated" in row_label:
                            client.wealth_info.total_wealth_range = DocxParser.get_wealth_range(row_value)
                        elif "Origin of wealth" in row_label:
                            client.wealth_info.wealth_sources = DocxParser.extract_wealth_sources(row_label)
                            if row_value:
                                client.wealth_info.source_info.append(row_value)
                        elif "estimated assets" in row_label.lower():
                            client.wealth_info.assets = DocxParser.extract_assets(row_value)
                        # print(f"Row label: {row_label}, Row value: {row_value}")
                
                elif i == 13:  # Income info
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Estimated Total income" in row_label:
                            client.income_info.total_income_range = DocxParser.get_income_range(row_value)
                        if "Country of main source of income" in row_label:
                            client.income_info.source_info = row_value
                            
                
                elif i == 15:  # Account details and basic investment preferences
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Account Number" in row_label:
                            client.account_details.account_number = row_value
                        elif "Commercial Account" in row_label:
                            client.account_details.is_commercial_account = "☒ Yes" in row_value
                        elif "Investment Risk Profile" in row_label:
                            client.account_details.risk_profile = DocxParser.get_risk_profile(row_value)
                        elif "Type of Mandate" in row_label:
                            client.account_details.investment_preferences.type_of_mandate = DocxParser.get_mandate_type(row_value)
                        elif "Investment Experience" in row_label:
                            client.account_details.investment_preferences.investment_experience = DocxParser.get_investment_experience(row_value)
                        elif "Investment Horizon" in row_label:
                            client.account_details.investment_preferences.investment_horizon = DocxParser.get_investment_horizon(row_value)
                        elif "Expected Transactional Behavior" in row_label:
                            client.account_details.investment_preferences.expected_transactional_behavior = row_value
                        elif "Preferred Markets" in row_label:
                            client.account_details.investment_preferences.preferred_markets = DocxParser.extract_preferred_markets(row_value)
                
                elif i == 17:  # Assets info
                    for row in table.rows:
                        row_label = DocxParser.extract_cell_value(row, 0)
                        row_value = DocxParser.extract_cell_value(row, 2)
                        
                        if "Total Asset Under Management" in row_label:
                            try:
                                client.account_details.total_assets = float(row_value.replace(",", ""))
                            except ValueError:
                                client.account_details.total_assets = row_value
                        elif "Asset Under Management to transfer" in row_label:
                            try:
                                client.account_details.transfer_assets = float(row_value.replace(",", ""))
                            except ValueError:
                                client.account_details.transfer_assets = row_value

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return client

def parse_docx_to_json(docx_file_path, output_json_path=None):
    """
    Parse a docx file to a ClientProfile object and optionally save as JSON
    
    Args:
        docx_file_path: Path to the docx file
        output_json_path: Optional path to save JSON output, if None returns JSON string
        
    Returns:
        JSON string if output_json_path is None, otherwise None
    """
    client_profile = DocxParser.parse_docx_file(docx_file_path)
    
    # Convert to JSON
    json_data = client_profile.to_json(indent=2, ensure_ascii=False)
    
    # Save to file if path provided
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        return None
    
    return json_data

if __name__ == "__main__":
    # Example usage:
    # For single file
    json_data = parse_docx_to_json("C:\\Users\\jekatrinaj\\swisshacks\\data\\level_5\\profile.docx", "C:\\Users\\jekatrinaj\\swisshacks\\data\\level_5\\profile_output.json")
    # print("JSON data saved to profile_output.json")