// Import utilities
import { wrap } from "@girder/core/utilities/PluginUtils";
import events from "@girder/core/events";
import { getCurrentUser } from "@girder/core/auth";
import router from '@girder/core/router';
// Import views
import UserAccountView from "@girder/core/views/body/UserAccountView.js";
import "@girder/core/stylesheets/widgets/searchFieldWidget.styl";

// Import templates
import UserAccountTab from "../templates/userAccountTab.pug";
import UserAccountConversion from "../templates/userAccountConversion.pug";

// Add an entry to the User Account view
wrap(UserAccountView, "render", function (render) {
  render.call(this);

  if (getCurrentUser() && getCurrentUser().get("admin")) {
    $(this.el).find("ul.g-account-tabs.nav.nav-tabs").append(UserAccountTab);
    $(this.el).find(".tab-content").append(UserAccountConversion({ user: this.user }));
    // Change the route
    $(this.el)
    .find('a[name="conversion"]')
    .on("shown.bs.tab", (e) => {
      var tab = $(e.currentTarget).attr("name");
      router.navigate("useraccount/" + this.model.id + "/" + tab);
    });
  }

  return this;
});

var imported_events = events;

wrap(UserAccountView, "events", function (events) {
  this.events["submit #g-user-conversion-rights-form"] = function (event) {
    event.preventDefault();
    this.$("#g-user-info-error-msg").empty();

    var params = {
      canConvert: this.$("#creatis-convert-vip").is(":checked"),
    };

    this.user.set(params);
    this.user.altUrl = "change_conversion_rights";

    this.user
      .off("g:error")
      .on(
        "g:error",
        function (err) {
          var msg = err.responseJSON.message;
          this.$("#g-" + err.responseJSON.field).trigger("focus");
          this.$("#g-user-info-error-msg").text(msg);
        },
        this
      )
      .off("g:saved")
      .on(
        "g:saved",
        function () {
          imported_events.trigger("g:alert", {
            icon: "ok",
            text: "Info saved.",
            type: "success",
            timeout: 4000,
          });
        },
        this
      )
      .save();
  };
  return this.events;
});
