from google.adk.agents import Agent
import json

# Define the internal tools as regular Python functions
def classify_incident(call_transcript: str, current_severity: str = "Medium") -> dict:
    """
    Classifies the incident type from the call transcript and identifies its urgency/severity.
    Returns a dictionary with 'incident_type', 'urgency', and 'keywords'.
    This tool performs 'Early Classification of Incidents'.
    """
    print(f"DEBUG: Classifying incident from transcript: '{call_transcript}' with current_severity: {current_severity}")
    incident_type = "Unknown"
    urgency = current_severity # Start with provided severity or default

    lower_transcript = call_transcript.lower()
    keywords = []

    if "fire" in lower_transcript or "burning" in lower_transcript:
        incident_type = "Fire"
        urgency = "High"
        keywords.append("fire")
    if "medical" in lower_transcript or "ambulance" in lower_transcript or "collapsed" in lower_transcript:
        incident_type = "Medical Emergency"
        urgency = "High"
        keywords.append("medical")
    if "crime" in lower_transcript or "theft" in lower_transcript or "robbery" in lower_transcript or "assault" in lower_transcript:
        incident_type = "Crime"
        urgency = "High"
        keywords.append("crime")

    # Severity Assessment based on keywords
    # Prioritize 'Critical' if urgency keywords are present or if a specific override is active
    if "critical" in lower_transcript or "major" in lower_transcript or "quickly" in lower_transcript or "trapped" in lower_transcript or "serious" in lower_transcript:
        if urgency in ["High", "Medium"]: # Only upgrade if not already Critical
            urgency = "Critical"

    return {"incident_type": incident_type, "urgency": urgency, "keywords": list(set(keywords))}


def extract_entities(call_transcript: str) -> dict:
    """
    Extracts key entities from the call transcript, such as locations, names,
    and specific details relevant to the emergency. This supports 'Anomaly Detection'
    and 'Prediction of Potential Threats or Hotspots'.
    Returns a dictionary of extracted entities.
    """
    print(f"DEBUG: Extracting entities from transcript: '{call_transcript}'")
    entities = {
        "location": "Location Unknown (within Bengaluru, Karnataka, India)", # Default for Bengaluru context
        "description": "Emergency reported",
        "anomalies": []
    }
    lower_transcript = call_transcript.lower()

    # Location Extraction (Prioritize specific over general)
    if "brigade road" in lower_transcript:
        entities["location"] = "Brigade Road, Bengaluru, Karnataka, India"
        if "10th cross" in lower_transcript:
            entities["location"] = "Brigade Road, 10th cross, Bengaluru, Karnataka, India"
            if "home no 36" in lower_transcript or "house no 36" in lower_transcript:
                entities["location"] = "Brigade Road, 10th cross, home no 36, Bengaluru, Karnataka, India"
    elif "mg road" in lower_transcript:
        entities["location"] = "MG Road, Bengaluru, Karnataka, India"
    elif "koramangala" in lower_transcript:
        entities["location"] = "Koramangala, Bengaluru, Karnataka, India"
    elif "indiranagar" in lower_transcript:
        entities["location"] = "Indiranagar, Bengaluru, Karnataka, India"
    elif "peenya" in lower_transcript:
        entities["location"] = "Peenya, Bengaluru, Karnataka, India"
    elif "bangalore" in lower_transcript or "bengaluru" in lower_transcript:
         pass # Handled by default or specific sub-locations

    # Description and Anomaly Detection
    incident_description_parts = []
    anomalies_detected = []

    if "collapsed" in lower_transcript:
        incident_description_parts.append("Friend collapsed")
    if "breathing heavily" in lower_transcript:
        incident_description_parts.append("breathing heavily")
    if "conscious" in lower_transcript:
        incident_description_parts.append("conscious")
    if "unconscious" in lower_transcript:
        incident_description_parts.append("unconscious")
    if "car accident" in lower_transcript:
        incident_description_parts.append("Car accident")
    if "traffic blocked" in lower_transcript:
        incident_description_parts.append("Traffic blocked")
    if "fire" in lower_transcript:
        incident_description_parts.append("Fire incident")
    if "blast" in lower_transcript:
        incident_description_parts.append("Blast occurred")
    if "robbed" in lower_transcript or "theft" in lower_transcript:
        incident_description_parts.append("Crime/Robbery reported")

    entities["description"] = ", ".join(incident_description_parts) if incident_description_parts else "Emergency reported"

    # Anomaly Detection for stressed caller / refusal to provide info
    if "not the right time" in lower_transcript or "right now" in lower_transcript or \
       "stop asking" in lower_transcript or "ambulance right now" in lower_transcript:
        anomalies_detected.append("caller stressed and unwilling to provide further information")
    
    entities["anomalies"] = anomalies_detected
    
    return entities

