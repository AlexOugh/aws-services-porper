
import json
import traceback
from slash_handler import lambda_handler as slash_handler
from handler import lambda_handler as handler

ALLOWED_RESOURCES = [
    'github_auth',
    'google_auth',
    'slack_auth',
    'sso_auth',
    'group',
    'user',
    'invited_user',
    'aws_account',
    'permission'
]

def lambda_handler(event, context):

    print('Received event:\n{}'.format(event))

    method = event['httpMethod'].lower()
    paths = event['path'].split('/')
    path = paths[len(paths)-1]
    res_type = event.get('resType')
    print('method: {}'.format(method))
    print('paths: {}'.format(paths))
    print('path: {}'.format(path))
    print('res_type: {}'.format(res_type))

    if path == 'slash':
        return slash_handler(event, context)

    resource = path
    if resource not in ALLOWED_RESOURCES:
        print("not supported resource, {}".format(resource))
        raise Exception("not found")

    query_params = event.get('queryStringParameters')
    if not query_params:
        query_params = {}
    elif isinstance(query_params, str) or isinstance(query_params, unicode):
        query_params = json.loads(query_params)
    post_data = event.get('body')
    if not post_data:
        post_data = {}
    elif isinstance(post_data, str) or isinstance(post_data, unicode):
        post_data = json.loads(post_data)
    params = post_data;
    if method == 'get':
        params = query_params;
    print('resource: {}'.format(resource))
    print('parameters: {}'.format(params))

    oper = params.get('oper')
    print('oper: {}'.format(oper
    if oper is None:
        if method == 'get':
            oper = 'find'
        elif method == 'post':
            oper = 'create'
        elif method == 'put':
            oper = 'update'
        elif method == 'delete':
            oper = 'delete'
    else:
        del params['oper']
    print('converted oper: {}'.format(oper))

    access_token = event['headers'].get('Authorization')
    print('access_token: {}'.format(access_token))

    # add 'access_token' to the params if the operation is 'authenticate' of auth controllers
    if access_token and oper == 'authenticate':
        params['access_token'] = access_token

    handler_event = {'access_token': access_token, 'resource': resource, 'oper': oper, 'params': json.dumps(params)}

    try:
        ret = handler(handler_event, context)
        response = { 'statusCode': 200 };
        if res_type and res_type == 'json':
            response['body'] = ret
        else:
            response['headers'] = { "Access-Control-Allow-Origin": "*" }
            response['body'] = json.dumps(ret)
        return response
    except Exception as ex:
        traceback.print_exc()
        err_msg = '{}'.format(ex
        if err_msg == 'not permitted':
            status_code = 401
        elif err_msg == 'unauthorized':
            status_code = 403
        elif err_msg == 'not found':
            status_code = 404
        else:
            status_code = 500
        response = { 'statusCode': status_code };
        response['headers'] = { "Access-Control-Allow-Origin": "*" }
        if res_type and res_type == 'json':
            response['body'] = err_msg
        else:
            response['body'] = json.dumps(err_msg)
        return response
