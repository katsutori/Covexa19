 import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import AskForPermissionsConsentCard
import requests


# Add a new intent handler class here!
# You must implement can_handle() and handle()

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = 'Hi! I heard you were curious about how you would fair against covid today.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
  """Handler for Hello World Intent."""
  def can_handle(self, handler_input):
    print('checking if we can handle')
    return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

  def handle(self, handler_input):
    speak_output = "Hello World!"

    return (
      handler_input.response_builder
          .speak(speak_output)
          .response
    )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "This intent handler is not finished yet!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # Any cleanup logic goes here.
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


#_______________________________________________________________________

permissions = ["read::alexa:device:all:address"]

#_______________________________________________________________

class GetCovidIntentHandler(AbstractRequestHandler):
  """Handler for the get blog intent"""
  def can_handle(self, handler_input):
    
    return ask_utils.is_intent_name("GetCovidIntent")(handler_input)

  def handle(self, handler_input):
    #api for CovidActNow
    api_key = '3854207e6f314c6b9ce50f47b808380b'
    base_url = "https://api.covidactnow.org/v2/"
    #request device address located in app profile
    response_builder = handler_input.response_builder
    response_builder.set_card(AskForPermissionsConsentCard(permissions=permissions))
    device = handler_input.request_envelope.context.system.device
    device_dict = device.to_dict()
    device_id = device_dict.get('device_id')
    api_access = handler_input.request_envelope.context.system.api_access_token
    #handler_input.request_envelope.context.system.user.permissions.consent_token
    headers = {'Accept':'application/json', 'Authorization':'Bearer ' + api_access}
    amazon_endpoint = f'https://api.amazonalexa.com/v1/devices/{device_id}/settings/address'
    payload = {}
    alexa_response = requests.request("GET", amazon_endpoint, headers=headers, data=payload)
    print(alexa_response)
      
    #if device has location enabled, skill pulls covid metrics for device's location that is set in profile
    if alexa_response.status_code in range (200, 203):
      state = alexa_response.json()["stateOrRegion"]
      endpoint = f"{base_url}state/{state}.json?apiKey={api_key}"
      r = requests.get(endpoint)
      cases = r.json()["actuals"]["cases"]
      deaths = r.json()["actuals"]['deaths']
      deathRate = deaths / cases
      print(deathRate)
      percentage = "{:.0%}".format(deathRate)
      if deathRate <= .01:
        speak_output = f'The number of covid cases in your state thus far is {cases}. The number of covid deaths in your state is {deaths}. That is a {percentage} death rate. Looks like you are in great shape. But remember, wear a mask, or you could be next. Bwahahahaha!'
      elif deathRate > .01 and deathRate <= .03:
        speak_output = f'The number of covid cases in your state thus far is {cases}. The number of covid deaths in your state is {deaths}. That is a {percentage} death rate. Looks like you will fair pretty well, but don\'t be too sure! Remember, wear a mask and get vaccinated, or you\'ll be adding to that number. Bwahahahaha!'
      elif deathRate > .03:
        speak_output = f'The current death rate in your state is {percentage}, and it is spiraling out of control! Hide yo kids. Hide yo wife. Wear yo mask. Get yo vaccine. It\'s coming for you. Screeeeeeeeeech!'
    #if device had location disabled, skill pulls covid metric for the entire US
    else:
      endpoint = f"{base_url}country/US.json?apiKey={api_key}"
      print(endpoint)
      r = requests.get(endpoint)
      cases = r.json()["actuals"]["cases"]
      deaths = r.json()["actuals"]['deaths']
      deathRate = deaths / cases
      percentage = "{:.0%}".format(deathRate)
      if deathRate <= .01:
        speak_output = f'If you want to see how your state is doing, remember to enable location permission the next time you use this skill. Until then, here are your chances in the United States. The number of covid cases in the US thus far is {cases}. The number of covid deaths in the US thus far is {deaths}. That is a {percentage} death rate. Looks like you are in great shape. But remember, wear a mask, or you could be next. Bwahahahaha!'
      elif deathRate > .01 and deathRate <= .03:
        speak_output = f'If you want to see how your state is doing, remember to enable location permission the next time you use this skill. Until then, here are your chances in the United States. The number of covid cases in the US thus far is {cases}. The number of covid deaths in the US thus far is {deaths}. That is a {percentage} death rate. Looks like you will fair pretty well, but don\'t be too sure! Remember, wear a mask and get vaccinated, or you\'ll be adding to that number. Bwahahahaha!'
      elif deathRate > .03:
        speak_output = f'If you want to see how your state is doing, remember to enable location permission the next time you use this skill. Until then, here are your chances in the United States. The current death rate is {percentage}, and it is spiraling out of control! Hide yo kids. Hide yo wife. Wear yo mask. Get yo vaccine. It\'s coming for you. Screeeeeeeeeech!'

    return (
      handler_input.response_builder
          .speak(speak_output)
          .response
    )