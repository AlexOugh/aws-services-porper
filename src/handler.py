
import json
from porper.controllers.auth_controller import AuthController
from porper.controllers.github_auth_controller import GithubAuthController
from porper.controllers.google_auth_controller import GoogleAuthController
from porper.controllers.sso_auth_controller import SsoAuthController
#from porper.controllers.permission_controller import PermissionController
from porper.controllers.group_controller import GroupController
#from porper.controllers.token_controller import TokenController
from porper.controllers.user_controller import UserController
from porper.controllers.user_group_controller import UserGroupController
from porper.controllers.invited_user_controller import InvitedUserController

ALLOWED_RESOURCES = [
    'github_auth',
    'google_auth',
    'sso_auth',
    'group',
    'user',
    'user_group',
    'invited_user'
]

def lambda_handler(event, context):

    print 'Received event:\n%s' % json.dumps(event)

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
        ret = getattr(controller, oper)(access_token, params)
    print ret
    return ret
