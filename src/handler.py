
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

    print 'Received event:\n%s', % json.dumps(event)

    method = event['httpMethod'].lower()
    paths = event['path'].split('/')
    path = paths[len(paths)-1]
    query_params = (event.get('queryStringParameters')) ? event['queryStringParameters'] : {}
    if (query_params and isinstance(query_params, str)) query_params = json.loads(query_params)
    post_data = (event.get('body')) ? event['body'] : {}
    if (post_data and isinstance(post_data, str)) post_data = json.loads(post_data)
    https_params = post_data;
    if (method == 'get') https_params = query_params;

    print 'path: %s', % path
    resource = path
    if resource not in ALLOWED_RESOURCES: raise Exception("not supported resource : %s" % resource)

    print 'oper: %s', % https_params.get('params')
    print 'parameters: %s', % https_params.get('params')

    oper = https_params.get('oper')
    print 'oper: %s', % https_params.get('oper')
    if oper is None:
        if method == 'get':
            if params and params.get('id'):
                oper = 'find_by_id'
            else:
                oper = 'find'
        elif method == 'post':
            oper = 'create'
        elif method == 'put':
            oper = 'update'
        elif method = 'delete':
            oper = 'delete'

    params = https_params.get('params')

    import os
    import boto3
    region = os.environ.get('AWS_DEFAULT_REGION')
    dynamodb = boto3.resource('dynamodb', region_name=region)
    controller = globals()['%sController' % resource.title().replace('_', '')](dynamodb)
    if isinstance(controller, AuthController):
        ret = getattr(controller, oper)(params)
    else:
        access_token = event['headers']['authorization']
        ret = getattr(controller, oper)(access_token, params)
    print ret
    return ret
