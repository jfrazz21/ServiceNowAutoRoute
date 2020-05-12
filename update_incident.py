# REQUIRED IMPORTS FOR DIALOGFLOW
#import os
#import dialogflow_v2 as dialogflow
#from google.api_core.exceptions import InvalidArgument
#======================================================#
import requests
import joblib
import sklearn
import json

PRIMARY_URL = 'https://dev64130.service-now.com'  # Company's Servicenow URL
USERNAME = 'admin'  # Servicenow Username
PASSWORD = '2aNYt5xlxDUQ'  # Servicenow Password

# Used to check if newly received ticket has a different number than the previous one
previous_incident_number = '1'

#==================================================================#
# DIALOGFLOW PRELIMINARY SETUP
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
# DIALOGFLOW_PROJECT_ID = 'autoassign-jhyguw'  # ProjectID
# DIALOGFLOW_LANGUAGE_CODE = 'en-US'  # Language
# SESSION_ID = 'me'
#==================================================================#


# gets the number of the most recently created incident
def get_latest_incident_number():
    #url queries for most recently created incident
    url = PRIMARY_URL + \
        '/api/now/table/incident?sysparm_query=ORDERBYDESCsys_created_on&sysparm_limit=1'

    # Set proper headers
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    # Do the HTTP request
    response = requests.get(url, auth=(USERNAME, PASSWORD), headers=headers)

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:',
              response.headers, 'Error Response:', response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    number = data['result'][0]['number']

    # number will need to remove 'INC' if Dialogflow is used
    # number = number[3:len(number)]
    # while number[0] == '0':
    # number = number[1:len(number)]

    sys_id = data['result'][0]['sys_id']
    short_desc = data['result'][0]['short_description']
    assignment_group = data['result'][0]['assignment_group']
    return [number, sys_id, short_desc, assignment_group] # Sends array with number, sys_id, and short_desc


def send_assignment_group(sys_id, assignment_group):
    url = PRIMARY_URL+'/api/now/table/incident/'+sys_id

    # Set proper headers
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    # Do the HTTP request
    response = requests.patch(url, auth=(USERNAME, PASSWORD), headers=headers,
                              data="{\"assignment_group\":\""+assignment_group+"\"}")

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:',
              response.headers, 'Error Response:', response.json())
        exit()

#Compares the new ticket's short description to the model
def compare_to_model(short_desc):
    loaded_model = joblib.load('D:/School/445/AeritaeAutoRoute/update_incident/model.pkl') #load the model
    X_test = []
    X_test.append(short_desc) #Test against the new ticket's short description
    pred_cat = loaded_model.predict(X_test) #Predict an assignment group
    val1 = str(pred_cat[0])
    prob_val = loaded_model.predict_proba(X_test) #Calculate the probability that it fits into each assignment group
    val2 = max(prob_val[0])
    data = {}
    data['predicted'] = val1
    data['probability'] = val2
    assignment_group = val1
    return assignment_group


while True:
    data = get_latest_incident_number()
    #checks to see if new incident number is the same as previous incident number and checks to see if assignment group is empty
    if data[0] != previous_incident_number and data[3] == '':
        previous_incident_number = data[0]
        assignment_group = compare_to_model(data[2])
        print(data[2])
        print(assignment_group)
        send_assignment_group(data[1], assignment_group)
        # =======================================================================
        # BELOW IS THE CODE TO CONNECT TO DIALOGFLOW IF REQUESTED
        # =======================================================================
        # text_to_be_analyzed = "Update incident "+data[0]
        # session_client = dialogflow.SessionsClient()
        # session = session_client.session_path(
        #     DIALOGFLOW_PROJECT_ID, SESSION_ID)

        # # IGNORE THE ERRORS BELOW (they may not appear though)
        # text_input = dialogflow.types.TextInput(
        #     text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
        # query_input = dialogflow.types.QueryInput(text=text_input)
        # # IGNORE THE ERRORS ABOVE

        # try:
        #     response = session_client.detect_intent(
        #         session=session, query_input=query_input)
        # except InvalidArgument:
        #     raise

        # print("Query text:", response.query_result.query_text)
        # print("Detected intent:", response.query_result.intent.display_name)
        # print("Detected intent confidence:",
        #       response.query_result.intent_detection_confidence)
        # print("Fulfillment text:", response.query_result.fulfillment_text)
        
