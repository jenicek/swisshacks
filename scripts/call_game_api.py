#!/usr/bin/env python
"""
Script to call the game API at hackathon-api.mlo.sehlat.io

Usage:
    python call_game_api.py --player-name NAME --player-id ID [--api-key KEY]
"""

import argparse
import requests
import json
import sys


def start_game(player_name, player_id, api_key):
    """
    Start a new game session for the player.
    
    Args:
        player_name (str): The name of the player
        player_id (str): The ID of the player
        api_key (str): API key for authentication
    
    Returns:
        dict: The response from the API
    """
    url = "https://hackathon-api.mlo.sehlat.io/game/start"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    
    # Add API key to headers if provided - try multiple common API key header formats
    if api_key:
        # Try different common API key header formats
        headers["X-API-Key"] = api_key
        headers["x-api-key"] = api_key
        headers["api_key"] = api_key
        headers["apikey"] = api_key
        # Keep the Bearer format as well
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "player_name": player_name,
        "player_id": player_id
    }
    
    print(f"Sending request to: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        if response.status_code == 400:
            print(f"Error details: {response.text}", file=sys.stderr)
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Call the game API to start a new game session")
    parser.add_argument("--player-name", required=True, help="Name of the player")
    parser.add_argument("--player-id", required=True, help="ID of the player")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--output", "-o", help="Output file for the response (default: stdout)")
    args = parser.parse_args()
    
    # Call the API
    response = start_game(args.player_name, args.player_id, args.api_key)
    
    if response:
        # Format the response as JSON
        formatted_response = json.dumps(response, indent=2)
        
        # Output to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(formatted_response)
            print(f"Response written to: {args.output}")
        else:
            print(formatted_response)
        
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())