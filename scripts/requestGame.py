import requests
import json
import time
from dotenv import load_dotenv
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import base64
from openai import AzureOpenAI

from data_parsing.parse_docx import parse_docx_to_json
from data_parsing.parse_pdf_banking_form import (
    parse_banking_form,
    save_form_data_as_json,
)
from data_parsing.parse_txt import parse_text_to_json, save_json_output

# from data_parsing.parse_png import process_image_regions
from storage import store_dict
# from model.rule_based_model import SimpleModel
# from client_data.client_data import ClientData
# from openai.test import (
#     OpenAIPredictor, check_data_consistency
# )

PROJECT_DIR = Path(__file__).parent.parent.resolve().absolute()

data_dir = PROJECT_DIR / "data"
load_dotenv("C:\\Users\\jekatrinaj\\swisshacks\\.env")

# API configuration
BASE_URL = "https://hackathon-api.mlo.sehlat.io"
API_KEY = "KR4iOS4v-zY57HPvT7U6HCrnN08ufEg5RT7Ye-bOU4Y"
HEADERS = {"x-api-key": API_KEY}

api_key = "3L2W6niZ2aTcZWiobBG5d54g3M3xTvbbUWqLjuhajbyDYIpJ6xRGJQQJ99BDACYeBjFXJ3w3AAABACOGzqpD"

# class Predictor:
#     """Base predictor class"""
#     def predict(self, data, *args, **kwargs):
#         return self._predict(data, *args, **kwargs)
    
#     def _predict(self, data, *args, **kwargs):
#         raise NotImplementedError("Subclasses must implement this method")

# class OpenAIPredictor(Predictor):

#     def __init__(self, rulebook_path: str | Path):
#         super().__init__()

#         with open(rulebook_path, "r") as f:
#             self.rules = f.read()

#     def _predict(self, data: List[Dict[str, Any]], *args, **kwargs) -> List[int]:

#         PROMPT = """
#             HERE is a client data, that we would like to verify that has no inconsistencies.
#             We would like to reject the application if something does not add up, or misses a field.
#             - Compare fields across documents
#             - Check if the description of the client adds up with the numbers and backstories.
#             - You can reason for yourself shortly.
#             - last line of your response should be a json {'reject': true/false}.
#             - Most importanyl reject only if the document breaks one of these rules:
#             - {rules}
            
#             HERE is the data: {data}
#         """
#         result = []
#         for client in data:
#             client_openai = AzureOpenAI(
#                 api_key=api_key,
#                 api_version="2025-01-01-preview",
#                 azure_endpoint="https://swisshacks-3plus1.openai.azure.com"
#             )

#             response = client_openai.chat.completions.create(
#                 model="gpt-4o",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant focused on data validation."},
#                     {"role": "user", "content": PROMPT.format(rules=self.rules, data=json.dumps(client))}
#                 ]
#             )
            
#             # Extract the rejection decision
#             response_content = response.choices[0].message.content
#             print(f"Validation response: {response_content}")
            
#             # Check if the response contains the decision
#             if "{'reject': true}" in response_content.lower():
#                 result.append(0)  # Rejected
#             else:
#                 result.append(1)  # Accepted
                
#         return result

