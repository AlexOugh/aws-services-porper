
import json

# from porper.controllers.auth_controller import AuthController
# from porper.controllers.github_auth_controller import GithubAuthController
# from porper.controllers.google_auth_controller import GoogleAuthController
# from porper.controllers.slack_auth_controller import SlackAuthController
# from porper.controllers.sso_auth_controller import SsoAuthController
# from porper.controllers.group_controller import GroupController
# from porper.controllers.user_controller import UserController
# from porper.controllers.invited_user_controller import InvitedUserController
# from porper.controllers.permission_controller import PermissionController
#
# from aws_account_controller import AwsAccountController

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
    return ret
