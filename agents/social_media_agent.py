# test_agent.py

import requests
import json
import os
import base64

# Assuming your agent is running locally on port 5000 (default for ADK)
AGENT_URL = "http://localhost:5000/"

# Function to send input to the agent and get JSON response
def test_agent_with_report(report_data: dict):
    print(f"\n--- Testing with report: {report_data.get('report_text', 'N/A')[:50]}... ({report_data.get('report_source')}) ---")
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(AGENT_URL, data=json.dumps(report_data), headers=headers)

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
    except FileNotFoundError:
        print(f"Error: Audio file not found at {audio_file_path}") # This line is a remnant, but harmless here
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Dummy Data for Testing ---
DUMMY_FIRE_IMAGE_B64 = base64.b64encode(b"fire_image_content_sim").decode('utf-8')
DUMMY_MOB_IMAGE_B64 = base64.b64encode(b"mob_image_content_sim").decode('utf-8')
DUMMY_GENERIC_IMAGE_B64 = base64.b64encode(b"generic_image_content_sim").decode('utf-8')

if __name__ == "__main__":
    # IMPORTANT: Make sure your Social_Media_Citizen_Report_Agent is running in a separate terminal
    # before you run this test script.
    # Command to run the agent (from the directory *containing* your 'app' folder):
    # /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m google.adk.cli run app

    # --- Use Cases ---

    # Scenario 1: High-Priority Public Order Concern (Social Media)
    test_agent_with_report({
        "report_text": "Massive crowd blocking traffic near Town Hall, things are getting heated! #BengaluruProtest",
        "report_source": "Social Media"
    })

    # Scenario 2: Citizen Report - Medical Emergency with Text and Generic Image
    test_agent_with_report({
        "report_text": "My friend collapsed near the park entrance at Koramangala, he's not moving. I've attached a picture.",
        "report_image_b64": DUMMY_GENERIC_IMAGE_B64,
        "report_source": "Citizen App"
    })
    
    # Scenario 3: Low-Priority Information/Noise (Social Media)
    test_agent_with_report({
        "report_text": "Traffic is really bad on Outer Ring Road today. So frustrating!",
        "report_source": "Social Media"
    })

    # Scenario 4: Citizen App Report - Utility Issue (Text Only)
    test_agent_with_report({
        "report_text": "Power has been out in our apartment in JP Nagar for over 5 hours. When will it be restored?",
        "report_source": "Citizen App"
    })

    # Scenario 5: Suspicious Activity (Text & Generic Image)
    test_agent_with_report({
        "report_text": "There's a suspicious looking person loitering around the school gate in Malleshwaram. Attaching a photo.",
        "report_image_b64": DUMMY_GENERIC_IMAGE_B64,
        "report_source": "Citizen App"
    })

    # Scenario 6: Social Media - Chaos/Stampede at RCB Match (Text Only)
    test_agent_with_report({
        "report_text": "Absolute chaos at RCB match, stampede near gate 3! Need help! #RCB #Bengaluru #Stampede #Chinnaswamy",
        "report_source": "Social Media"
    })

    # Scenario 7: Social Media - RCB Celebration Crowd/Traffic Concern (Text Only) - Pre-event build-up
    test_agent_with_report({
        "report_text": "Going for the RCB match now (3 hours early!) and the metro is already absolutely packed at Majestic station. Roads near Chinnaswamy are choked too. This is going to be crazy later! #RCB #BengaluruTraffic #MatchDay",
        "report_source": "Social Media"
    })

    # Additional Scenario: Citizen App Report - Fire with specific image content
    test_agent_with_report({
        "report_text": "There's a fire, it looks bad! See the smoke in the picture.",
        "report_image_b64": DUMMY_FIRE_IMAGE_B64,
        "report_source": "Citizen App"
    })

    # Additional Scenario: Social Media Report - Mob with specific image content
    test_agent_with_report({
        "report_text": "Huge mob gathering at city center, police not here yet!",
        "report_image_b64": DUMMY_MOB_IMAGE_B64,
        "report_source": "Social Media"
    })
