import requests
import json
import time
import os
from dotenv import load_dotenv
import hashlib
import pathlib
from storage import store_dict

# local imports
from model.rule_based_model import make_decision


# Get the project root directory (assuming scripts is directly under project root)
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()

# Load .env file from project root
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


# API configuration
BASE_URL = 'https://hackathon-api.mlo.sehlat.io'
API_KEY = 'KR4iOS4v-zY57HPvT7U6HCrnN08ufEg5RT7Ye-bOU4Y'
HEADERS = {"x-api-key": API_KEY}

def start_game():
    """Start a new game session and return session details"""

    url = f'{BASE_URL}/game/start'
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

    url = f'{BASE_URL}/game/decision'

    picked_decision = "Accept" if decision == 1 else "Reject"

    payload = {
        "decision": picked_decision,
        "client_id": client_id,
        "session_id": session_id
    }

    # Return also the decision (1 for Accept, 0 for Reject)
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_data = response.json()

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error making decision: {e}")
        return None


def toMd5(client_data: dict):
    """Convert client data to MD5 hash"""
    json_string = json.dumps(client_data, sort_keys=True)
    # Compute the MD5 hash
    md5_hash = hashlib.md5(json_string.encode('utf-8')).hexdigest()
    return md5_hash


def save_result(client_data, score, status, answer):
    """Save the result """

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
    
    print(f"\nGame started ...")
    
    session_id = game_data["session_id"]
    current_client_id = game_data["client_id"]
    client_data = game_data["client_data"]
    score = 0  # Starting score
    
    # Calculate delay to achieve 55 requests per minute
    delay = 60 / 55  # seconds per request
    
    # Run the queries
    queries_made = 0
    start_time = time.time()
    
    while True:  # Run indefinitely until game over

        print(f"\nChecking result for level {score} ...")
        decision = make_decision(client_data, score)
        response = send_decision(session_id, current_client_id, decision)

        queries_made += 1
        client_data = response.get("client_data", {})

        # Check if game is over
        if response["status"] == "gameover":
            print(f"\nGame over! Final score: {score}")
            
            # Save the result
            save_result(client_data, score, 0, decision)
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
