
from porper.controllers.resource_controller import ResourceController

class OrderController(ResourceController):

    def __init__(self, permission_connection):
        ResourceController.__init__(self, None, None, permission_connection)
        self.resource = 'order'

        from order import Order
        self.model = Order(permission_connection)
