function initializeApp() {
  // Fetch the json containing the applications, versions and containers
  fetch("/api/v1/vip_applications")
    .then((response) => response.json())
    .then((data) => {
      // Get the dropdowns
      const applicationSelect = document.getElementById("application");
      const versionSelect = document.getElementById("version");
      const containerSelect = document.getElementById("container");

      function fillVersionDropdown() {
        // Remove current options
        versionSelect.innerHTML = "";
        containerSelect.innerHTML = "";

        const selectedApplication = applicationSelect.value;
        const selectedAppData = data.find(
          (item) => item.application === selectedApplication
        );

        if (selectedAppData) {
          // Fill the version dropdown
          selectedAppData.versions.forEach((versionData) => {
            const option = document.createElement("option");
            option.value = versionData.version;
            option.textContent = versionData.version;
            versionSelect.appendChild(option);
          });
        }
        fillContainerDropdown();
      }

      function fillContainerDropdown() {
        // Remove current options
        containerSelect.innerHTML = "";

        const selectedApplication = applicationSelect.value;
        const selectedVersion = versionSelect.value;
        const selectedAppData = data.find(
          (item) => item.application === selectedApplication
        );

        if (selectedAppData) {
          const selectedVersionData = selectedAppData.versions.find(
            (versionData) => versionData.version === selectedVersion
          );

          if (selectedVersionData) {
            // Fill the container dropdown
            selectedVersionData.containers.forEach((container) => {
              const option = document.createElement("option");
              option.value = container;
              option.textContent = container;
              containerSelect.appendChild(option);
            });
          }
        }
      }

      // Listen for changes in the application dropdown
      applicationSelect.addEventListener("change", fillVersionDropdown);

      // Listen for changes in the version dropdown
      versionSelect.addEventListener("change", fillContainerDropdown);

      // Initial fill of the application dropdown
      data.forEach((appData) => {
        const option = document.createElement("option");
        option.value = appData.application;
        option.textContent = appData.application;
        applicationSelect.appendChild(option);
      });

      // Initial fill of the version dropdown
      fillVersionDropdown();
    });
}

// Setup the MutationObserver to wait for the dropdowns to be available
const observerConfig = { childList: true, subtree: true };

const observer = new MutationObserver(function (mutationsList, observer) {
  const applicationSelect = document.getElementById("application");
  const versionSelect = document.getElementById("version");
  const containerSelect = document.getElementById("container");

  if (applicationSelect && versionSelect && containerSelect) {
    initializeApp();
    observer.disconnect();
  }
});

// Start observing
observer.observe(document, observerConfig);
