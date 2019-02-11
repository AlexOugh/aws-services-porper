
import os
import json
import urllib
import shlex
import traceback

import sys
sys.path.append('./lib')

from porper.controllers.auth_controller import AuthController
from porper.controllers.github_auth_controller import GithubAuthController
from porper.controllers.google_auth_controller import GoogleAuthController
from porper.controllers.slack_auth_controller import SlackAuthController
from porper.controllers.sso_auth_controller import SsoAuthController
from porper.controllers.group_controller import GroupController
from porper.controllers.user_controller import UserController
from porper.controllers.invited_user_controller import InvitedUserController
from porper.controllers.permission_controller import PermissionController
from porper.models.user import User

from aws_account_controller import AwsAccountController
#from slackclient import SlackClient

import os
import boto3
region = os.environ.get('AWS_DEFAULT_REGION')
dynamodb = boto3.resource('dynamodb', region_name=region)

auth_endpoint = os.environ.get('SLACK_AUTH_ENDPOINT')
client_id = os.environ.get('SLACK_CLIENT_ID')
slash_command_token = os.environ.get('SLACK_SLASH_COMMAND_TOKEN')
#legacy_token = os.environ.get('SLACK_LEGACY_TOKEN')

def lambda_handler(event, context):

    print 'Received event:\n%s' % json.dumps(event)

    try:
        body = event['body']
        print 'Received body = %s' % body
        params = {}
        param_strs = body.split('&')
        for str in param_strs:
            splitted = str.split('=')
            params[splitted[0]] = splitted[1]
            print 'param %s = %s' % (splitted[0], splitted[1])

        if params.get('token') != slash_command_token:
            return _send_response("This request is not from Slack!!")

        text = urllib.unquote(params.get('text')).replace('+', ' ')
        args = shlex.split(text)
        if len(args) == 1:
            return globals()['%s' % (args[0])](params['user_id'], params['team_id'])
        else:
            return globals()['%s_%s' % (args[0], args[1])](params['user_id'], params['team_id'], *args[2:])
    except Exception, ex:
        traceback.print_exc()
        err_msg = '%s' % ex
        if err_msg == 'unauthorized' or err_msg == 'not permitted':
            return _send_response("You're not allowed. Please contact the Administrator")
        else:
            attachments = [ { "text": err_msg } ]
            return _send_response("Error happened", attachments)

def _send_response(text, attachments=None):
    response = { 'statusCode': 200 };
    response_body = {
        "response_type": "ephemeral",
        "text": text
    }
    if attachments:
        response_body["attachments"] = attachments
    response['body'] = json.dumps(response_body)
    print 'response = %s' % response
    return response

"""def _find_user(user_id):
    sc = SlackClient(legacy_token)
    users = sc.api_call("users.list")["members"]
    print '%s' % users
    for user in users:
        if user_id == user["id"]:
            return user
    return None

def _find_invited(user_id, team_id):

    user = _find_user(user_id)
    if user is None:    return []

    user_id = '%s-%s' % (team_id, user_id)
    invited_user_controller = InvitedUserController(dynamodb)
    items = invited_user_controller.find_using_user_id(user_id, {'email': user["profile"]["email"], 'auth_type': 'slack'})
    print 'invited users : %s' % items
    return items"""

def _authenticate(user_id, team_id):

    user_id = '%s-%s' % (team_id, user_id)

    user_controller = UserController(dynamodb)
    item = user_controller.find_using_user_id(user_id, {'id': user_id})
    if item is None:
        return None

    group_controller = GroupController(dynamodb)
    items = group_controller.find_using_user_id(user_id, {})
    print 'groups found : %s' % items
    return items

def activate(user_id, team_id):

    #invited_users = _find_invited(user_id, team_id)
    #if len(invited_users) == 0:
    #    print 'no user found with %s-%s' % (team_id, user_id)
    #    return _send_response("You're not allowed. Please contact the Administrator")

    attachments = [ { "text": '%s/authorize?client_id=%s&scope=identity.basic,identity.email' % (auth_endpoint, client_id) } ]
    return _send_response("Please connect to the link to activate your account", attachments)

