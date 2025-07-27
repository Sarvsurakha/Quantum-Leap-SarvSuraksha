# test_agent_predictive_policing.py

import requests
import json
import os
import datetime

# Assuming your agent is running locally on port 5000 (default for ADK)
AGENT_URL = "http://localhost:5000/"

# Function to send input to the agent and get JSON response
def test_predictive_agent(prediction_data: dict):
    print(f"\n--- Testing Predictive Policing for Location: {prediction_data.get('location_context')} ---")
    print(f"    Time: {prediction_data.get('time_of_day')}, Day: {prediction_data.get('day_of_week')}, Events: {prediction_data.get('active_events')}")
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(AGENT_URL, data=json.dumps(prediction_data), headers=headers)

        print(f"Status Code: {response.status_code}")
        try:
            response_json = response.json()
            print("Response JSON:")
            if isinstance(response_json, str):
                try:
                    inner_json = json.loads(response_json)
                    print(json.dumps(inner_json, indent=2))
                except json.JSONDecodeError:
                    print(response_json)
            else:
                print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError:
            print("Response is not JSON:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the agent. Is it running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # IMPORTANT: Make sure your Predictive_Policing_Agent is running in a separate terminal
    # Command to run the agent (from the directory *containing* your 'app' folder):
    # /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m google.adk.cli run app

    # --- Mock Prediction Scenarios ---
    mock_prediction_scenarios = [
        # Scenario 1: Typical Weekend Night in Commercial Area (High Theft Risk)
        {
            "location_context": "MG Road, Bengaluru",
            "time_of_day": "night",
            "day_of_week": "weekend",
            "active_events": []
        },
        # Scenario 2: Weekday Morning, Low Risk
        {
            "location_context": "Koramangala, Bengaluru",
            "time_of_day": "morning",
            "day_of_week": "weekday",
            "active_events": []
        },
        # Scenario 3: Match Day Evening at Stadium (Critical Pickpocketing/Crowd Disorder Risk)
        {
            "location_context": "M. Chinnaswamy Stadium, Bengaluru",
            "time_of_day": "evening",
            "day_of_week": "matchday",
            "active_events": [{"name": "RCB Match", "location": "M. Chinnaswamy Stadium"}]
        },
        # Scenario 4: Mid-day, General Area, No Specific Risk
        {
            "location_context": "JP Nagar, Bengaluru",
            "time_of_day": "afternoon",
            "day_of_week": "weekday",
            "active_events": []
        },
        # Scenario 5: Late Night, Residential Area, Moderate Risk (Simulated recent incidents)
        {
            "location_context": "Indiranagar, Bengaluru",
            "time_of_day": "late_night",
            "day_of_week": "weekday",
            "active_events": []
        }
    ]

    # Iterate through the mock scenarios and test each one
    for scenario in mock_prediction_scenarios:
        test_predictive_agent(scenario)
