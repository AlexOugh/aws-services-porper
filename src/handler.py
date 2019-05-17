
import json

from porper.controllers.auth_controller import AuthController
from porper.controllers.github_auth_controller import GithubAuthController
from porper.controllers.google_auth_controller import GoogleAuthController
from porper.controllers.slack_auth_controller import SlackAuthController
from porper.controllers.cognito_auth_controller import CognitoAuthController
from porper.controllers.sso_auth_controller import SsoAuthController
from porper.controllers.group_controller import GroupController
from porper.controllers.user_controller import UserController
from porper.controllers.invited_user_controller import InvitedUserController
from porper.controllers.permission_controller import PermissionController
from porper.controllers.function_controller import FunctionController
from porper.controllers.role_controller import RoleController
from porper.controllers.token_controller import TokenController

from aws_account_controller import AwsAccountController

import os
smtp_server = os.environ.get('SMTP_SERVER')
smtp_port = os.environ.get('SMTP_PORT')
smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')
signup_sender = os.environ.get('SIGN_UP_SENDER')
signup_server = os.environ.get('SIGN_UP_SERVER')
print(smtp_server)
print(smtp_port)
print(smtp_username)
print(smtp_password)
print(signup_sender)
print(signup_server)

import sys
sys.path.append('./lib')

def lambda_handler(event, context):

    print('Received event:\n{}'.format(json.dumps(event)))

    access_token = event.get('access_token')
    resource = event['resource']
    oper = event['oper']
    params = json.loads(event['params'])

    import os
    import boto3
    region = os.environ.get('AWS_DEFAULT_REGION')
    dynamodb = boto3.resource('dynamodb', region_name=region)
    controller = globals()['%sController' % resource.title().replace('_', '')](dynamodb)
    if isinstance(controller, AuthController):
        ret = getattr(controller, oper)(params)
    else:
        if not access_token:    raise Exception("unauthorized")
        ret = getattr(controller, oper)(access_token, params)
    print(ret)

    # send an sign up email
    if resource == 'invited_user' and (oper == "create" or oper == "update"):
        try:
            send_email(params['email'])
        except Exception as ex:
            print(ex)
    return ret


def send_email(to_addr):

    import smtplib

    # creates SMTP session
    server = smtplib.SMTP(smtp_server, int(smtp_port))

    # start TLS for security
    server.ehlo()
    server.starttls()

    # Authentication
    server.login(smtp_username, smtp_password)

    # message to be sent
    from_addr = signup_sender
    subject = "Welcome to AFactor Application!"
    body = "Please click this link to sign up, https://{}/auth/sign-up?email={}".format(signup_server, to_addr)

    message = """From: {}\nTo: {}\nSubject: {}\n\n{}
    """.format(from_addr, to_addr, subject, body)
    # sending the mail
    server.sendmail(from_addr, to_addr, message)

    # terminating the session
    server.quit()
