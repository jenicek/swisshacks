import base64
import json
from pathlib import Path
import os
from openai import AzureOpenAI

# Get API key from environment variable or define it
api_key = os.environ.get("AZURE_OPENAI_API_KEY")
api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")


def parse_png_to_json(passport_png_path: str) -> dict:
    """
    Parse a passport image (PNG) to extract structured data using OpenAI vision API.

    Args:
        passport_png_path: Path to the passport image file

    Returns:
        Dictionary containing extracted passport information
    """
    # Encode PNG as base64 for the AI to analyze
    with open(passport_png_path, "rb") as image_file:
        image_data = image_file.read()

    passport_data = parse_png(image_data)

    # Extract and parse the JSON response
    try:
        print(f"Extracted passport data: {passport_data}")
        print(f"Successfully extracted passport data")

        # Save the extracted data to file for debugging/reference
        output_dir = Path(passport_png_path).parent
        output_path = output_dir / "passport.json"
        with open(output_path, "w") as f:
            json.dump(passport_data, f, indent=2)

        return passport_data

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from OpenAI response: {e}")
        # Return empty dict with structure matching expected schema
        return {
            "given_name": "",
            "last_name": "",
            "gender": "",
            "country": "",
            "country_code": "",
            "nationality": "",
            "birth_date": "",
            "passport_number": "",
            "passport_mrz": [],
            "passport_issue_date": "",
            "passport_expiry_date": "",
            "signature": False,
        }



def parse_png(image_data: bytes) -> dict:
    """
    Parse a PNG image using OpenAI's vision API to extract structured data.
    """
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    client_openai = AzureOpenAI(
        api_key=api_key,
        api_version="2025-01-01-preview",
        azure_endpoint=api_endpoint,
    )

    # Define expected JSON schema for passport data
    passport_json_schema = """{
    "given_name": "string",
    "last_name": "string",
    "gender": "string",
    "country": "string",
    "country_code": "string",
    "nationality": "string",
    "birth_date": "YYYY-MM-DD",
    "passport_number": "string",
    "passport_mrz": ["array", "of", "strings"],
    "passport_issue_date": "YYYY-MM-DD",
    "passport_expiry_date": "YYYY-MM-DD"
    "signature": "boolean"
    }"""

    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant focused on parsing image data from a passport to a structured JSON format.\
                    Extract all visible information from the passport image. Return ONLY valid JSON without any additional text.\
                        The required JSON format is: {passport_json_schema}",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all information from this passport image and return it as JSON:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
                    },
                ],
            },
        ],
        temperature=0.1,  # Lower temperature for more deterministic responses
        response_format={"type": "json_object"},  # Ensure response is formatted as JSON
    )

    try:
        passport_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print(f"Raw response: {response.choices[0].message.content}")
        raise

    return passport_data
