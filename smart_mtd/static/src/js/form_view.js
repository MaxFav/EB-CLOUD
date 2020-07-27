odoo.define('smart_mtd.ActionManager', function (require) {
    "use strict";
    
    //var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    function wizard_keep_open(parent, action){
        parent.currentDialogController.widget.update();
        return false;
    }
    core.action_registry.add('wizard_keep_open', wizard_keep_open);


});