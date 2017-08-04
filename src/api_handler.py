
import json
from handler import lambda_handler as handler

def lambda_handler(event, context):

    print 'Received event:\n%s' % json.dumps(event)

    method = event['httpMethod'].lower()
    paths = event['path'].split('/')
    path = paths[len(paths)-1]
    query_params = event.get('queryStringParameters')
    if not query_params:
        query_params = {}
    elif isinstance(query_params, str):
        query_params = json.loads(query_params)
    post_data = event.get('body')
    if not post_data:
        post_data = {}
    elif isinstance(post_data, str):
        post_data = json.loads(post_data)
    https_params = post_data;
    if method == 'get':
        https_params = query_params;

    print 'path: %s' % path
    resource = path

    params = https_params.get('params')
    oper = https_params.get('oper')
    print 'parameters: %s' % params
    print 'oper: %s' % oper

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
        elif method == 'delete':
            oper = 'delete'

    access_token = event['headers'].get('Authorization')
    print 'converted oper: %s' % oper
    print 'access_token: %s' % access_token

    handler_event = {'access_token': access_token, 'resource': resource, 'oper': oper, 'params': json.dumps(params)}

    return handler(handler_event, context)