def generate_follow_up_questions(incident_type: str, location: str, description: str, current_anomalies: list) -> str:
    """
    Generates tailored follow-up questions for the user based on the incident details.
    This also serves as part of the 'Augmentation of Call Centers'.
    """
    # If caller is stressed/unwilling to provide more info, switch to minimal, vital questions
    if "caller stressed and unwilling to provide further information" in current_anomalies:
        return "We are dispatching an ambulance immediately. While it's on the way, could you tell me if he has any known allergies or medical conditions that we should be aware of? This information will help the paramedics provide the best care."

    # Default questions for initial interaction
    questions = []

    if "Location Unknown" in location or "near Brigade Road" in location: # General or less precise location
        questions.append("Can you please provide the exact address or cross street?")
    
    # Specific questions for Medical Emergency
    if "medical emergency" in incident_type.lower() or "collapsed" in description.lower() or "unconscious" in description.lower():
        questions.append("Is your friend conscious and breathing?")
        questions.append("How old is your friend, and do they have any known medical conditions?")
        
    # Example for other incident types if needed, similar to previous version.
    # For now, let's keep it focused on the medical example given.
    
    # If no specific questions generated, provide a general prompt
    if not questions:
        return "Thank you for the information. We are processing your request. Is there anything else you can add?"
    
    return " ".join(questions)


def process_transcript_for_orchestration_and_user_followup(call_transcript: str) -> dict:
    """
    Processes a given emergency call transcript to extract and format critical incident information
    for the Central Orchestration Agent AND generates follow-up questions for the user.
    Returns a dictionary with 'orchestration_json' and 'user_followup_message'.
    This function combines 'Early Classification', 'Severity Assessment', and 'Anomaly Detection'
    with 'Augmentation of Call Centers'.
    """
    if not call_transcript:
        return {
            "orchestration_json": json.dumps({"status": "error", "message": "No transcript provided.", "incident_source": "Emergency Call NLP Agent"}),
            "user_followup_message": "I didn't hear anything. Can you please state your emergency?"
        }

    # Step 1: Extract entities and detect anomalies first to determine context
    entities_result = extract_entities(call_transcript)
    location = entities_result.get("location", "Location Unknown")
    description = entities_result.get("description", "Emergency reported")
    anomalies = entities_result.get("anomalies", []) # Get detected anomalies

    # Determine initial severity for classification based on anomalies
    # If caller is stressed, immediately bump severity to critical
    initial_severity_for_classification = "High"
    if "caller stressed and unwilling to provide further information" in anomalies:
        initial_severity_for_classification = "Critical"

    # Step 2: Classify the incident, potentially using the bumped severity
    classification_result = classify_incident(call_transcript, current_severity=initial_severity_for_classification)
    incident_type = classification_result.get("incident_type", "Unknown")
    severity = classification_result.get("urgency", "Medium") # Use 'severity' as per your desired output

    # Construct the output for the Central Orchestration Agent based on your desired format
    output_for_orchestration_agent = {
        "incident_type": incident_type,
        "location": location,
        "description": description,
        "severity": severity, # Use the determined severity
        "anomalies": anomalies # Include anomalies detected
    }
    
    # Step 3: Generate follow-up questions for the user, sensitive to anomalies
    user_followup_message = generate_follow_up_questions(
        incident_type=incident_type,
        location=location,
        description=description,
        current_anomalies=anomalies
    )

    # Construct the final response structure
    return {
        "orchestration_json": json.dumps(output_for_orchestration_agent),
        "user_followup_message": user_followup_message
    }


# Define the Agent
basic_agent = Agent(
    model='gemini-2.0-flash-001',
    name='Emergency_Call_NLP_Agent_Transcript_Mode',
    description='An AI agent that processes emergency call transcripts, performs early incident classification, severity assessment, anomaly detection, and provides structured JSON for the Central Orchestration Agent as well as natural language follow-up questions for the user, augmenting call center operations. It also supports the prediction of potential threats or hotspots by analyzing text streams.',
    instruction=(
        'You are the Emergency Call NLP Agent, a key component of the Public Safety system in Bengaluru, Karnataka, India.'
        'Your primary function is to process raw text transcripts of emergency calls. '
        'For each transcript, you must perform two critical actions: '
        '1. **Generate Structured Incident Data for Orchestration:** Automatically categorize the incident (e.g., crime, medical, fire), assess its severity (including recognizing caller urgency for "Critical" priority), detect anomalies (like caller stress), and extract key entities like location and a concise description. This data must be formatted as a JSON string for the Central Orchestration Agent to trigger specific emergency responses. '
        '2. **Provide User Follow-up Questions:** Craft a concise, natural language response with follow-up questions to gather more specific details from the user, directly supporting human operators in augmenting call centers. If the caller indicates extreme urgency or unwillingness to provide more information (e.g., "right now", "stop asking"), prioritize confirming dispatch and ask only absolutely essential, non-blocking questions. '
        'Your final output MUST be a JSON object containing two keys: "orchestration_json" (holding the stringified JSON for the orchestration agent) '
        'and "user_followup_message" (holding the natural language questions for the user). '
        'Do NOT ask for audio data. Prioritize accuracy, speed, and complete, structured output for both parts.'
    ),
    tools=[process_transcript_for_orchestration_and_user_followup],
)

root_agent = basic_agent
