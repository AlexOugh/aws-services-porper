
from porper.models.resource import Resource

class Order(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table("orders")
