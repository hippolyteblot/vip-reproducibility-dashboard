console.log("Script loaded: girder_navigation.js")

document.addEventListener("DOMSubtreeModified", function(event) {
    // Try to get radio btn with the class form-check-input
    var radio_items = document.getElementsByClassName("form-check-label");
    var old_item = null;
    for (var i = 0; i < radio_items.length; i++) {
        radio_items[i].addEventListener("click", function(event) {
            if (old_item != null) {
                old_item.style.backgroundColor = "white";
            }
            event.target.style.backgroundColor = "#91cfff";
            old_item = event.target;
        });
    }
}, false);