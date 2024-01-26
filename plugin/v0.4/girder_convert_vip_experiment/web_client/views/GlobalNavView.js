import { wrap } from "@girder/core/utilities/PluginUtils";

import LayoutGlobalNavView from "@girder/core/views/layout/GlobalNavView.js";
import LayoutGlobalNavTemplate from "@girder/core/templates/layout/layoutGlobalNav.pug";
import "@girder/core/stylesheets/layout/globalNav.styl";
import { getCurrentUser } from "@girder/core/auth";

wrap(LayoutGlobalNavView, "render", function (render) {
  var navItems;
  if (this.navItems) {
    navItems = this.navItems;
  } else {
    navItems = this.defaultNavItems;
    if (getCurrentUser()) {
      // copy navItems so that this.defaultNavItems is unchanged
      navItems = navItems.slice();
      navItems.push({
        name: "Users",
        icon: "icon-user",
        target: "users",
      });
      if (getCurrentUser().get("admin")) {
        navItems.push({
          name: "Admin console",
          icon: "icon-wrench",
          target: "admin",
        });
      }
      if (getCurrentUser().get("canConvert") && getCurrentUser().get("canConvert") == true) {
        navItems.push({
          name: "Conversion",
          icon: "icon-cog",
          target: "conversion",
        });
    }
    }
  }
  this.$el.html(
    LayoutGlobalNavTemplate({
      navItems: navItems,
    })
  );

  if (Backbone.history.fragment) {
    this.$('[g-target="' + Backbone.history.fragment + '"]')
      .parent()
      .addClass("g-active");
  }

  return this;
});
