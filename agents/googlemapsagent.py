# app/agent.py

from google.adk.agents import Agent
import json
import datetime

# --- Internal Tools for the Public Communication & Alert Dissemination Agent ---

def format_alert_message(alert_data: dict) -> str:
    """
    Formats the raw alert data into a human-readable, actionable message for the public.
    """
    print(f"DEBUG: Formatting alert message for type: {alert_data.get('alert_type')}")
    
    alert_type = alert_data.get("alert_type", "Public Safety Alert").upper()
    severity = alert_data.get("severity", "Medium").upper()
    location = alert_data.get("location", "Bengaluru").upper()
    description = alert_data.get("description", "An incident has occurred.").capitalize()
    recommended_action = alert_data.get("recommended_action", "Please stay informed.").capitalize()

    message = f"[{alert_type} - {severity} ALERT] "
    
    if alert_type == "TRAFFIC ADVISORY":
        message += f"Traffic congestion in {location}. {description}. {recommended_action}."
    elif alert_type == "EMERGENCY":
        message += f"Immediate emergency in {location}. {description}. {recommended_action}."
    elif alert_type == "EVENT UPDATE":
        message += f"Important update for {location} event. {description}. {recommended_action}."
    elif alert_type == "CRIME ALERT":
        message += f"Crime alert in {location}. {description}. {recommended_action}."
    else:
        message += f"{description} in {location}. {recommended_action}."

    return message

def determine_channels_and_audience(alert_type: str, severity: str, location: str, target_audience_area: str = "") -> dict:
    """
    Determines relevant communication channels and target audience based on alert type, severity, and location.
    This supports 'Targeted Communication' and 'Multi-Channel Dissemination' [cite: none].
    """
    print(f"DEBUG: Determining channels and audience for {alert_type}, {severity}, {location}.")
    channels = []
    audience_criteria = {"geofence": location, "demographics": "all_citizens"} # Default wide audience

    # Channel selection based on severity
    if severity == "CRITICAL":
        channels.extend(["SMS", "Push Notification (Citizen App)", "Social Media (Twitter/Facebook)", "Public Display Boards"])
    elif severity == "HIGH":
        channels.extend(["Push Notification (Citizen App)", "Social Media (Twitter/Facebook)", "Public Display Boards"])
    elif severity == "MEDIUM":
        channels.extend(["Push Notification (Citizen App)", "Social Media (Twitter/Facebook)"])
    else: # Low or Information
        channels.append("Social Media (Twitter/Facebook)")

    # Audience refinement based on location or target_audience_area
    if target_audience_area and target_audience_area != location:
        audience_criteria["geofence"] = target_audience_area # More specific targeting
    
    # Specific channels for certain alert types
    if alert_type == "TRAFFIC ADVISORY":
        if "Traffic Management Center" not in channels: # Avoid duplicates
            channels.append("Traffic Management Center Display") # For internal use/specific displays
            
    # Remove duplicates
    channels = list(set(channels))

    return {"channels": channels, "audience_criteria": audience_criteria}

def disseminate_alert(formatted_message: str, channels: list, audience_criteria: dict) -> dict:
    """
    Simulates sending the alert via various communication channels.
    This is where conceptual calls to FCM, SMS API, Twitter API would go.
    """
    print(f"DEBUG: Simulating dissemination of alert via channels: {channels} to audience: {audience_criteria}")
    dissemination_status = {"status": "success", "channels_used": [], "details": []}

    for channel in channels:
        if channel == "SMS":
            # Simulate SMS API call
            print(f"INFO: Sending SMS alert: '{formatted_message}' to {audience_criteria.get('geofence', 'affected area')}")
            dissemination_status["channels_used"].append("SMS")
            dissemination_status["details"].append("SMS simulated successfully.")
        elif channel == "Push Notification (Citizen App)":
            # Simulate Firebase Cloud Messaging (FCM) call
            print(f"INFO: Sending Push Notification via FCM: '{formatted_message}' to Citizen App users in {audience_criteria.get('geofence', 'Bengaluru')}")
            dissemination_status["channels_used"].append("Push Notification")
            dissemination_status["details"].append("Push Notification simulated successfully.")
        elif channel == "Social Media (Twitter/Facebook)":
            # Simulate Twitter/Facebook API call
            print(f"INFO: Posting to Social Media: '{formatted_message}'")
            dissemination_status["channels_used"].append("Social Media")
            dissemination_status["details"].append("Social Media post simulated successfully.")
        elif channel == "Public Display Boards":
            # Simulate interface with public display systems
            print(f"INFO: Updating Public Display Boards in {audience_criteria.get('geofence', 'Bengaluru')}: '{formatted_message}'")
            dissemination_status["channels_used"].append("Public Display Boards")
            dissemination_status["details"].append("Public Display Boards update simulated successfully.")
        elif channel == "Traffic Management Center Display":
            print(f"INFO: Sending to Traffic Management Center Display: '{formatted_message}'")
            dissemination_status["channels_used"].append("Traffic Management Center Display")
            dissemination_status["details"].append("TMC Display update simulated successfully.")
        else:
            print(f"WARNING: Unknown channel: {channel}. Alert not disseminated via this channel.")
            dissemination_status["details"].append(f"Failed to disseminate via {channel}.")
            dissemination_status["status"] = "partial_success" if dissemination_status["status"] == "success" else "failure"

    return dissemination_status

