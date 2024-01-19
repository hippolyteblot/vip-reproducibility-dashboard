// Import utilities
import router from '@girder/core/router';
import events from '@girder/core/events';

import { exposePluginConfig } from '@girder/core/utilities/PluginUtils';

exposePluginConfig('conversion', 'plugins/conversion/config');

import ConfigView from './views/ConfigView';
router.route('plugins/conversion/config', 'conversionConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});

import ConvertExperimentView from './views/ConvertExperimentView';
router.route('conversion', function() {
    events.trigger('g:navigateTo', ConvertExperimentView);
})
