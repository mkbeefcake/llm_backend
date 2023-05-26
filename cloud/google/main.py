from __future__ import annotations

import logging
import os
import requests
from typing import Any

import flask
from flask import request
from google.oauth2.credentials import Credentials
from googleapiclient import discovery
from werkzeug.middleware.proxy_fix import ProxyFix

import auth

app = flask.Flask(__name__)
app.register_blueprint(auth.mod, url_prefix='/auth')
app.wsgi_app = ProxyFix(app.wsgi_app)

register_proxy_url = 'https://localhost:8000/register_chatbot_proxy'
get_response_url = 'https://localhost:8000/get_response'
headers = {
    'Content-Type': 'application/json'
}
register_proxy_data = { 
    "proxy": "google",
    "option" : ""
}

# Set the secret key for sessions
app.secret_key = os.environ.get('SESSION_SECRET', 'notasecret')

logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{levelname:.1}{asctime} {filename}:{lineno}] {message}')

@app.route('/', methods=['GET'])
def home():
    """Default home page"""
    return flask.render_template('home.html')

@app.route('/', methods=['POST'])
def on_event() -> (Any | dict):
    """Handler for events from Hangouts Chat."""
    if event := flask.request.get_json():
      if message := event.get('message'):
        if 'logout' in message.get('text', '').lower():
            return on_logout(event)
        else:
            return on_mention(event)
      if event['type'] == 'ADDED_TO_SPACE':
          return flask.jsonify({
              'text': (
                  'Thanks for adding me! '
                  'Try mentioning me with `@MyProfile` to see your profile.'
              )
          })
      return flask.jsonify({})

    return 'Error: Unknown action'


def on_mention(event: dict) -> dict:
    """Handles a mention from Hangouts Chat."""
    user_name = event['user']['name']    
    user_credentials = auth.get_user_credentials(user_name)
    if not user_credentials:
        logging.info('Requesting credentials for user %s', user_name)
        return flask.jsonify({
            'actionResponse': {
                'type': 'REQUEST_CONFIG',
                'url': auth.get_config_url(event),
            },
        })
    logging.info('Found existing auth credentials for user %s', user_name)

    # if message happened
    if event['type'] == 'MESSAGE':
        return flask.jsonify(get_ai_response(user_credentials, message=event['message']['text']))

    return flask.jsonify(produce_profile_message(user_credentials))


def on_logout(event) -> dict:
    """Handles logging out the user."""
    user_name = event['user']['name']
    try:
        auth.logout(user_name)
    except Exception as e:
        logging.exception(e)
        return flask.jsonify({
            'text': 'Failed to log out user %s: ```%s```' % (user_name, e),
        })
    else:
        return flask.jsonify({
            'text': 'Logged out.',
        })

def get_ai_response(user_credentials, message):
    response = requests.post(get_response_url, 
                             headers=headers,
                             json={
                                "proxy_name": "google",
                                "email": "",
                                "message": message
                             })
    return {"text": response.message}

def produce_profile_message(creds: Credentials) -> dict:
    """Generate a message containing the users profile inforamtion."""
    people_api = discovery.build('people', 'v1', credentials=creds)
    try:
        person = people_api.people().get(
            resourceName='people/me',
            personFields=','.join([
                'names',
                'addresses',
                'emailAddresses',
                'phoneNumbers',
                'photos',
            ])).execute()
    except Exception as e:
        logging.exception(e)
        return {
            'text': 'Failed to fetch profile info: ```%s```' % e,
        }
    card = {}
    if person.get('names') and person.get('photos'):
        card.update({
            'header': {
                'title': person['names'][0]['displayName'],
                'imageUrl': person['photos'][0]['url'],
                'imageStyle': 'AVATAR',
            },
        })
    widgets = []
    for email_address in person.get('emailAddresses', []):
        widgets.append({
            'keyValue': {
                'icon': 'EMAIL',
                'content': email_address['value'],
            }
        })
    for phone_number in person.get('phoneNumbers', []):
        widgets.append({
            'keyValue': {
                'icon': 'PHONE',
                'content': phone_number['value'],
            }
        })
    for address in person.get('addresses', []):
        if 'formattedValue' in address:
            widgets.append({
                'keyValue': {
                    'icon': 'MAP_PIN',
                    'content': address['formattedValue'],
                }
            })
    if widgets:
        card.update({
            'sections': [
                {
                    'widgets': widgets,
                }
            ]
        })
    if card:
        return {'cards': [card]}
    return {
        'text': 'Hmm, no profile information found',
    }


if __name__ == '__main__':
    os.environ.update({
        # Disable HTTPS check in oauthlib when testing locally.
        'OAUTHLIB_INSECURE_TRANSPORT': '1',
    })

    if not os.environ['GOOGLE_APPLICATION_CREDENTIALS']:
        raise Exception(
            'Set the environment variable GOOGLE_APPLICATION_CREDENTIALS with '
            'the path to your service account JSON file.')

    response = requests.post(register_proxy_url, 
                             headers=headers,
                             json=register_proxy_data)
    print(response)
    app.run(port=8081, debug=True)
