from django.shortcuts import render, redirect
from django.http import HttpResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

# Scopes required to access the user's email and profile info
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def login(request):
    creds = None
    token_file = './credentials/token.json'
    client_secrets_file = './credentials/client_secret.json'

    # Check if the token file exists and load credentials
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except ValueError as e:
            print(f"Error loading credentials from token file: {e}")

    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=8001)  # Specify a different static port
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

    try:
        # Build the service to interact with the Google API
        service = build('oauth2', 'v2', credentials=creds)

        # Fetch the user info
        user_info = service.userinfo().get().execute()

        # Extract email and name
        email = user_info['email']
        name = user_info['name']

        # Print or use the email and name
        print(f"User email: {email}")
        print(f"User name: {name}")

        user_details = [name, email]
        print(user_details)

        # Optionally save the user details to a file
        with open('./credentials/user_details.json', 'w') as file:
            json.dump(user_details, file)

        # Render the custom HTML template that closes the window
        return redirect('/chat/')
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred during login. Please try again.")


def chat(request):
    return HttpResponse('Chatting window')