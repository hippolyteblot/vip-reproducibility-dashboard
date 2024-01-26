import json
from girder.api import access
from girder.api.rest import Resource, filtermodel
from girder.api.describe import Description, autoDescribeRoute
from girder.models.setting import Setting
from girder.models.user import User
from girder.constants import AccessType
from girder.exceptions import AccessException, RestException


class UserConvertHandler(Resource):
    DEFAULT_USER = 'ANONYMOUS'

    def __init__(self):
        super(UserConvertHandler, self).__init__()
        self.resourceName = 'user_with_convert'
        self.settings = Setting()
        self.resourceName = 'user_with_convert'
        User().exposeFields(level=AccessType.READ, fields={'canConvert'})
        self._model = User()
        self.route('PUT', (':id',), self.updateUser)
    
    @access.user
    @filtermodel(model=User)
    @autoDescribeRoute(
        Description("Update a user's information.")
        .modelParam('id', model=User, level=AccessType.WRITE)
        .param('canConvert', 'Can the user convert an experiment (admin access required)',
                required=False, dataType='boolean')
        .errorResponse()
        .errorResponse(('You do not have write access for this user.',
                        'Must be an admin to create an admin.'), 403)
    )
    def updateUser(self, user, canConvert):
        # Only admins can change canConvert state
        if not self.getCurrentUser()['admin']:
            raise AccessException('Only admins may change canConvert status.')
        if canConvert not in (True, False):
            raise RestException('canConvert must be a boolean.')

        user['canConvert'] = canConvert

        return self._model.save(user)