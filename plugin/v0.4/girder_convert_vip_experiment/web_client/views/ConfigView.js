import _ from "underscore";
import events from "@girder/core/events";
import { restRequest } from "@girder/core/rest";

import PluginConfigBreadcrumbWidget from "@girder/core/views/widgets/PluginConfigBreadcrumbWidget";
import View from "@girder/core/views/View";

import ConfigViewTemplate from "../templates/configView.pug";

var ConfigView = View.extend({
  events: {
    "submit #conversion-plugin-config-form": "onSubmit",
  },

  initialize: function () {
    this.conversionConfig;

    restRequest({
      method: "GET",
      url: "system/setting",
      data: { key: "conversion_plugin.settings" },
    }).done((resp) => {
      this.conversionConfig = resp;
      this.render();
    });
  },

  render: function () {
    this.$el.html(ConfigViewTemplate({
        conversionConfig: this.conversionConfig,
      })
    );

    new PluginConfigBreadcrumbWidget({
      pluginName: "VIP conversion plugin",
      el: this.$(".g-config-breadcrumb-container"),
      parentView: this,
    }).render();

    return this;
  },

  onSubmit: function (e) {
    e.preventDefault();

    if (!this.buildAndValidate()) return;

    // its ok, save on girder server

    restRequest({
      method: "PUT",
      url: "system/setting",
      data: {
        key: "conversion_plugin.settings",
        value: JSON.stringify(this.conversionConfig),
      },
      error: null,
    })
      .done(() => {
        events.trigger("g:alert", {
          icon: "ok",
          text: "Settings saved.",
          type: "success",
          timeout: 4000,
        });
      })
      .fail((resp) => {
        messageGirder("danger", "Girder error : " + resp.responseJSON.message);
      });
  },

  buildAndValidate: function () {
    var data_path = this.$("#conversion-config-data-path").val().trim();
    var girder_id_outputs = this.$("#conversion-config-outputs-id")
      .val()
      .trim();
    var target_name = this.$("#conversion-config-target-name").val().trim();

    this.conversionConfig.data_path = data_path;

    this.conversionConfig.girder_id_outputs = girder_id_outputs;

    this.conversionConfig.target_name = target_name;

    return true;
  },
});

export default ConfigView;
