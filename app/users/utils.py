import os.path
from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
from email.mime.text import MIMEText
import pickle
from app.models import User


def send__email(user, type):
  '''
  :param user: models.User object
  :param type: 0: account activation; 1: password reset
  '''

  SCOPES = ['https://mail.google.com/']
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  # if os.path.exists(current_app.config['OAUTH2_TOKEN']):
  #     creds = Credentials.from_authorized_user_file(current_app.config['OAUTH2_TOKEN'], SCOPES)
  # else:
  #   raise FileNotFoundError()
  # print("0")

  if os.path.exists('token.pickle'):

    # Read the token from the file and store it in the variable creds
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)

  # If credentials are not available or are invalid, ask the user to log in.
  if not creds or not creds.valid:
    if user.admin:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(current_app.config['OAUTH2_TOKEN'], SCOPES)
        creds = flow.run_local_server(port=0)

      # Save the access token in token.pickle file for the next run
      with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
  try:
    service = build('gmail', 'v1', credentials=creds)
    if type == 0:
      account_token = user.get_activation_token()
      message = MIMEText(f'''<!DOCTYPE html>
      <html lang="en">
        <head>
          <style>
            body {{
              width: 100%;
            }}
            .content {{
              width: 80%;
              margin-left: auto;
              margin-right: auto;
            }}
            img {{
                max-width: 100%;
                margin-bottom: 150px;
            }}
            .message {{
                font-size: 1rem;
                font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
                color: rgb(61, 61, 61);
                line-height: 40px;
                white-space: pre-line;
            }}
            .greeting {{
                font-size: 20px;
                color: black;
                margin-bottom: 20px;
            }}
            .confirm {{
              font-size: 18px;
                background-color: rgb(0, 89, 255);
                color: white;
                padding: 5px;
                margin-top: 30px;
            }}
            .muted {{
                font-weight: 200;
                color: rgb(145, 145, 145);
            }}
          </style>
        </head>

        <body>
          <div class="content">
            <img src="https://e0.flightcdn.com/images/nav/flightaware-logo.png" alt="logo">
            <p class="message"><span class="greeting">Hello {user.firstName},</span>
                <br>Your FlightAlert account has been successfully created.  
                <br>Please, confirm your email to activate your account. 
                <br>The account will be deleted automatically if you do not confirm it. 
            </p>
            <a class="confirm" href="account/confirm/{account_token}">Confirm Email</a>
            <p class="muted">If you did not request this email, you can simply ignore it. No account will be confirmed if you do not click the link above.</p>
          </div>
        </body>
      </html>''')
      message['Subject'] = 'FlightAlert Account Activation'
    elif type == 1:
      account_token = user.get_reset_token()
      message = MIMEText(f'''<!DOCTYPE html>
      <html lang="en">
        <head>
          <style>
            body {{
              width: 100%;
            }}
            .content {{
              width: 80%;
              margin-left: auto;
              margin-right: auto;
            }}
            img {{
                max-width: 100%;
                margin-bottom: 150px;
            }}
            .message {{
                font-size: 1rem;
                font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
                color: rgb(61, 61, 61);
                line-height: 40px;
                white-space: pre-line;
            }}
            .greeting {{
                font-size: 20px;
                color: black;
                margin-bottom: 20px;
            }}
            .confirm {{
              font-size: 18px;
                background-color: rgb(0, 89, 255);
                color: white;
                padding: 5px;
                margin-top: 30px;
            }}
            .muted {{
                font-weight: 200;
                color: rgb(145, 145, 145);
            }}
          </style>
        </head>

        <body>
          <div class="content">
            <img src="https://e0.flightcdn.com/images/nav/flightaware-logo.png" alt="logo">
            <p class="message"><span class="greeting">Forgot your password?</span>
                <br>That's okay, it happens!  
                <br>Click the link below to reset your FlightAlert password 
            </p>
            <a class="confirm" href="reset_password/{account_token}">Confirm Email</a>
            <p class="muted">If you did not request this email, you can simply ignore it. Your password will not change if you click do not click the link above.</p>
          </div>
        </body>
      </html>''')
      message['Subject'] = 'FlightAlert password reset'
    message.set_type('text/html')
    message['To'] = user.email
    message['From'] = 'noreply.airportactivity@gmail.com'
    print(message['To'])
    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'raw': encoded_message
    }
    # pylint: disable=E1101
    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(F'An error occurred: {error}')
    send_message = None


