
import sys
sys.path.append('./lib')

from porper.controllers.resource_controller import ResourceController

class AwsAccountController(ResourceController):

    def __init__(self, permission_connection):
        ResourceController.__init__(self, None, None, permission_connection)
        self.resource = 'aws_account'

        from aws_account import AwsAccount
        self.model = AwsAccount(permission_connection)
