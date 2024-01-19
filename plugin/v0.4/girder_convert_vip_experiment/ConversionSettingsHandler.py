import girder.models.setting as Setting
from girder.api import access
from girder.api.rest import Resource
from girder.api.describe import Description, autoDescribeRoute

from .ConversionPluginSettings import ConversionPluginSettings


class ConversionSettingsHandler(Resource):
    @access.user
    @autoDescribeRoute(
        Description('Get the plugin api conf')
    )
    def getConversionPluginConf(self):
        return Setting().get(ConversionPluginSettings.SETTING_KEY)