def add_account(user_id, team_id, account_id, account_name, role_name, external_id):

    print 'add_account'
    print 'user_id = %s' % user_id
    print 'team_id = %s' % team_id
    print 'account_id = %s' % account_id
    print 'account_name = %s' % account_name
    print 'role_name = %s' % role_name
    print 'external_id = %s' % external_id

    if _authenticate(user_id, team_id) is None:
        print 'no user found with %s-%s' % (team_id, user_id)
        return _send_response("You're not allowed. Please contact the Administrator")

    user_id = '%s-%s' % (team_id, user_id)
    aws_account_controller = AwsAccountController(dynamodb)
    aws_account_controller.create_using_user_id(user_id, {"id": account_id, "name": account_name, "role_name": role_name, "external_id": external_id})

    attachments = [ { "text": 'new account: %s - %s' % (account_id, account_name) } ]
    return _send_response("A new account is added", attachments)

def invite_user(user_id, team_id, new_user_str, to=None, user_type=None):

    new_user_info = new_user_str.replace('<', '').replace('>', '').split('|')
    new_user_id = new_user_info[0][1:]
    new_user_name = new_user_info[1]
    to = "as"
    if user_type:
        is_admin = True
    else:
        is_admin = False
        user_type = 'user'
    print 'add_user'
    print 'user_id = %s' % user_id
    print 'team_id = %s' % team_id
    print 'new_user_name = %s' % new_user_name
    print 'new_user_id = %s' % new_user_id
    print 'is_admin = %s' % is_admin

    #new_user = _find_user(new_user_id)
    #if not new_user:
    #    print 'no slack user found with %s' % (new_user_id)
    #    return _send_response("The specified user does not exist in Slack")

    groups = _authenticate(user_id, team_id)
    if groups is None:
        print 'no user found with %s-%s' % (team_id, user_id)
        return _send_response("You're not allowed. Please contact the Administrator")

    if not groups:
        print "something is not right because this user does not belong to any group"
        return _send_response("You do not belong to any group. Please contact Administrator")

    user_id = '%s-%s' % (team_id, user_id)
    invited_user_controller = InvitedUserController(dynamodb)
    #invited_user_controller.create_using_user_id(user_id, {'email':new_user["profile"]["email"], 'group_id': groups[0]['id'], 'is_admin': is_admin, 'auth_type': 'slack', 'slack_team_id': team_id})
    invited_user_controller.create_using_user_id(user_id, {'email': '%s-%s' % (team_id, new_user_id), 'group_id': groups[0]['id'], 'is_admin': is_admin, 'auth_type': 'slack', 'slack_team_id': team_id})

    attachments = [ { "text": 'new user: %s' % new_user_name } ]
    return _send_response("A new user is invited %s %s. Please ask the user to activate first using '/porper activate'" % (to, user_type), attachments)

def list_accounts(user_id, team_id):
    return list_account(user_id, team_id)

def list_account(user_id, team_id):

    print 'list_account'
    print 'user_id = %s' % user_id
    print 'team_id = %s' % team_id

    if _authenticate(user_id, team_id) is None:
        print 'no user found with %s-%s' % (team_id, user_id)
        return _send_response("You're not allowed. Please contact the Administrator")

    user_id = '%s-%s' % (team_id, user_id)
    aws_account_controller = AwsAccountController(dynamodb)
    items = aws_account_controller.find_using_user_id(user_id, {})
    attachments = []
    for item in items:
        attachments.append({ "text": ' account: %s - %s' % (item['id'], item['name']) })
    return _send_response("%d account(s) found" % (len(items)), attachments)

def list_users(user_id, team_id):
    return list_user(user_id, team_id)

def list_user(user_id, team_id):

    print 'list_user'
    print 'user_id = %s' % user_id
    print 'team_id = %s' % team_id

    if _authenticate(user_id, team_id) is None:
        print 'no user found with %s-%s' % (team_id, user_id)
        return _send_response("You're not allowed. Please contact the Administrator")

    user_id = '%s-%s' % (team_id, user_id)
    user_controller = UserController(dynamodb)
    items = user_controller.find_using_user_id(user_id, {})
    attachments = []
    for item in items:
        print item
        attachments.append({ "text": ' user: %s' % (item['name']) })
    return _send_response("%d user(s) found" % (len(items)), attachments)
