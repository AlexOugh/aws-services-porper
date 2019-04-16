
import json
import os
import boto3
import traceback

from porper.models.group import Group

def lambda_handler(event, context):

    print('Received event:\n{}'.format(event))

    try:
        region = os.environ.get('AWS_DEFAULT_REGION')
        dynamodb = boto3.resource('dynamodb', region_name=region)
        group = Group(dynamodb)

        params = {'id': 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'name': 'admin'}
        group.create(params)

        params = {'id': '435a6417-6c1f-4d7c-87dd-e8f6c0effc7a', 'name': 'public'}
        group.create(params)

        response = { 'statusCode': 200 };
        response['headers'] = { "Access-Control-Allow-Origin": "*" }
        response['body'] = json.dumps("successfully initialized")
        return response
    except Exception as ex:
        traceback.print_exc()
        err_msg = '%s' % ex
        response = { 'statusCode': 500 };
        response['headers'] = { "Access-Control-Allow-Origin": "*" }
        response['body'] = json.dumps(err_msg)
        return response
