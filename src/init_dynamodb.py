
import os
region = os.environ.get('AWS_DEFAULT_REGION')

import boto3
dynamodb = boto3.resource('dynamodb', region_name=region)

from porper.models.group import Group
group = Group(dynamodb)

params = {'id': 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'name': 'admin'}
group.create(params)

params = {'id': '435a6417-6c1f-4d7c-87dd-e8f6c0effc7a', 'name': 'public'}
group.create(params)
