import json
from girder.api import access
from girder.api.rest import Resource
from girder.api.describe import Description, autoDescribeRoute
from girder.models.setting import Setting


class VipApplicationsHandler(Resource):
    DEFAULT_USER = 'ANONYMOUS'

    def __init__(self):
        super(VipApplicationsHandler, self).__init__()
        self.resourceName = 'vip_applications'
        self.settings = Setting()
        self.resourceName = 'vip_applications'
        self.route('GET', (), self.get_applications)

    @access.public
    @autoDescribeRoute(
         Description("Get the list of applications as a json")
            .errorResponse('ID was invalid')
    )
    def get_applications(self):
        json_file = json.load(open("applications.json", "r"))
        return json_file