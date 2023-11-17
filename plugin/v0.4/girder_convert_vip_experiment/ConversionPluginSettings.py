import jsonschema

from girder.exceptions import ValidationException
from girder.utility import setting_utilities


class ConversionPluginSettings(object):
    SETTING_KEY = 'conversion_plugin.settings'


@setting_utilities.default(ConversionPluginSettings.SETTING_KEY)
def _defaultConversionSettings():
    return {
        'data_path': '/home/blot/Documents/girderServer/venv/storage',
        'girder_id_outputs': '645112388de4f6c4656c8eaa',
        'target_name': 'experiment_id'
    }


@setting_utilities.validator(ConversionPluginSettings.SETTING_KEY)
def _validateConversionSettings(doc):
    conversionSettingsSchema = {
        'type': 'object',
        'properties': {
            'data_path': {
                'type': 'string'
            },
            'girder_id_outputs': {
                'type': 'string'
            },
            'target_name': {
                'type': 'string'
            }
        },
        'required': ['data_path', 'girder_id_outputs', 'target_name']
    }
    try:
        jsonschema.validate(doc['value'], conversionSettingsSchema)
    except jsonschema.ValidationError as e:
        raise ValidationException('Invalid conversion plugin settings : ' + str(e))