def check_data_consistency(account_json_path: str, profile_json_path: str, description_json_path: str, passport_png_path: str, rules_path: str) -> Dict[str, Any]:
    """
    Check consistency across multiple data files for a client
    
    Args:
        account_json_path: Path to account JSON file
        profile_json_path: Path to profile JSON file
        description_json_path: Path to passport JSON file
        passport_png_path: Path to passport PNG image
        rules_path: Path to rules file
    
    Returns:
        Dict with consistency check results and reasoning
    """
    # Load JSON data
    with open(account_json_path, 'r') as f:
        account_data = json.load(f)
    
    with open(profile_json_path, 'r') as f:
        profile_data = json.load(f)

    with open(description_json_path, 'r') as f:
        description_data = json.load(f)
    
    # Encode PNG as base64 for the AI to analyze
    with open(passport_png_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create prompt for consistency check
    consistency_prompt = f"""
    Analyze the provided client data for consistency across different documents.
    
    Account data: {json.dumps(account_data, indent=2)}
    
    Profile data: {json.dumps(profile_data, indent=2)}
    
    Description data: {json.dumps(description_data, indent=2)}
    
    The passport image is also provided as base64. Please check if the data is consistent across all sources.
    
    Check for:
    1. Name consistency across all documents
    2. Address consistency
    3. Passport number matching between passport data and account data
    4. Any suspicious inconsistencies or missing critical information
    5. Any signs of fraud or data manipulation
    
    Provide detailed reasoning about any inconsistencies found.
    Respond with a JSON structure that includes:
    - "is_consistent": true/false
    - "inconsistencies": [list of specific inconsistencies found]
    - "reasoning": detailed explanation of your findings
    - "risk_level": "low", "medium", or "high"
    - "only_small_inconsistencies": true/false (if the inconsistencies are minor and do not affect the decision-making process)
    """
    
    # Create Azure OpenAI client for this specific check
    consistency_client = AzureOpenAI(
        api_key=api_key,
        api_version="2025-01-01-preview",
        azure_endpoint="https://swisshacks-3plus1.openai.azure.com"
    )
    
    # Make API call with image included
    consistency_response = consistency_client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a financial fraud detection assistant that specializes in identifying inconsistencies in client documentation. Only identify inconsistencies that are critical to the decision-making process and missing critical information. Take a note that some of the fields can be separated into multiple keys in json formats (like address). Disregard missing account number and expected_transactional_behavior."},
            {"role": "user", "content": consistency_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "Here is the passport image to analyze:"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
            ]}
        ],
        temperature=0.1  # Lower temperature for more deterministic responses
    )
    
    # Extract and parse the response
    response_content = consistency_response.choices[0].message.content
    
    # Find and extract JSON from the response
    try:
        # Try to extract JSON from the response content
        import re
        json_match = re.search(r'```json\n(.*?)\n```', response_content, re.DOTALL)
        if json_match:
            result_json = json.loads(json_match.group(1))
        else:
            # Try to parse the entire response as JSON
            result_json = json.loads(response_content)
    except json.JSONDecodeError:
        # If parsing fails, return a structured error
        result_json = {
            "is_consistent": False,
            "inconsistencies": ["Unable to parse AI response into structured format"],
            "reasoning": response_content,
            "risk_level": "medium"
        }
    
    return result_json


def start_game():
    """Start a new game session and return session details"""

    url = f"{BASE_URL}/game/start"
    payload = {"player_name": "3plus1"}

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_data = response.json()

        print("Game started successfully!")
        print(f"Session ID: {response_data['session_id']}")
        print(f"Initial client ID: {response_data['client_id']}")

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error starting game: {e}")
        return None


def send_decision(session_id, client_id, decision):
    """Send the decision (Accept or Reject) to the API and return the response"""

    url = f"{BASE_URL}/game/decision"

    picked_decision = "Accept" if decision == 1 else "Reject"

    payload = {
        "decision": picked_decision,
        "client_id": client_id,
        "session_id": session_id,
    }

    # Return also the decision (1 for Accept, 0 for Reject)
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_data = response.json()  # Converts the response to a dict object

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error making decision: {e}")
        return None


def toMd5(client_data: dict):
    """Convert client data to MD5 hash"""
    json_string = json.dumps(client_data, sort_keys=True)
    # Compute the MD5 hash
    md5_hash = hashlib.md5(json_string.encode("utf-8")).hexdigest()
    return md5_hash


def save_result(client_data, score, status, answer):
    """Save the result"""

    result = "1" if status else "0"

    # Format the score as a two-digit string
    formatted_score = str(score).zfill(2)

    print(f"test/{result}/{formatted_score}/{toMd5(client_data)}")
    store_dict(client_data, f"test/{result}/{formatted_score}/{toMd5(client_data)}")

    # print(f"\nlevel_{formatted_score}-answer_{answer}_result_{result}.json")


