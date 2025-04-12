import easyocr
from pathlib import Path
import argparse
import numpy as np
import json
from PIL import Image
import cv2  # OpenCV for visualization

# TODO extend bounding boxes
FIELD_TO_EXTRACT ={
    "issuing_country": [(10,21), (290,21), (290,40), (10,40)],
    "code": [(130, 55), (184, 55), (184, 69), (130, 69)],
    "surname": [(22, 98), (80, 98), (80,116), (22, 116)],
    "given_name": [(131, 98), (230, 98), (230,115), (131, 115)],
    "passport_number": [(245, 55), (317, 55), (317, 69), (245, 69)],
    "birth_date": [(23, 139), (110, 139), (110, 155), (23, 155)],
    "citizenship": [(135, 139), (290, 139), (290, 155), (135, 155)],
    "issue_date": [(135, 179), (209,179), ( 209, 195), (135, 195)],
    "expiry_date": [(135, 209), (209, 209), (209, 225), (135, 225)],
    "sex": [(22, 177), (45, 177), (45, 200), (22, 200)],
}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract text from images using OCR")
    parser.add_argument("--file", "-f", type=str, required=True, 
                        help="Path to the image file to process")
    parser.add_argument("--regions", "-r", action="store_true",
                        help="Process specific regions defined in the code")
    parser.add_argument("--visualize", "-v", action="store_true",
                        help="Visualize bounding boxes on the image and save")
    parser.add_argument("--threshold", "-t", type=float, default=0.3,
                        help="Confidence threshold for OCR results (default: 0.3)")
    return parser.parse_args()

def process_image(image_path):
    reader = easyocr.Reader(['en'])  # specify the language
    
    image = Image.open(image_path)
    image_np = np.array(image)
    
    results = reader.readtext(image_path)
    
    print(f"Processing full image: {image_path}, image size: {image_np.shape}")
    print("-" * 50)
    
    for i, (bbox, text, prob) in enumerate(results):
        print(f"Detection #{i+1}:")
        print(f"  Bounding Box: {bbox}")
        print(f"  Text: {text}")
        print(f"  Confidence: {prob:.4f}")
        print("-" * 50)
    
    return results

def process_image_regions(image_path, visualize=False, threshold=0.3):
    reader = easyocr.Reader(['en'])
    image = Image.open(image_path)
    image_np = np.array(image)
    
    # If visualization is requested, create a copy for drawing
    if visualize:
        # Convert to BGR if needed (for OpenCV compatibility)
        if len(image_np.shape) == 3 and image_np.shape[2] == 4:  # RGBA image
            vis_image = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
        elif len(image_np.shape) == 3 and image_np.shape[2] == 3:  # RGB image
            vis_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:  # Grayscale or other format
            vis_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # Results dictionary for raw OCR output
    results = {}
    
    # Aggregate dictionary for extracted text (matching original keys)
    extracted_text = {}
    
    print(f"Processing regions in image: {image_path} with size: {image_np.shape}")
    print("-" * 50)
    
    for region_name, bbox in FIELD_TO_EXTRACT.items():
        # Calculate the min/max coordinates to crop the image
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        min_x, max_x = max(0, min(x_coords)), min(image_np.shape[1], max(x_coords))
        min_y, max_y = max(0, min(y_coords)), min(image_np.shape[0], max(y_coords))
        
        # Crop the image to the region
        region_image = image_np[min_y:max_y, min_x:max_x]
        
        # Skip empty regions
        if region_image.size == 0:
            print(f"Region '{region_name}' is outside of image bounds or has zero size. Skipping.")
            continue
            
        # Process the region
        region_results = reader.readtext(region_image)
        
        # Adjust coordinates to be relative to the original image
        adjusted_results = []
        
        # Filter results by confidence threshold and store text
        filtered_text = []
        
        for r_bbox, text, prob in region_results:
            # Only include results above the confidence threshold
            if prob >= threshold:
                # Adjust bounding box coordinates to be relative to the original image
                adjusted_bbox = [
                    (pt[0] + min_x, pt[1] + min_y) for pt in r_bbox
                ]
                adjusted_results.append((adjusted_bbox, text, prob))
                
                # Add text to the filtered list
                filtered_text.append(text)
        
        # Store adjusted results in the raw results dictionary
        results[region_name] = adjusted_results
        
        # Store extracted text in the aggregate dictionary
        # If there are multiple text entries, store as a list; otherwise, store single string
        if len(filtered_text) > 0:
            extracted_text[region_name] = filtered_text if len(filtered_text) > 1 else filtered_text[0]
        
        print(f"Region: {region_name}")
        if not region_results:
            print("  No text detected in this region")
        for i, (_, text, prob) in enumerate(region_results):
            if prob >= threshold:
                print(f"  Detection #{i+1}:")
                print(f"    Text: {text}")
                print(f"    Confidence: {prob:.4f}")
            else:
                print(f"  Detection #{i+1}: (below threshold, confidence: {prob:.4f})")
        print("-" * 50)
        
        # Draw bounding box for this region if visualization is enabled
        if visualize:
            # Convert bbox to the format OpenCV expects for polylines
            pts = np.array(bbox, np.int32)
            pts = pts.reshape((-1, 1, 2))
            # Draw red polygon with thickness=2
            cv2.polylines(vis_image, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            # Add region name as label
            cv2.putText(vis_image, region_name, (min_x, min_y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # Export the extracted text dictionary to a JSON file
    image_path_obj = Path(image_path)
    json_output_path = image_path_obj.parent / f"{image_path_obj.stem}_extracted.json"
    
    with open(json_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_text, json_file, indent=4, ensure_ascii=False)
    
    print(f"Extracted text saved to: {json_output_path}")
    
    # Save the visualization image if requested
    if visualize:
        # Construct output filename in the same directory as the input
        output_path = image_path_obj.parent / f"{image_path_obj.stem}_annotated{image_path_obj.suffix}"
        cv2.imwrite(str(output_path), vis_image)
        print(f"Annotated image saved to: {output_path}")
    
    return results, extracted_text

if __name__ == "__main__":
    args = parse_arguments()
    image_path = args.file
    
    # Verify the file exists
    if not Path(image_path).exists():
        print(f"Error: File '{image_path}' does not exist")
        exit(1)
    
    if args.regions:
        process_image_regions(image_path, visualize=args.visualize, threshold=args.threshold)
    else:
        process_image(image_path)