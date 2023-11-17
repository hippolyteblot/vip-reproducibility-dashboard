# -----------------------------------------------------------------------------
# Description : entry point of the plugin
# Author      : Hippolyte Blot. <hippolyte.blot@creatis.insa-lyon.fr>
# -----------------------------------------------------------------------------

from girder.plugin import GirderPlugin

# Local imports
from .ConversionHandler import ConversionHandler
from .VipApplicationsHandler import VipApplicationsHandler
from .UserConvertHandler import UserConvertHandler
from .ConversionSettingsHandler import ConversionSettingsHandler


class ConvertVIPExperiment(GirderPlugin):
    DISPLAY_NAME = 'Convert VIP experiment'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        info['apiRoot'].convert = ConversionHandler()
        info['apiRoot'].vip_applications = VipApplicationsHandler()
        info['apiRoot'].change_conversion_rights = UserConvertHandler()
        info['apiRoot'].system.route('GET', ('setting', 'conversion_plugin'),
                                     ConversionSettingsHandler.getConversionPluginConf)

        baseTemplateFilename = info['apiRoot'].templateFilename
        info['apiRoot'].updateHtmlVars({
            'baseTemplateFilename': baseTemplateFilename
        })
