window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        search_exp: function(value, children) {
            // Check if inputs are valid
            if(children.props === undefined) return [];
            if(value === undefined || value === null || value === '') {
                return children.props.children[0].props.children;
            }
            // Clone the children
            let clone = children.props.children[0].props.children.slice(0);
            for(let i = 0; i < clone.length; i++) {
                // Check if the value is in the text
                if(clone[i].props.children[0].props.children.toLowerCase().indexOf(value.toLowerCase()) === -1) {
                    // If not, remove the element
                    clone.splice(i, 1);
                    i--;
                }
            }
            return clone;
        },
        serach_wf: function(value, children) {
            // Check if inputs are valid
            if(children.props === undefined) return [];
            if(value === undefined || value === null || value === '') {
                return children.props.children[0].props.children;
            }
            // Clone the children
            let clone = children.props.children[0].props.children.slice(0);
            for(let i = 0; i < clone.length; i++) {
                // Check if the value is in the text
                if(clone[i].props.children[0].props.children.toLowerCase().indexOf(value.toLowerCase()) === -1) {
                    // If not, remove the element
                    clone.splice(i, 1);
                    i--;
                }
            }
            return clone;
        }
    }
});