# --- Main Processing Function for the Agent ---
def disseminate_public_alert(alert_input: dict) -> str:
    """
    Disseminates public safety alerts and advisories to citizens via multiple channels.
    This agent enables 'Targeted Communication', 'Multi-Channel Dissemination',
    and 'Proactive Public Guidance' [cite: none].
    """
    print(f"DEBUG: Receiving alert input for dissemination: {json.dumps(alert_input)}")

    # Validate essential input parameters
    required_params = ["alert_type", "severity", "location", "description", "recommended_action"]
    if not all(param in alert_input for param in required_params):
        return json.dumps({"status": "error", "message": "Missing required alert parameters.", "received_input": alert_input})

    # 1. Format the alert message
    formatted_message = format_alert_message(alert_input)

    # 2. Determine appropriate channels and audience
    channels_audience = determine_channels_and_audience(
        alert_input["alert_type"],
        alert_input["severity"],
        alert_input["location"],
        alert_input.get("target_audience_area", "")
    )
    channels = channels_audience["channels"]
    audience_criteria = channels_audience["audience_criteria"]

    # 3. Disseminate the alert
    dissemination_result = disseminate_alert(formatted_message, channels, audience_criteria)

    # Construct the final output for confirmation/logging
    final_output = {
        "timestamp": datetime.datetime.now().isoformat(),
        "original_alert_input": alert_input,
        "formatted_alert_message": formatted_message,
        "dissemination_status": dissemination_result["status"],
        "channels_used": dissemination_result["channels_used"],
        "dissemination_details": dissemination_result["details"],
        "target_audience_criteria": audience_criteria,
        "source_agent": "Public Communication & Alert Dissemination Agent"
    }

    # --- Conceptual Firestore Write (for Audit/Logging) ---
    # This agent would log its dissemination actions to a 'dissemination_logs' collection.
    # db = firestore.Client(project="YOUR_GCP_PROJECT_ID")
    # doc_ref = db.collection("dissemination_logs").add(final_output)
    # print(f"INFO: Wrote dissemination log to Firestore: {doc_ref.id}")
    print(f"DEBUG: Simulating Firestore write to 'dissemination_logs' collection: {json.dumps(final_output)}")

    return json.dumps(final_output)


# --- Agent Definition ---
basic_agent = Agent(
    model='gemini-2.0-flash-001',
    name='Public_Communication_Alert_Dissemination_Agent',
    description=(
        'An AI agent responsible for disseminating public safety alerts and advisories to citizens '
        'via multiple channels. It ensures **Targeted Communication**, **Multi-Channel Dissemination**, '
        'and **Proactive Public Guidance** [cite: none]. It receives critical alerts and advisories '
        'from other Public Safety Agents (e.g., Central Orchestration Agent, Traffic Management Agent) '
        'and translates them into actionable public messages, simulating delivery via SMS, push notifications '
        '(Firebase Cloud Messaging), social media, and public displays.'
    ),
    instruction=(
        'You are the Public Communication & Alert Dissemination Agent. Your role is to receive structured '
        'alert inputs (e.g., incident type, severity, location, description, recommended action) from other agents. '
        'You must format this information into a clear, concise public alert message. '
        'Then, determine the most effective communication channels and target audience based on the alert\'s '
        'severity and location. Finally, simulate the dissemination of this alert through the identified channels. '
        'Your final output MUST be a structured JSON string confirming the alert dissemination status, '
        'the message sent, and the channels used. Do NOT ask for additional information; your processing is based on the given input.'
    ),
    tools=[disseminate_public_alert], # The main tool for this agent
)

root_agent = basic_agent
