import json
import re
import os

def parse_text_to_json(file_path):
    """
    Parses a text file and converts it to a structured JSON format with specific fields.
    
    Args:
        file_path (str): Path to the text file to be parsed
        
    Returns:
        dict: A dictionary with parsed information in the specified format
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Read the text file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Initialize the structure
        parsed_data = {
            "Summary Note": "",
            "Family Background": "",
            "Education Background": "",
            "Occupation History": "",
            "Wealth Summary": "",
            "Client Summary": ""
        }
        
        # Define sections to extract
        sections = list(parsed_data.keys())
        
        # Extract content between sections
        for i, section in enumerate(sections):
            # Create pattern to match the section and its content
            pattern = f"{section}: ?(.*?)"
            
            # If this is the last section, match until the end of file
            if i == len(sections) - 1:
                pattern += "(?:\Z)"
            else:
                # Otherwise match until the next section
                pattern += f"(?={sections[i+1]}: )"
            
            # Find the section in the text
            matches = re.search(pattern, content, re.DOTALL)
            if matches:
                # Extract and clean the section content
                section_content = matches.group(1).strip()
                
                # Process the section content (here just remove extra whitespace)
                section_content = re.sub(r'\n+', '\n', section_content)
                
                # Add to the parsed data
                parsed_data[section] = section_content
        
        return parsed_data
    
    except Exception as e:
        return {"error": f"Error parsing text file: {str(e)}"}

def save_json_output(parsed_data, output_path):
    """
    Save the parsed data as a JSON file
    
    Args:
        parsed_data (dict): The parsed data to save
        output_path (str): Path where to save the JSON output
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(parsed_data, json_file, indent=2, ensure_ascii=True)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return False

def main():
    """
    Example usage of the parsing function
    """
    # Example usage
    import sys
    if len(sys.argv) < 3:
        print("Usage: python parse_txt.py <input_text_file> <output_json_file>")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    parsed_data = parse_text_to_json(input_path)
    if "error" in parsed_data:
        print(parsed_data["error"])
        return
    
    if save_json_output(parsed_data, output_path):
        print(f"Successfully parsed {input_path} and saved to {output_path}")
    else:
        print(f"Failed to save output to {output_path}")

if __name__ == "__main__":
    main()