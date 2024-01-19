// Import utilities
import _ from 'underscore';
import { getCurrentUser } from '@girder/core/auth';
import { restRequest, cancelRestRequests } from '@girder/core/rest';
import events from '@girder/core/events';
import FolderModel from '@girder/core/models/FolderModel';
import ApiKeyCollection from '@girder/core/collections/ApiKeyCollection.js'
import ApiKeyModel from '@girder/core/models/ApiKeyModel.js'
import FolderCollection from '@girder/core/collections/FolderCollection';


var conversionConfig = null;

function getConversionConfig() {
  if (conversionConfig) return Promise.resolve(conversionConfig);

  return restRequest({
    method: 'GET',
    url: '/system/setting/conversion_plugin'
  })
  .then(resp => {
    conversionConfig = resp;
    return conversionConfig;
  });
}

function useConversionConfig(promise, f) {
    return Promise.all([
      getConversionConfig(),
      promise,
    ])
    .then( res => f.apply(this, res) );
}