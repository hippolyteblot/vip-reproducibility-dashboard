import _ from "underscore";
import { restRequest } from "@girder/core/rest";

// Import views
import View from "@girder/core/views/View";
import "bootstrap/js/button";

// Import templates
import ConvertExperimentTemplate from "../templates/convertExperiment.pug";
import "../stylesheets/userConversionRights.styl";
// Reuse system config style to separate input sections
import "@girder/core/stylesheets/body/systemConfig.styl";
import { getCurrentToken } from "@girder/core/auth";
import "../stylesheets/searchView.styl";
import "../scripts/fill_dropdown.js"

var ConvertExperimentView = View.extend({
  events: {
    "click #action-query": function (event) {
      event.preventDefault();
      this.actionQuery();
    },
  },
  getKeyquery: function () {
    var params = {};
    this.pending = null;
    params["query"] = "";
    restRequest({
      method: "GET",
      url: "conversion/",
      data: params,
    }).then((keyname) => {
      this.containers = keyname;
      this.render();
    });
  },

  initialize: function (settings) {
    this.render();
  },

  initInternal: function () {
    this.render();
  },

  render: function () {
    // Display the list of executions
    this.$el.html(
      ConvertExperimentTemplate({
        query:this.query,
      })
    );

    return this;
  },

  
  actionQuery: function () {
    // Get the values from the form
    var container = document.getElementById("container").value;
    var experiment_id = document.getElementById("experiment_id").value;
    var application = document.getElementById("application").value;
    var version = document.getElementById("version").value;
  
    // Check that all the fields are filled in
    if (!application || !version || !container || !experiment_id) {
      alert("Please fill in all the fields");
      return;
    }
  
    // Build the URL to query the server
    var requestURL = `/api/v1/convert?application=${application}&version=${version}&containerId=${container}&experimentId=${experiment_id}`;
    console.log(getCurrentToken())
    fetch(requestURL, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Girder-Token": getCurrentToken()
      },
    })
      .then((response) => {
        if (response.ok) {
          response.json().then((json) => {
            const message = json.message
            const type = json.type
            if(type == "error"){
              setResultStatus(message, "error")
            }
            else{
              setResultStatus(message, "success")
            }
          }
          );
        }
        else{
          setResultStatus("Error: " + response.statusText, "error")
        }
      }
      )
      .catch((error) => {
        console.error("Error:", error);
      });
    // While the request is being processed, display a message
    setResultStatus("Processing...", "processing")
  },
});

function setResultStatus(message, type) {
  const result = document.getElementById("result");
  result.innerHTML = message;

  result.classList.remove("error");
  result.classList.remove("success");
  result.classList.remove("processing");
  
  result.classList.add(type);
}

export default ConvertExperimentView;
