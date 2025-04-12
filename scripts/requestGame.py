import requests
import json
import time
import uuid
from datetime import datetime
import random
from dotenv import load_dotenv

load_dotenv('/Users/kareen/works/swisshacks/.env')

# import os
# from storage import store_dict
# from storage import read_dict

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
        
        print(f"Game started successfully!")
        print(f"Session ID: {response_data['session_id']}")
        print(f"Initial client ID: {response_data['client_id']}")
        
        return response_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error starting game: {e}")
        return None

def make_decision(session_id, client_id, score):
    """Make a decision (Accept or Reject) based on the score and return the response"""

    url = f'{BASE_URL}/game/decision'

    # Get the current client data to check level
    if score == 9:
        decision = "Reject"
    elif score == 10:
        decision = "Reject"
    elif score >= 11:
        decision = random.choice(["Accept", "Reject"])
    else:
        decision = "Accept"

    payload = {
        "decision": decision,
        "client_id": client_id,
        "session_id": session_id
    }

    # Return also the decision (1 for Accept, 0 for Reject)
    if decision == "Accept":
        selected_decision = 1
    else:
        selected_decision = 0

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_data = response.json()
        response_data["decision"] = selected_decision

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error making decision: {e}")
        return None

def save_result(client_data, score, status, answer):
    """Save the result """

    result = "1" if status else "0"

    print(f"\nlevel_{score}-answer_{answer}_result_{result}.json")

def run_game():
    """Run the game with 55 queries per minute"""
    game_data = start_game()
    
    if not game_data:
        print("Failed to start game. Exiting.")
        return
    
    print(f"\nGame started ...")
    
    session_id = game_data["session_id"]
    current_client_id = game_data["client_id"]
    score = 1  # Starting score
    
    # Calculate delay to achieve 55 requests per minute
    delay = 60 / 55  # seconds per request
    
    # Run the queries
    queries_made = 0
    start_time = time.time()
    
    while True:  # Run indefinitely until game over

        print(f"\nChecking result for level {score} ...")
        response = make_decision(session_id, current_client_id, score)

        queries_made += 1
        client_data = response.get("client_data", {})
        level_answer = response.get("decision")

        # Check if game is over
        if response["status"] == "gameover":
            print(f"\nGame over! Final score: {score}")
            
            # Save the result
            save_result(client_data, score, 0, level_answer)
            break

        else:
            # Update client ID and score for next request immediately after receiving the response
            current_client_id = response["client_id"]
            score = response["score"]

            # Save the result
            save_result(client_data, score, 1, level_answer)
            
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
    run_game_continuously()