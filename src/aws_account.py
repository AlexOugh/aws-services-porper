
import sys
sys.path.append('./lib')

from porper.models.resource import Resource

class AwsAccount(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table("aws_accounts")