def run_game():
    """Main script"""
    game_data = start_game()

    if not game_data:
        print("Failed to start game. Exiting.")
        return

    print("\nGame started ...")

    session_id = game_data["session_id"]
    current_client_id = game_data["client_id"]
    client_data = game_data["client_data"]
    score = 0  # Starting score

    # Calculate delay to achieve 55 requests per minute
    delay = 60 / 55  # seconds per request

    # Run the queries
    queries_made = 0
    start_time = time.time()

    # Fix OpenAIPredictor instantiation with rulebook_path
    rules_path = PROJECT_DIR / "scripts" / "openai" / "validation_rules.txt"
    # predictor = OpenAIPredictor(rulebook_path=str(rules_path))  # SimpleModel()

    while True:  # Run indefinitely until game over
        print(f"\nChecking result for level {score} ...")

        # Save data in reasonable formats
        from decode_game_files import process_json_file

        # TODO: define what folder structure we use
        output_dir = data_dir / f"level_{score}"
        process_json_file(client_data, output_dir)

        ### Parse saved documents
        # Parse the PNG passport image and save as JSON
        # process_image_regions(
        #     output_dir / "passport.png", visualize=False, threshold=0.3
        # )

        # Parse the PDF banking form and save as JSON
        form_data = parse_banking_form(output_dir / "account.pdf")
        save_form_data_as_json(form_data, output_dir / "account.json")

        # Parse the DOCX file and save as JSON
        parse_docx_to_json(output_dir / "profile.docx", output_dir / "profile.json")

        # Parse the TXT file and save as JSON
        parsed_txt = parse_text_to_json(output_dir / "description.txt")
        save_json_output(parsed_txt, output_dir / "description.json")

        # client_file = ClientData(
        #     client_file=str(output_dir),
        #     account_form=json.load(open(output_dir / "account.json")),
        #     client_description=parsed_txt,
        #     client_profile=json.load(open(output_dir / "profile.json")),
        #     passport=json.load(open(output_dir / "passport.json")),
        #     label=0,
        # )
        openai_response = check_data_consistency(
            str(output_dir / "account.json"),
            str(output_dir / "profile.json"),
            str(output_dir / "description.json"),
            str(output_dir / "passport.png"),
            str(rules_path),
        )
        decision = openai_response["risk_level"]
        decision = 0 if decision == "high" else 1

        # Make decision based on client data
        # decision = predictor.predict(client_file)
        response = send_decision(session_id, current_client_id, decision)

        queries_made += 1
        client_data = response.get("client_data", {})
        score = response["score"]

        # Check if game is over
        if response["status"] == "gameover":
            print(f"\nGame over! Final score: {score}")

            # Save the result
            save_result(response, score + 1, 0, decision)
            break

        else:
            # Update client ID and score for next request immediately after receiving the response
            current_client_id = response["client_id"]

            score = response["score"]

            # Save the result
            save_result(client_data, score, 1, decision)

        # Calculate time to sleep to maintain 55 requests per minute
        elapsed = time.time() - start_time
        expected_elapsed = queries_made * delay
        sleep_time = max(0, expected_elapsed - elapsed)

        if sleep_time > 0:
            time.sleep(sleep_time)

    # Print summary
    elapsed_time = time.time() - start_time
    print(f"\nCompleted {queries_made} queries in {elapsed_time:.2f} seconds")
    print(f"Rate: {queries_made / elapsed_time * 60:.2f} queries per minute")


def run_game_continuously():
    """Run the game continuously, creating a new game every time it stops."""

    while True:
        run_game()
        print("\nRestarting game in 3 seconds...")
        time.sleep(3)  # Delay before starting a new game


if __name__ == "__main__":
    run_game()
    # run_game_continuously()
