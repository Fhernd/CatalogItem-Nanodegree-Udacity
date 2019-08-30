#!/usr/bin/env python3

import json
import sys

from flask import (jsonify, request, make_response)
from google.oauth2 import id_token
from google.auth.transport import requests


try:
    SECRET_DATA = json.loads(open('client_secrets.json', 'r').read())['web']
    CLIENT_ID = SECRET_DATA['client_id']
    CLIENT_SECRET = SECRET_DATA['client_secret']

    # Get the redirect uri from the file in the form of '/url'
    CLIENT_REDIRECT = SECRET_DATA['redirect_uris'][0]
    CLIENT_REDIRECT = '/%s' % (CLIENT_REDIRECT.split('/')[-1])
except IOError as ioe:
    print('Error: Download \'client_secrets.json\' file from Google Console')
    print(ioe.pgerror)
    print(ioe.diag.message_detail)
    sys.exit(1)


def Google_Callback():
    """
    Callback for login request.
    """
    user_data = None

    try:
        # Check if the POST request is trying to log in
        if 'idtoken' in request.form:
            # Get the token from the POST form
            token = request.form['idtoken']

            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                CLIENT_ID
            )

            verified_providers = [
                'accounts.google.com',
                'https://accounts.google.com'
            ]

            if idinfo['iss'] not in verified_providers:
                raise ValueError('Wrong issuer.')

            # ID token is valid.
            # Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']

            # Add the token to the flask session variable
            user_data = {
                'name': idinfo['name'],
                'email': idinfo['email'],
                'picture': idinfo['picture']
            }

    except ValueError as e:
        print('error ->', e)
        # Invalid token
        print('Error: Unable to verify the token id')

    if user_data:
        user_data_json = json.dumps(user_data)
    else:
        user_data_json = None

    return user_data_json
