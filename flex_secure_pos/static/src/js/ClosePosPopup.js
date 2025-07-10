 odoo.define('flex_secure_pos.ClosePosPopup', function (require) {
 'use strict';

 const ClosePosPopup = require('point_of_sale.ClosePosPopup');
 const Registries = require('point_of_sale.Registries');

 const NewClosePosPopup = (ClosePosPopup) =>
     class extends ClosePosPopup {
         async confirm() {
             this.closeSession();
         }
     };

 Registries.Component.extend(ClosePosPopup, NewClosePosPopup);
 return ClosePosPopup;
 });
