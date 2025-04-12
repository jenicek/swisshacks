import easyocr
from pathlib import Path
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract text from images using OCR")
    parser.add_argument("--file", "-f", type=str, required=True, 
                        help="Path to the image file to process")
    return parser.parse_args()

def process_image(image_path):
    reader = easyocr.Reader(['en'])  # specify the language
    results = reader.readtext(image_path)
    
    print(f"Processing file: {image_path}")
    print("-" * 50)
    
    for i, (bbox, text, prob) in enumerate(results):
        print(f"Detection #{i+1}:")
        print(f"  Bounding Box: {bbox}")
        print(f"  Text: {text}")
        print(f"  Confidence: {prob:.4f}")
        print("-" * 50)
    
    return results

if __name__ == "__main__":
    args = parse_arguments()
    image_path = args.file
    
    # Verify the file exists
    if not Path(image_path).exists():
        print(f"Error: File '{image_path}' does not exist")
        exit(1)
        
    process_image(image_path)