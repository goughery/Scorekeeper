import json


spB = "<speak>"
spE = "</speak>"
def build_speechlet_response(title, output, reprompt_text, should_end_session, directives=[]):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - "
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session,
        'directives': directives
        
    }
    
    

def build_response(session_attributes, speechlet_response): #, directives = {}
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    #,'directives': [directives]

def continue_dialog(state, intentname = "", slotname="", slotvalue=""):
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    sessionAttributes = {}
    return build_response(sessionAttributes, message)
    

def addPlayers(session, intent_request={'dialogState':'In_Progress'}):
    #def add_words(session, intent_request={'dialogState':'In_Progress'}):

    
    speech_output = ""
    dialog_state = intent_request['dialogState']
    if dialog_state != "COMPLETED":
        return continue_dialog(dialog_state)
    else:
        namesSpoken = intent_request['intent']['slots']['PlayerNames']['value']
        nameList = []
        nameString = ""
        for name in namesSpoken.split(" "):
            nameList.append(name)
            nameString += name + ", "
        nameString = nameString[:-2]
        
        speech_output = "Ok, those players are %s"%(nameString)
        speech_output  = spB + speech_output + spE
        reprompt_text = speech_output
        card_title = "AddPlayersIntent"
        should_end_session = False
        return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    
def newGame(session, intent_request):
    return addPlayers(session,intent_request)

def addPlayersIntent(session,intent_request):
    return addPlayers(session,intent_request)

# --------------- Events ------------------

def get_welcome_response(session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Scorekeeper. Start a new game or continue playing?"
    speech_output = spB + speech_output + spE
    reprompt_text = speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
def on_launch(event, launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response(session)
    
    
    
    
def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    # Dispatch to your skill's intent handlers
    if intent_name == "AddPlayersIntent":
        return addPlayers(session, intent_request)
    elif intent_name == "NewGameIntent":
         return newGame(session,intent_request)
    # elif intent_name == "AddPlayersIntent":
    #     return add_words(session,intent_request)
    # elif intent_name == "AMAZON.HelpIntent":
    #     return get_help_response()
    # elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
    #     return handle_session_end_request()
    # else:
    #     return handle_session_end_request()
    #     #raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Scorekeeper skill. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    speech_output  = spB + speech_output + spE
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Main handler ------------------
def lambda_handler(event, context):
    session = event['session']

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
    else:
        return handle_session_end_request()
